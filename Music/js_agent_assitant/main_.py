import os
import redis
import re
import logging
import requests
import numpy as np
import networkx as nx
from bs4 import BeautifulSoup
from flask import jsonify, Flask, render_template, request, session
from flask_session import Session
from datetime import datetime, timedelta
from markdown import markdown
import google.generativeai as genai
from google.api_core import retry
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings
from chromadb import Documents, EmbeddingFunction, Embeddings

#########################################
# Configuration and Setup
#########################################

API_KEY = os.environ.get("GOOGLE_GENAI_API_KEY", "AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k")
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
CACHE_TTL = 300  # seconds to cache scraped content

genai.configure(api_key=API_KEY)
print("Google Generative AI API configured successfully.")

try:
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_client.ping()
    print("Successfully connected to Redis.")
except redis.ConnectionError as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None

app = Flask(__name__, static_folder='static')
app.jinja_env.globals.update(now=datetime.now)
app.secret_key = FLASK_SECRET_KEY
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
if redis_client:
    app.config['SESSION_REDIS'] = redis_client
    Session(app)

LOG_FILE_PATH = 'log.txt'
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, format='%(message)s')

#########################################
# Helper Functions
#########################################

def get_user_ip():
    forwarded_for = request.headers.get('X-Forwarded-For', None)
    return forwarded_for.split(',')[0].strip() if forwarded_for else request.remote_addr

def log_api_hit(endpoint, request_type, request_data, response_data, status_code, message, request_ip):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    import json
    log_data = {
        "timestamp": timestamp,
        "url": endpoint,
        "request_type": request_type,
        "user_query": request_data,
        "response": response_data,
        "status_code": status_code,
        "message": message,
        "ip": request_ip
    }
    logging.info(json.dumps(log_data, ensure_ascii=False))

# Rate limiter: Limit each IP to 20 POST requests per minute.
RATE_LIMIT = 20
@app.before_request
def rate_limiter():
    if request.method != "POST":
        return
    ip = get_user_ip()
    try:
        if redis_client:
            key = f"rate_limit:{ip}"
            current_value = redis_client.get(key)
            if current_value is not None:
                current_value = int(current_value)
                if current_value >= RATE_LIMIT:
                    print(f"[DEBUG] Rate limit exceeded for IP {ip}.")
                    return jsonify({"error": f"Too many requests from IP {ip}. Please try again after a minute."}), 429
                else:
                    new_count = redis_client.incr(key)
                    if new_count == 1:
                        redis_client.expire(key, 60)
                    print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
            else:
                new_count = redis_client.incr(key)
                redis_client.expire(key, 60)
                print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
    except Exception as e:
        print(f"[DEBUG] Error in rate limiter for IP {ip}: {e}")
        logging.exception(e)

#########################################
# Custom Embedding Function for ChromaDB & GraphRAG
#########################################
class GeminiEmbeddingFunction(EmbeddingFunction):
    document_mode = True  # True for documents; False for queries

    def __call__(self, input: Documents) -> Embeddings:
        task = "retrieval_document" if self.document_mode else "retrieval_query"
        retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
        print(f"Embedding task set to: {task}")
        response = genai.embed_content(
            model="models/text-embedding-004",
            content=input,
            task_type=task,
            request_options=retry_policy,
        )
        return response["embedding"]

#########################################
# Setup Persistent ChromaDB Collection
#########################################
DB_NAME = "googlecardb"
embed_fn = GeminiEmbeddingFunction()
embed_fn.document_mode = True
chroma_client = chromadb.Client(Settings(persist_directory="db"))
db = chromadb.Client(Settings(persist_directory="db")).get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

#########################################
# GraphRAG Component: Build a Knowledge Graph
#########################################

# Global document graph (nodes: document chunks, attributes: text and embedding)
document_graph = nx.Graph()

def cosine_similarity(vec1, vec2):
    # Flatten the vectors to ensure they are 1D arrays.
    vec1 = np.array(vec1).flatten()
    vec2 = np.array(vec2).flatten()
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def add_chunk_to_graph(chunk_text, pdf_path, index):
    # Compute embedding for the single chunk (wrap text in a list)
    embed_fn.document_mode = True
    embedding = embed_fn([chunk_text])
    node_id = f"{pdf_path}_{index}"
    document_graph.add_node(node_id, text=chunk_text, embedding=embedding)
    # Optionally, add edges to similar nodes already in the graph.
    for other_node, data in document_graph.nodes(data=True):
        if other_node == node_id:
            continue
        sim = cosine_similarity(embedding, data.get('embedding', []))
        # Add an edge if similarity exceeds a threshold (e.g., 0.8)
        if sim > 0.8:
            document_graph.add_edge(node_id, other_node, weight=sim)

#########################################
# PDF Indexing Support & GraphRAG Update
#########################################
INDEXED_PDFS_FILE = "indexed_pdfs.txt"

def load_and_index_pdf(pdf_path):
    print(f"Loading PDF file: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    raw_file = loader.load()
    print("PDF loaded and text extracted.")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3200, chunk_overlap=1300)
    documents = text_splitter.split_documents(raw_file)
    print("First 3 document chunks:")
    for i, doc in enumerate(documents[:3]):
        print(f"Chunk {i}: {doc.page_content[:200]}")
    document_contents = [doc.page_content for doc in documents]
    # Add to ChromaDB
    db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
    # Update graph with each document chunk
    for i, chunk in enumerate(document_contents):
        add_chunk_to_graph(chunk, pdf_path, i)
    # (Skipping logic for already-indexed PDFs)

def load_and_index_pdfs(pdf_paths):
    for pdf_path in pdf_paths:
        load_and_index_pdf(pdf_path)

#########################################
# Helper Function: Flatten Nested Lists
#########################################
def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        elif item and item.strip():
            flat_list.append(item)
    print(f"Flattened list contains {len(flat_list)} items.")
    return flat_list


#########################################
# Index PDF Documents at App Startup
#########################################
pdf_files = [
    '20 links Knowledge base.pdf',
    'First Page URLs.pdf',
    'Second Page URLs.pdf',
    'Third Page URLs.pdf',
    'PPG  - Home Finance - Clean Copy.pdf',
    'PPG - Auto Financing - Clean Copy (1).pdf',
    'Credit Cards PPG.pdf',
    'Gold Finance PPG.pdf',
    'PPG - Renewable Energy - March 2024- V1.1.pdf',
    'JSBL-SOC-Jan-Jun-2025-English.pdf'
]

print("Starting PDF loading and indexing process for multiple PDFs.")
load_and_index_pdfs(pdf_files)
print("PDF loading and indexing complete.")

#########################################
# Fallback Topics and Topic Extraction
#########################################

CURRENT_TOPICS = "JS Bank Services and Digital Transformation initiatives."

def extract_topic(query):
    match = re.search(r'(?:what\s+is|explain)\s+([^\?\.]+)', query, re.IGNORECASE)
    if match:
        topic = match.group(1).strip()
        return re.sub(r'[\?\.,!]+$', '', topic)
    return None

def get_dynamic_features(topic):
    query_text = f"{topic} features"
    embed_fn.document_mode = False
    result = db.query(query_texts=[query_text], n_results=3)
    features_passages = flatten_list(result['documents'])
    return "\n".join(features_passages) if features_passages else "No additional information available."

#########################################
# Sentiment Analysis and Clarification
#########################################
def analyze_sentiment(query):
    negative_words = ['shit', 'sucks', 'terrible', 'bad', 'horrible']
    return "negative" if any(word in query.lower() for word in negative_words) else "neutral"

def get_clarification_prompt(query):
    return "It seems you are dissatisfied. Could you please provide more details about the issue?\n\n" if analyze_sentiment(query) == "negative" else ""

#########################################
# GraphRAG: Retrieve Graph Context for a Query
#########################################
def get_graph_context(query, top_k=3):
    """Compute the query embedding and return text from top-k similar graph nodes."""
    embed_fn.document_mode = False  # Query mode
    query_embedding = embed_fn([query])
    similarities = []
    for node, data in document_graph.nodes(data=True):
        node_embedding = data.get('embedding', [])
        sim = cosine_similarity(query_embedding, node_embedding)
        similarities.append((node, sim))
    # Sort nodes by similarity descending and take top_k
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    context_texts = []
    for node, sim in similarities:
        text = document_graph.nodes[node].get('text', '')
        context_texts.append(text)
    return "\n".join(context_texts) if context_texts else "No graph context available."

#########################################
# Dynamic Multi-Source Retrieval with Caching
#########################################
def scrape_website(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            main_content = soup.find('main') or soup.body
            return main_content.get_text(separator="\n", strip=True) if main_content else ""
        return f"Failed to retrieve content, status code {response.status_code}."
    except Exception as e:
        return f"Error during scraping: {str(e)}"

def get_cached_scrape(url, cache_key):
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            print(f"[DEBUG] Returning cached content for {url}")
            return cached.decode("utf-8")
    content = scrape_website(url)
    if redis_client:
        redis_client.setex(cache_key, timedelta(seconds=CACHE_TTL), content)
    return content

def get_dynamic_web_results(query):
    url = "https://www.jsbl.com/about-us/board-of-directors/"
    cache_key = "scrape:board_of_directors"
    scraped_content = get_cached_scrape(url, cache_key)
    return f"Live Web Data from JSBL Board of Directors Page:\n{scraped_content}"

#########################################
# Flask Route for Handling User Queries
#########################################
@app.route("/", methods=["GET", "POST"])
def index():
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    if request.method == "POST":
        query = request.form.get("query")
        print(f"Received user query: {query}")
        if query:
            explicit_topic = extract_topic(query)
            if explicit_topic:
                session['last_topic'] = explicit_topic
                print(f"Explicit topic detected: {explicit_topic}")
            conversation_context = "\n".join([f"Q: {q}\nA: {a}" for q, a in session['conversation_history']])
            context_info = ""
            if session.get('last_topic'):
                topic = session.get('last_topic')
                dynamic_features = get_dynamic_features(topic)
                context_info = f"Topic: {topic}\nFeatures:\n{dynamic_features}\n\n"
            embed_fn.document_mode = False
            result = db.query(query_texts=[query], n_results=3)
            print("Raw query result:", result)
            if result['documents']:
                relevant_passages = flatten_list(result['documents'])
                document_context = "\n".join(relevant_passages)
            else:
                document_context = "No relevant static document context found."
            dynamic_web_context = get_dynamic_web_results(query)
            graph_context = get_graph_context(query)
            clarification_prompt = get_clarification_prompt(query)
            prompt = (
                "You are a JS bank customer query representative. Your knowledge is based on pre-indexed documents, a knowledge graph (GraphRAG), and real-time web data. "
                "Customers ask about various JS bank services. When a customer uses negative language, ask for further clarification rather than only listing features. "
                "Answer naturally and interactively.\n\n"
                f"{clarification_prompt}"
                f"{context_info}"
                f"{conversation_context}\n"
                "Document Context:\n" + document_context + "\n\n" +
                "Graph Context:\n" + graph_context + "\n\n" +
                "Dynamic Web Context:\n" + dynamic_web_context + "\n\n" +
                f"Q: {query}"
            )
            print("Generating answer using Generative AI model...")
            model = genai.GenerativeModel("gemini-2.0-flash")
            try:
                answer = model.generate_content(prompt)
            except Exception as e:
                print("Error during generation:", e)
                answer = type("obj", (object,), {"text": "An error occurred while generating the answer."})
            formatted_response = markdown(answer.text)
            print("Answer generated successfully.")
            log_api_hit(
                endpoint=request.url,
                request_type=request.method,
                request_data=query,
                response_data=formatted_response,
                status_code=200,
                message="Answer generated successfully.",
                request_ip=get_user_ip()
            )
            session['conversation_history'].append((query, formatted_response))
            session.modified = True
            return render_template("index.html", answer=formatted_response, query=query, conversation_history=session['conversation_history'])
        else:
            print("User submitted an empty query.")
            return render_template("index.html", warning="Please enter a question to get an answer.")
    return render_template("index.html", conversation_history=session['conversation_history'])

#########################################
# Run the Flask Application
#########################################
if __name__ == "__main__":
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    print("Starting Flask app...")
    app.run(host="0.0.0.0", port=5006)
