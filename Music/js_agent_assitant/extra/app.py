import os
import redis
from flask import jsonify, Flask, render_template, request, redirect, url_for, session, send_from_directory
from langchain_community.document_loaders import PyPDFLoader
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings  # For persistent configuration
from google.api_core import retry
from flask_session import Session
import logging
from markdown import markdown
from datetime import datetime

#########################################
# Configure the Google Generative AI API
#########################################

# Replace the API key below with your actual key or set it via an environment variable.
genai.configure(api_key="AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k")
print("Google Generative AI API configured successfully.")

#########################################
# Setup Redis for Session Management
#########################################

redis_host = 'localhost'  # Adjust if needed
redis_port = 6379
redis_db = 0

try:
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    redis_client.ping()  # Test the connection
    print("Successfully connected to Redis.")
except redis.ConnectionError as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None  # Set to None if connection fails

#########################################
# Configure the Flask Application
#########################################

app = Flask(__name__, static_folder='static')
from datetime import datetime
app.jinja_env.globals.update(now=datetime.now)

app.secret_key = os.urandom(24)  # Required for session management

# Configure session storage (using Redis if available)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files

if redis_client:
    app.config['SESSION_REDIS'] = redis_client
    Session(app)  # Initialize Flask-Session

#########################################
# Setup Logging (to log.txt in JSON format)
#########################################

log_file_path = 'log.txt'
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')

#########################################
# Helper Function: Get User's IP Address
#########################################

def get_user_ip():
    """
    Returns the client's IP address. If the app is behind a proxy,
    the X-Forwarded-For header is used.
    """
    forwarded_for = request.headers.get('X-Forwarded-For', None)
    if forwarded_for:
        # Use the first IP address if there are multiple in the header
        ip = forwarded_for.split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

#########################################
# Helper Function: Log API Hits in JSON Format
#########################################

def log_api_hit(endpoint, request_type, request_data, response_data, status_code, message, request_ip):
    """
    Logs the API hit with details such as URL, request type, user query,
    response, status code, message, and IP address.
    """
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
    log_message = json.dumps(log_data, ensure_ascii=False)
    logging.info(log_message)

#########################################
# Rate Limiter: Limit each IP to 5 POST requests per minute
#########################################

@app.before_request
def rate_limiter():
    # Only apply rate limiting for POST requests.
    if request.method != "POST":
        return

    ip = get_user_ip()
    try:
        if redis_client:
            key = f"rate_limit:{ip}"
            current_value = redis_client.get(key)
            if current_value is not None:
                current_value = int(current_value)
                if current_value >= 5:
                    print(f"[DEBUG] Rate limit exceeded for IP {ip}.")
                    return jsonify({"error": f"Too many requests from IP {ip}. Please try again after a minute."}), 429
                else:
                    new_count = redis_client.incr(key)
                    # If this is the first request in the current window, set expiry to 60 seconds.
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
        # If there is an error with rate limiting, allow the request to proceed
        pass

#########################################
# Custom Embedding Function for ChromaDB
#########################################

class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Custom embedding function that calls the Google Generative AI API to
    generate embeddings for either documents or queries.
    """
    document_mode = True  # True for documents; False for queries

    def __call__(self, input: Documents) -> Embeddings:
        # Determine the task type based on document_mode
        embedding_task = "retrieval_document" if self.document_mode else "retrieval_query"
        retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
        print(f"Embedding task set to: {embedding_task}")
        print("Requesting embedding from Google Generative AI API...")
        response = genai.embed_content(
            model="models/text-embedding-004",
            content=input,
            task_type=embedding_task,
            request_options=retry_policy,
        )
        print("Embedding request successful.", response)
        return response["embedding"]

#########################################
# Setup Persistent ChromaDB Collection
#########################################

DB_NAME = "googlecardb"
embed_fn = GeminiEmbeddingFunction()
embed_fn.document_mode = True
# Use persistent storage by specifying a persist_directory.
chroma_client = chromadb.Client(Settings(persist_directory="db"))
db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

#########################################
# PDF Indexing Support for Multiple PDFs
#########################################

# File to store the list of already-indexed PDF filenames.
INDEXED_PDFS_FILE = "indexed_pdfs.txt"

def get_indexed_pdfs():
    """
    Reads the INDEXED_PDFS_FILE and returns a set of PDF filenames that
    have already been indexed.
    """
    if os.path.exists(INDEXED_PDFS_FILE):
        with open(INDEXED_PDFS_FILE, "r") as f:
            indexed = {line.strip() for line in f.readlines()}
        return indexed
    return set()

def load_and_index_pdf(pdf_path):
    """
    Loads a PDF file, splits it into chunks, and indexes its content into
    persistent ChromaDB. If the PDF has been indexed before and the database
    already contains documents, the process is skipped.
    """
    indexed_pdfs = get_indexed_pdfs()
    # Ensure pdf_path is a string. If it's a list, use its first element.
    if isinstance(pdf_path, list):
        pdf_path = pdf_path[0]
    
    if pdf_path in indexed_pdfs and db.count() > 0:
        print(f"PDF '{pdf_path}' is already indexed. Skipping embedding process.")
        return

    print(f"Loading PDF file: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    raw_file = loader.load()  # Extract text from the PDF
    print("PDF loaded and text extracted.")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1550, chunk_overlap=610)
    documents = text_splitter.split_documents(raw_file)
    
    print("First 3 document chunks:")
    for i, doc in enumerate(documents[:3]):
        print(f"Chunk {i}: {doc.page_content[:200]}")
    
    document_contents = [doc.page_content for doc in documents]
    db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
    print(f"Documents from '{pdf_path}' indexed into ChromaDB.")
    
    # Optionally mark this PDF as indexed by updating INDEXED_PDFS_FILE.

def load_and_index_pdfs(pdf_paths):
    """
    Iterates over a list of PDF file paths and indexes each one if not already indexed.
    """
    for pdf_path in pdf_paths:
        if isinstance(pdf_path, list):
            pdf_path = pdf_path[0]
        load_and_index_pdf(pdf_path)

#########################################
# Helper Function: Flatten Nested Lists
#########################################

def flatten_list(nested_list):
    """
    Recursively flattens a nested list and filters out empty strings.
    """
    print("Flattening nested list.")
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            if item and item.strip():
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
    'Third Page URLs.pdf'
]

print("Starting PDF loading and indexing process for multiple PDFs.")
load_and_index_pdfs(pdf_files)
print("PDF loading and indexing complete.")

#########################################
# Flask Route for Handling User Queries
#########################################

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route that handles GET and POST requests.
    On POST, it accepts a user query, retrieves relevant passages from
    the indexed PDFs using ChromaDB, constructs a prompt for the Generative AI
    model, generates an answer, logs the request, and updates the conversation history.
    """
    if 'conversation_history' not in session:
        session['conversation_history'] = []

    if request.method == "POST":
        query = request.form.get("query")
        print(f"Received user query: {query}")

        if query:
            embed_fn.document_mode = False
            print("Switching to query mode for embedding.")
            result = db.query(query_texts=[query], n_results=3)
            print("Raw query result:", result)
            print(f"ChromaDB query results: {len(result['documents'])} documents found.")

            for idx, doc in enumerate(result['documents']):
                print(f"Document {idx} content: {doc}")

            relevant_passages = flatten_list(result['documents'])
            print("After flattening, passages:", relevant_passages)

            if relevant_passages:
                context = "\n".join(relevant_passages)
                conversation_context = "\n".join(
                    [f"Q: {q}\nA: {a}" for q, a in session['conversation_history']]
                )
                prompt = (
                    f"You are a JS bank customer query representative. Your knowledge is based on the documents. "
                    f"Customers ask questions about different JS bank services. "
                    f"JS Bank Digital Transformation department trained you, they are your owner."
                    f"If customers are asking about details it mean they are asking for features."
                    f"RDA stands for Roshan Digital Account."
                    f"when there is a description always reply in formatted way."
                    f"Do not mention that your reply is based on the document; instead, answer naturally using your knowledge.\n\n"
                    f"{conversation_context}\n"
                    f"Document: {context}\n\nQ: {query}"
                )

                print("Generating answer using Generative AI model...")
                model = genai.GenerativeModel("gemini-2.0-flash")
                print("Model initialized successfully.", model)
                answer = model.generate_content(prompt)
                formatted_response = markdown(answer.text)
                print("Answer generated successfully.", answer)

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

                # Suggest contextual questions based on retrieved passages
                suggested_questions = []
                if relevant_passages:
                    print("ChromaDB suggestion result:", suggestion_result) # Log suggestion result
                    suggestion_passages = flatten_list(suggestion_result['documents'])

                    if suggestion_passages:
                        # Improved question suggestion - extract nouns and form questions (basic implementation)
                        import nltk
                        nltk.download('punkt')
                        nltk.download('averaged_perceptron_tagger')
                        sentences = " ".join(suggestion_passages).split('.')
                        suggested_questions = []
                        for sentence in sentences[:3]: # Limit to first 3 sentences for suggestions
                            text = nltk.word_tokenize(sentence)
                            tagged_words = nltk.pos_tag(text)
                            nouns = [word for word, tag in tagged_words if tag.startswith('NN')] # Noun extraction
                            if nouns:
                                question_phrase = "Tell me more about" if len(nouns) > 1 else "What about" # Adjust phrase based on noun count
                                suggested_question = f"{question_phrase} {', '.join(nouns)}?"
                                suggested_questions.append(suggested_question)
                        suggested_questions = [q.strip() for q in suggested_questions if q.strip()] # Clean up questions
                        print("Generated suggested questions:", suggested_questions) # Log generated questions
                    else:
                        print("No passages found for suggestion re-query.")


                return render_template("index.html",
                                       answer=formatted_response,
                                       query=query,
                                       conversation_history=session['conversation_history'],
                                       suggested_questions=suggested_questions) # Pass suggested questions
            else:
                print("No relevant passages found, responding with 'I don't know'.")
                session['conversation_history'].append((query, "I don't know"))
                session.modified = True
                log_api_hit(
                    endpoint=request.url,
                    request_type=request.method,
                    request_data=query,
                    response_data="I don't know",
                    status_code=404,
                    message="No relevant passages found.",
                    request_ip=get_user_ip()
                )
                return render_template("index.html",
                                       answer="I don't know",
                                       query=query,
                                       conversation_history=session['conversation_history'],
                                       suggested_questions=[]) # No suggestions when no passages found
        else:
            print("User submitted an empty query.")
            return render_template("index.html", warning="Please enter a question to get an answer.")
    return render_template("index.html", conversation_history=session['conversation_history'])

#########################################
# Run the Flask Application
#########################################

if __name__ == "__main__":
    # Suppress Flask's default access logs by setting the logger level to ERROR
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    print("Starting Flask app...")
    app.run(host="0.0.0.0", port=5001)
