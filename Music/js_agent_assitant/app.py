import os
import redis
import re
from flask import jsonify, Flask, render_template, request, session
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
# It is highly recommended to use environment variables for sensitive API keys.
API_KEY = 'AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k'
genai.configure(api_key=API_KEY)
print("Google Generative AI API configured successfully.")

#########################################
# Setup Redis for Session Management & Rate Limiting
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
app.jinja_env.globals.update(now=datetime.now)
# Use a fixed secret key in production (ideally via an environment variable)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

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
    forwarded_for = request.headers.get('X-Forwarded-For', None)
    if forwarded_for:
        ip = forwarded_for.split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

#########################################
# Helper Function: Log API Hits in JSON Format
#########################################
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
    log_message = json.dumps(log_data, ensure_ascii=False)
    logging.info(log_message)

#########################################
# Rate Limiter: Limit each IP to 5 POST requests per minute
#########################################
@app.before_request
def rate_limiter():
    if request.method != "POST":
        return
    ip = get_user_ip()
    print("ip my", ip)
    try:
        if redis_client:
            key = f"rate_limit:{ip}"
            current_value = redis_client.get(key)
            if current_value is not None:
                current_value = int(current_value)
                if current_value >= 20:
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
        pass

#########################################
# Custom Embedding Function for ChromaDB
#########################################
class GeminiEmbeddingFunction(EmbeddingFunction):
    document_mode = True  # True for documents; False for queries

    def __call__(self, input: Documents) -> Embeddings:
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
        return response["embedding"]

#########################################
# Setup Persistent ChromaDB Collection
#########################################
DB_NAME = "googlecardb"
embed_fn = GeminiEmbeddingFunction()
embed_fn.document_mode = True
chroma_client = chromadb.Client(Settings(persist_directory="db"))
db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

#########################################
# PDF Indexing Support for Multiple PDFs
#########################################
INDEXED_PDFS_FILE = "indexed_pdfs.txt"

def get_indexed_pdfs():
    if os.path.exists(INDEXED_PDFS_FILE):
        with open(INDEXED_PDFS_FILE, "r") as f:
            indexed = {line.strip() for line in f.readlines()}
        return indexed
    return set()

def update_indexed_pdfs(pdf_path):
    with open(INDEXED_PDFS_FILE, "a") as f:
        f.write(f"{pdf_path}\n")

def load_and_index_pdf(pdf_path):
    indexed_pdfs = get_indexed_pdfs()
    if pdf_path in indexed_pdfs and db.count() > 0:
        print(f"PDF '{pdf_path}' is already indexed. Skipping embedding process.")
        return
    print(f"Loading PDF file: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    raw_file = loader.load()  # Extract text from the PDF
    print("PDF loaded and text extracted.")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3200, chunk_overlap=1300)
    documents = text_splitter.split_documents(raw_file)
    print("First 3 document chunks:")
    for i, doc in enumerate(documents[:3]):
        print(f"Chunk {i}: {doc.page_content[:200]}")
    document_contents = [doc.page_content for doc in documents]
    db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
    # update_indexed_pdfs(pdf_path)

def load_and_index_pdfs(pdf_paths):
    for pdf_path in pdf_paths:
        # Assume pdf_paths is a list of file paths (strings)
        load_and_index_pdf(pdf_path)

#########################################
# Helper Function: Flatten Nested Lists
#########################################
def flatten_list(nested_list):
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

# Define fallback current topics for general queries.
CURRENT_TOPICS = "JS Bank Services and Digital Transformation initiatives."

#########################################
# Improved Topic Extraction Function
#########################################
def extract_topic(query):
    """
    Attempts to extract a topic from the query. This version uses a more flexible
    regex to capture multi-word topics when the query starts with phrases like
    'what is' or 'explain'.
    """
    match = re.search(r'(?:what\s+is|explain)\s+([^\?\.]+)', query, re.IGNORECASE)
    if match:
        topic = match.group(1).strip()
        # Remove trailing punctuation
        topic = re.sub(r'[\?\.,!]+$', '', topic)
        return topic
    return None

#########################################
# Helper Function: Dynamically Retrieve Features for a Topic
#########################################
def get_dynamic_features(topic):
    """
    Dynamically retrieves feature information for a given topic from the indexed documents.
    """
    query_text = f"{topic} features"
    embed_fn.document_mode = False  # Switch to query mode for embedding.
    result = db.query(query_texts=[query_text], n_results=3)
    features_passages = flatten_list(result['documents'])
    if features_passages:
        return "\n".join(features_passages)
    else:
        return "No additional information available."

#########################################
# Flask Route for Handling User Queries
#########################################
@app.route("/", methods=["GET", "POST"])
def index():
    """
    Handles GET and POST requests. For POST requests, it retrieves relevant passages
    from the indexed PDFs, builds a prompt, and calls the Generative AI model.
    The chatbot dynamically uses the stored topic context if available.
    """
    if 'conversation_history' not in session:
        session['conversation_history'] = []

    if request.method == "POST":
        query = request.form.get("query")
        print(f"Received user query: {query}")

        if query:
            # Try to extract a topic from the query
            explicit_topic = extract_topic(query)
            if explicit_topic:
                session['last_topic'] = explicit_topic
                print(f"Explicit topic detected and stored: {explicit_topic}")

            # Build the conversation context from history
            conversation_context = "\n".join(
                [f"Q: {q}\nA: {a}" for q, a in session['conversation_history']]
            )

            # Prepare dynamic context based on stored topic if available
            context_info = ""
            if session.get('last_topic'):
                topic = session.get('last_topic')
                dynamic_features = get_dynamic_features(topic)
                context_info = f"Topic: {topic}\nFeatures:\n{dynamic_features}\n\n"

            # Retrieve relevant documents from ChromaDB using the query
            embed_fn.document_mode = False  # Ensure we're in query mode
            result = db.query(query_texts=[query], n_results=3)
            print("Raw query result:", result)
            print(f"ChromaDB query results: {len(result['documents'])} documents found.")

            if result['documents']:
                relevant_passages = flatten_list(result['documents'])
                document_context = "\n".join(relevant_passages)
                prompt = (
                    "You are a JS bank customer query representative. Your knowledge is based on the documents. "
                    "Customers ask questions about different JS bank services. "
                    "JS Bank Digital Transformation department trained you, they are your owner. "
                    "When there is a description, always reply in a formatted way. "
                    "When a customer expresses dissatisfaction with JS Bank services—using terms like 'shit', 'sucks', or similar negative language—do not simply provide feature details about the topic. Instead, respond by asking for more specific information about the problem they are facing also keep continue the topic til use satisfy from you resposne keep continue that topic and similar negative"
                    "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
                    f"{context_info}"
                    f"{conversation_context}\n"
                    f"Document Context:\n{document_context}\n\n"
                    f"Q: {query}"
                )
            else:
                print("No relevant passages found, using fallback current topics.")
                prompt = (
                    "You are a JS bank customer query representative. Your knowledge is based on the documents. "
                    "Customers ask questions about different JS bank services. "
                    "JS Bank Digital Transformation department trained you, they are your owner. "
                    "When there is a description, always reply in a formatted way. "
                    "When a customer expresses dissatisfaction with JS Bank services—using terms like 'shit', 'sucks', or similar negative language—do not simply provide feature details about the topic. Instead, respond by asking for more specific information about the problem they are facing also keep continue the topic til use satisfy from you resposne keep continue that topic and similar negative"
                    "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
                    f"{context_info}"
                    f"{conversation_context}\n"
                    f"Current Topics: {CURRENT_TOPICS}\n\n"
                    f"Q: {query}"
                )

            print("Generating answer using Generative AI model...")
            model = genai.GenerativeModel("gemini-2.0-flash")
            print("Model initialized successfully.", model)
            try:
                answer = model.generate_content(prompt)
            except Exception as e:
                print("Error during generation:", e)
                answer = type("obj", (object,), {"text": "An error occurred while generating the answer."})
            formatted_response = markdown(answer.text)
            print("Answer generated successfully.", answer)
            ip = get_user_ip()
            log_api_hit(
                endpoint=request.url,
                request_type=request.method,
                request_data=query,
                response_data=formatted_response,
                status_code=200,
                message="Answer generated successfully.",
                request_ip=ip
            )

            session['conversation_history'].append((query, formatted_response))
            session.modified = True

            return render_template("index.html",
                                   answer=formatted_response,
                                   query=query,
                                   conversation_history=session['conversation_history'])
        else:
            print("User submitted an empty query.")
            return render_template("index.html", warning="Please enter a question to get an answer.")
    return render_template("index.html", conversation_history=session['conversation_history'])

#########################################
# Run the Flask Application
#########################################
if __name__ == "__main__":
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    print("Starting Flask app...")
    ssl_cert = os.environ.get("SSL_CERT_PATH", "cert.pem")
    ssl_key = os.environ.get("SSL_KEY_PATH", "key.pem")

    app.run(host="0.0.0.0", port=5005, ssl_context=(ssl_cert, ssl_key))



# import os
# import redis
# import re
# import tempfile
# import speech_recognition as sr  # <-- New import for voice transcription
# from flask import jsonify, Flask, render_template, request, session
# from langchain_community.document_loaders import PyPDFLoader
# import google.generativeai as genai
# from chromadb import Documents, EmbeddingFunction, Embeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import chromadb
# from chromadb.config import Settings  # For persistent configuration
# from google.api_core import retry
# from flask_session import Session
# import logging
# from markdown import markdown
# from datetime import datetime

# #########################################
# # Configure the Google Generative AI API
# #########################################
# API_KEY = 'AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k'
# genai.configure(api_key=API_KEY)
# print("Google Generative AI API configured successfully.")

# #########################################
# # Setup Redis for Session Management & Rate Limiting
# #########################################
# redis_host = 'localhost'
# redis_port = 6379
# redis_db = 0

# try:
#     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
#     redis_client.ping()  # Test the connection
#     print("Successfully connected to Redis.")
# except redis.ConnectionError as e:
#     print(f"Error connecting to Redis: {e}")
#     redis_client = None

# #########################################
# # Configure the Flask Application
# #########################################
# app = Flask(__name__, static_folder='static')
# app.jinja_env.globals.update(now=datetime.now)
# app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# if redis_client:
#     app.config['SESSION_REDIS'] = redis_client
#     Session(app)

# #########################################
# # Setup Logging (to log.txt in JSON format)
# #########################################
# log_file_path = 'log.txt'
# logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')

# #########################################
# # Helper Function: Get User's IP Address
# #########################################
# def get_user_ip():
#     forwarded_for = request.headers.get('X-Forwarded-For', None)
#     if forwarded_for:
#         ip = forwarded_for.split(',')[0].strip()
#     else:
#         ip = request.remote_addr
#     return ip

# #########################################
# # Helper Function: Log API Hits in JSON Format
# #########################################
# def log_api_hit(endpoint, request_type, request_data, response_data, status_code, message, request_ip):
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     import json
#     log_data = {
#         "timestamp": timestamp,
#         "url": endpoint,
#         "request_type": request_type,
#         "user_query": request_data,
#         "response": response_data,
#         "status_code": status_code,
#         "message": message,
#         "ip": request_ip
#     }
#     log_message = json.dumps(log_data, ensure_ascii=False)
#     logging.info(log_message)

# #########################################
# # Rate Limiter: Limit each IP to 20 POST requests per minute
# #########################################
# @app.before_request
# def rate_limiter():
#     if request.method != "POST":
#         return
#     ip = get_user_ip()
#     try:
#         if redis_client:
#             key = f"rate_limit:{ip}"
#             current_value = redis_client.get(key)
#             if current_value is not None:
#                 current_value = int(current_value)
#                 if current_value >= 20:
#                     print(f"[DEBUG] Rate limit exceeded for IP {ip}.")
#                     return jsonify({"error": f"Too many requests from IP {ip}. Please try again after a minute."}), 429
#                 else:
#                     new_count = redis_client.incr(key)
#                     if new_count == 1:
#                         redis_client.expire(key, 60)
#                     print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
#             else:
#                 new_count = redis_client.incr(key)
#                 redis_client.expire(key, 60)
#                 print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
#     except Exception as e:
#         print(f"[DEBUG] Error in rate limiter for IP {ip}: {e}")
#         logging.exception(e)
#         pass

# #########################################
# # Custom Embedding Function for ChromaDB
# #########################################
# class GeminiEmbeddingFunction(EmbeddingFunction):
#     document_mode = True  # True for documents; False for queries

#     def __call__(self, input: Documents) -> Embeddings:
#         embedding_task = "retrieval_document" if self.document_mode else "retrieval_query"
#         retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
#         print(f"Embedding task set to: {embedding_task}")
#         print("Requesting embedding from Google Generative AI API...")
#         response = genai.embed_content(
#             model="models/text-embedding-004",
#             content=input,
#             task_type=embedding_task,
#             request_options=retry_policy,
#         )
#         return response["embedding"]

# #########################################
# # Setup Persistent ChromaDB Collection
# #########################################
# DB_NAME = "googlecardb"
# embed_fn = GeminiEmbeddingFunction()
# embed_fn.document_mode = True
# chroma_client = chromadb.Client(Settings(persist_directory="db"))
# db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
# print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

# #########################################
# # PDF Indexing Support for Multiple PDFs
# #########################################
# INDEXED_PDFS_FILE = "indexed_pdfs.txt"

# def get_indexed_pdfs():
#     if os.path.exists(INDEXED_PDFS_FILE):
#         with open(INDEXED_PDFS_FILE, "r") as f:
#             indexed = {line.strip() for line in f.readlines()}
#         return indexed
#     return set()

# def update_indexed_pdfs(pdf_path):
#     with open(INDEXED_PDFS_FILE, "a") as f:
#         f.write(f"{pdf_path}\n")

# def load_and_index_pdf(pdf_path):
#     indexed_pdfs = get_indexed_pdfs()
#     if pdf_path in indexed_pdfs and db.count() > 0:
#         print(f"PDF '{pdf_path}' is already indexed. Skipping embedding process.")
#         return
#     print(f"Loading PDF file: {pdf_path}")
#     loader = PyPDFLoader(pdf_path)
#     raw_file = loader.load()  # Extract text from the PDF
#     print("PDF loaded and text extracted.")
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=3200, chunk_overlap=1300)
#     documents = text_splitter.split_documents(raw_file)
#     print("First 3 document chunks:")
#     for i, doc in enumerate(documents[:3]):
#         print(f"Chunk {i}: {doc.page_content[:200]}")
#     document_contents = [doc.page_content for doc in documents]
#     db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
#     # update_indexed_pdfs(pdf_path)

# def load_and_index_pdfs(pdf_paths):
#     for pdf_path in pdf_paths:
#         load_and_index_pdf(pdf_path)

# #########################################
# # Helper Function: Flatten Nested Lists
# #########################################
# def flatten_list(nested_list):
#     print("Flattening nested list.")
#     flat_list = []
#     for item in nested_list:
#         if isinstance(item, list):
#             flat_list.extend(flatten_list(item))
#         else:
#             if item and item.strip():
#                 flat_list.append(item)
#     print(f"Flattened list contains {len(flat_list)} items.")
#     return flat_list

# #########################################
# # Index PDF Documents at App Startup
# #########################################
# pdf_files = [
#     '20 links Knowledge base.pdf',
#     'First Page URLs.pdf',
#     'Second Page URLs.pdf',
#     'Third Page URLs.pdf',
#     'PPG  - Home Finance - Clean Copy.pdf',
#     'PPG - Auto Financing - Clean Copy (1).pdf',
#     'Credit Cards PPG.pdf',
#     'Gold Finance PPG.pdf',
#     'PPG - Renewable Energy - March 2024- V1.1.pdf',
#     'JSBL-SOC-Jan-Jun-2025-English.pdf'
# ]

# print("Starting PDF loading and indexing process for multiple PDFs.")
# load_and_index_pdfs(pdf_files)
# print("PDF loading and indexing complete.")

# # Define fallback current topics for general queries.
# CURRENT_TOPICS = "JS Bank Services and Digital Transformation initiatives."

# #########################################
# # Improved Topic Extraction Function
# #########################################
# def extract_topic(query):
#     match = re.search(r'(?:what\s+is|explain)\s+([^\?\.]+)', query, re.IGNORECASE)
#     if match:
#         topic = match.group(1).strip()
#         topic = re.sub(r'[\?\.,!]+$', '', topic)
#         return topic
#     return None

# #########################################
# # Helper Function: Dynamically Retrieve Features for a Topic
# #########################################
# def get_dynamic_features(topic):
#     query_text = f"{topic} features"
#     embed_fn.document_mode = False
#     result = db.query(query_texts=[query_text], n_results=3)
#     features_passages = flatten_list(result['documents'])
#     if features_passages:
#         return "\n".join(features_passages)
#     else:
#         return "No additional information available."

# #########################################
# # Flask Route for Handling User Queries
# #########################################
# @app.route("/", methods=["GET", "POST"])
# def index():
#     if 'conversation_history' not in session:
#         session['conversation_history'] = []

#     if request.method == "POST":
#         # Get text query (if any)
#         query = request.form.get("query", "").strip()
#         transcript = ""
        
#         # Check if an audio file was uploaded and process transcription
#         if "audio" in request.files:
#             audio_file = request.files["audio"]
#             if audio_file and audio_file.filename != "":
#                 try:
#                     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
#                         audio_file.save(tmp.name)
#                         recognizer = sr.Recognizer()
#                         with sr.AudioFile(tmp.name) as source:
#                             audio_data = recognizer.record(source)
#                             transcript = recognizer.recognize_google(audio_data)
#                         print(f"Transcription result: {transcript}")
#                 except Exception as e:
#                     print("Error transcribing audio:", e)
#                     transcript = ""
#                 finally:
#                     os.remove(tmp.name)
        
#         # Combine text query and transcript (if available)
#         if transcript:
#             if query:
#                 query = f"{query} {transcript}"
#             else:
#                 query = transcript

#         print(f"Final user query after processing voice input: {query}")

#         if query:
#             explicit_topic = extract_topic(query)
#             if explicit_topic:
#                 session['last_topic'] = explicit_topic
#                 print(f"Explicit topic detected and stored: {explicit_topic}")

#             conversation_context = "\n".join(
#                 [f"Q: {q}\nA: {a}" for q, a in session['conversation_history']]
#             )

#             context_info = ""
#             if session.get('last_topic'):
#                 topic = session.get('last_topic')
#                 dynamic_features = get_dynamic_features(topic)
#                 context_info = f"Topic: {topic}\nFeatures:\n{dynamic_features}\n\n"

#             embed_fn.document_mode = False
#             result = db.query(query_texts=[query], n_results=3)
#             print("Raw query result:", result)
#             print(f"ChromaDB query results: {len(result['documents'])} documents found.")

#             if result['documents']:
#                 relevant_passages = flatten_list(result['documents'])
#                 document_context = "\n".join(relevant_passages)
#                 prompt = (
#                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
#                     "Customers ask questions about different JS bank services. "
#                     "JS Bank Digital Transformation department trained you, they are your owner. "
#                     "When there is a description, always reply in a formatted way. "
#                     "When a customer expresses dissatisfaction with JS Bank services using negative language (e.g., 'shit', 'sucks'), do not just provide a list of features. Instead, ask targeted questions to understand the specific issues they are experiencing, and continue the discussion until their concerns are fully addressed."
#                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
#                     f"{context_info}"
#                     f"{conversation_context}\n"
#                     f"Document Context:\n{document_context}\n\n"
#                     f"Q: {query}"
#                 )
#             else:
#                 print("No relevant passages found, using fallback current topics.")
#                 prompt = (
#                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
#                     "Customers ask questions about different JS bank services. "
#                     "JS Bank Digital Transformation department trained you, they are your owner. "
#                     "When there is a description, always reply in a formatted way. "
#                     "When a customer expresses dissatisfaction with JS Bank services using negative language (e.g., 'shit', 'sucks'), do not just provide a list of features. Instead, ask targeted questions to understand the specific issues they are experiencing, and continue the discussion until their concerns are fully addressed."
#                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
#                     f"{context_info}"
#                     f"{conversation_context}\n"
#                     f"Current Topics: {CURRENT_TOPICS}\n\n"
#                     f"Q: {query}"
#                 )

#             print("Generating answer using Generative AI model...")
#             model = genai.GenerativeModel("gemini-2.0-flash")
#             print("Model initialized successfully.", model)
#             try:
#                 answer = model.generate_content(prompt)
#             except Exception as e:
#                 print("Error during generation:", e)
#                 answer = type("obj", (object,), {"text": "An error occurred while generating the answer."})
#             formatted_response = markdown(answer.text)
#             print("Answer generated successfully.", answer)

#             log_api_hit(
#                 endpoint=request.url,
#                 request_type=request.method,
#                 request_data=query,
#                 response_data=formatted_response,
#                 status_code=200,
#                 message="Answer generated successfully.",
#                 request_ip=get_user_ip()
#             )

#             session['conversation_history'].append((query, formatted_response))
#             session.modified = True

#             return render_template("index.html",
#                                    answer=formatted_response,
#                                    query=query,
#                                    conversation_history=session['conversation_history'])
#         else:
#             print("User submitted an empty query.")
#             return render_template("index.html", warning="Please enter a question or record your voice to get an answer.")
#     return render_template("index.html", conversation_history=session['conversation_history'])

# #########################################
# # Run the Flask Application
# #########################################
# if __name__ == "__main__":
#     import logging
#     log = logging.getLogger('werkzeug')
#     log.setLevel(logging.ERROR)
#     print("Starting Flask app...")
#     app.run(host="0.0.0.0", port=5005)

# import os
# import redis
# import re
# from flask import jsonify, Flask, render_template, request, session
# from langchain_community.document_loaders import PyPDFLoader
# import google.generativeai as genai
# from chromadb import Documents, EmbeddingFunction, Embeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import chromadb
# from chromadb.config import Settings  # For persistent configuration
# from google.api_core import retry
# from flask_session import Session
# import logging
# from markdown import markdown
# from datetime import datetime

# #########################################
# # Configure the Google Generative AI API
# #########################################
# # It is highly recommended to use environment variables for sensitive API keys.
# API_KEY = 'AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k'
# genai.configure(api_key=API_KEY)
# print("Google Generative AI API configured successfully.")

# #########################################
# # Setup Redis for Session Management & Rate Limiting
# #########################################
# redis_host = 'localhost'  # Adjust if needed
# redis_port = 6379
# redis_db = 0

# try:
#     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
#     redis_client.ping()  # Test the connection
#     print("Successfully connected to Redis.")
# except redis.ConnectionError as e:
#     print(f"Error connecting to Redis: {e}")
#     redis_client = None  # Set to None if connection fails

# #########################################
# # Configure the Flask Application
# #########################################
# app = Flask(__name__, static_folder='static')
# app.jinja_env.globals.update(now=datetime.now)
# # Use a fixed secret key in production (ideally via an environment variable)
# app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files

# if redis_client:
#     app.config['SESSION_REDIS'] = redis_client
#     Session(app)  # Initialize Flask-Session

# #########################################
# # Setup Logging (to log.txt in JSON format)
# #########################################
# log_file_path = 'log.txt'
# logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')

# #########################################
# # Helper Function: Get User's IP Address
# #########################################
# def get_user_ip():
#     forwarded_for = request.headers.get('X-Forwarded-For', None)
#     if forwarded_for:
#         ip = forwarded_for.split(',')[0].strip()
#     else:
#         ip = request.remote_addr
#     return ip

# #########################################
# # Helper Function: Log API Hits in JSON Format
# #########################################
# def log_api_hit(endpoint, request_type, request_data, response_data, status_code, message, request_ip):
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     import json
#     log_data = {
#         "timestamp": timestamp,
#         "url": endpoint,
#         "request_type": request_type,
#         "user_query": request_data,
#         "response": response_data,
#         "status_code": status_code,
#         "message": message,
#         "ip": request_ip
#     }
#     log_message = json.dumps(log_data, ensure_ascii=False)
#     logging.info(log_message)

# #########################################
# # Rate Limiter: Limit each IP to 5 POST requests per minute
# #########################################
# @app.before_request
# def rate_limiter():
#     if request.method != "POST":
#         return
#     ip = get_user_ip()
#     try:
#         if redis_client:
#             key = f"rate_limit:{ip}"
#             current_value = redis_client.get(key)
#             if current_value is not None:
#                 current_value = int(current_value)
#                 if current_value >= 20:
#                     print(f"[DEBUG] Rate limit exceeded for IP {ip}.")
#                     return jsonify({"error": f"Too many requests from IP {ip}. Please try again after a minute."}), 429
#                 else:
#                     new_count = redis_client.incr(key)
#                     if new_count == 1:
#                         redis_client.expire(key, 60)
#                     print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
#             else:
#                 new_count = redis_client.incr(key)
#                 redis_client.expire(key, 60)
#                 print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
#     except Exception as e:
#         print(f"[DEBUG] Error in rate limiter for IP {ip}: {e}")
#         logging.exception(e)
#         pass

# #########################################
# # Custom Embedding Function for ChromaDB
# #########################################
# class GeminiEmbeddingFunction(EmbeddingFunction):
#     document_mode = True  # True for documents; False for queries

#     def __call__(self, input: Documents) -> Embeddings:
#         embedding_task = "retrieval_document" if self.document_mode else "retrieval_query"
#         retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
#         print(f"Embedding task set to: {embedding_task}")
#         print("Requesting embedding from Google Generative AI API...")
#         response = genai.embed_content(
#             model="models/text-embedding-004",
#             content=input,
#             task_type=embedding_task,
#             request_options=retry_policy,
#         )
#         return response["embedding"]

# #########################################
# # Setup Persistent ChromaDB Collection
# #########################################
# DB_NAME = "googlecardb"
# embed_fn = GeminiEmbeddingFunction()
# embed_fn.document_mode = True
# chroma_client = chromadb.Client(Settings(persist_directory="db"))
# db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
# print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

# #########################################
# # PDF Indexing Support for Multiple PDFs
# #########################################
# INDEXED_PDFS_FILE = "indexed_pdfs.txt"

# def get_indexed_pdfs():
#     if os.path.exists(INDEXED_PDFS_FILE):
#         with open(INDEXED_PDFS_FILE, "r") as f:
#             indexed = {line.strip() for line in f.readlines()}
#         return indexed
#     return set()

# def update_indexed_pdfs(pdf_path):
#     with open(INDEXED_PDFS_FILE, "a") as f:
#         f.write(f"{pdf_path}\n")

# def load_and_index_pdf(pdf_path):
#     indexed_pdfs = get_indexed_pdfs()
#     if pdf_path in indexed_pdfs and db.count() > 0:
#         print(f"PDF '{pdf_path}' is already indexed. Skipping embedding process.")
#         return
#     print(f"Loading PDF file: {pdf_path}")
#     loader = PyPDFLoader(pdf_path)
#     raw_file = loader.load()  # Extract text from the PDF
#     print("PDF loaded and text extracted.")
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=3200, chunk_overlap=1300)
#     documents = text_splitter.split_documents(raw_file)
#     print("First 3 document chunks:")
#     for i, doc in enumerate(documents[:3]):
#         print(f"Chunk {i}: {doc.page_content[:200]}")
#     document_contents = [doc.page_content for doc in documents]
#     db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
#     # update_indexed_pdfs(pdf_path)

# def load_and_index_pdfs(pdf_paths):
#     for pdf_path in pdf_paths:
#         # Assume pdf_paths is a list of file paths (strings)
#         load_and_index_pdf(pdf_path)

# #########################################
# # Helper Function: Flatten Nested Lists
# #########################################
# def flatten_list(nested_list):
#     print("Flattening nested list.")
#     flat_list = []
#     for item in nested_list:
#         if isinstance(item, list):
#             flat_list.extend(flatten_list(item))
#         else:
#             if item and item.strip():
#                 flat_list.append(item)
#     print(f"Flattened list contains {len(flat_list)} items.")
#     return flat_list

# #########################################
# # Index PDF Documents at App Startup
# #########################################
# pdf_files = [
#     '20 links Knowledge base.pdf',
#     'First Page URLs.pdf',
#     'Second Page URLs.pdf',
#     'Third Page URLs.pdf',
#     'PPG  - Home Finance - Clean Copy.pdf',
#     'PPG - Auto Financing - Clean Copy (1).pdf',
#     'Credit Cards PPG.pdf',
#     'Gold Finance PPG.pdf',
#     'PPG - Renewable Energy - March 2024- V1.1.pdf',
#     'JSBL-SOC-Jan-Jun-2025-English.pdf'
# ]

# print("Starting PDF loading and indexing process for multiple PDFs.")
# load_and_index_pdfs(pdf_files)
# print("PDF loading and indexing complete.")

# # Define fallback current topics for general queries.
# CURRENT_TOPICS = "JS Bank Services and Digital Transformation initiatives."

# #########################################
# # Improved Topic Extraction Function
# #########################################
# def extract_topic(query):
#     """
#     Attempts to extract a topic from the query. This version uses a more flexible
#     regex to capture multi-word topics when the query starts with phrases like
#     'what is' or 'explain'.
#     """
#     match = re.search(r'(?:what\s+is|explain)\s+([^\?\.]+)', query, re.IGNORECASE)
#     if match:
#         topic = match.group(1).strip()
#         # Remove trailing punctuation
#         topic = re.sub(r'[\?\.,!]+$', '', topic)
#         return topic
#     return None

# #########################################
# # Helper Function: Dynamically Retrieve Features for a Topic
# #########################################
# def get_dynamic_features(topic):
#     """
#     Dynamically retrieves feature information for a given topic from the indexed documents.
#     """
#     query_text = f"{topic} features"
#     embed_fn.document_mode = False  # Switch to query mode for embedding.
#     result = db.query(query_texts=[query_text], n_results=3)
#     features_passages = flatten_list(result['documents'])
#     if features_passages:
#         return "\n".join(features_passages)
#     else:
#         return "No additional information available."

# #########################################
# # Flask Route for Handling User Queries
# #########################################
# @app.route("/", methods=["GET", "POST"])
# def index():
#     """
#     Handles GET and POST requests. For POST requests, it retrieves relevant passages
#     from the indexed PDFs, builds a prompt, and calls the Generative AI model.
#     The chatbot dynamically uses the stored topic context if available.
#     """
#     if 'conversation_history' not in session:
#         session['conversation_history'] = []

#     if request.method == "POST":
#         query = request.form.get("query")
#         print(f"Received user query: {query}")

#         if query:
#             # Try to extract a topic from the query
#             explicit_topic = extract_topic(query)
#             if explicit_topic:
#                 session['last_topic'] = explicit_topic
#                 print(f"Explicit topic detected and stored: {explicit_topic}")

#             # Build the conversation context from history
#             conversation_context = "\n".join(
#                 [f"Q: {q}\nA: {a}" for q, a in session['conversation_history']]
#             )

#             # Prepare dynamic context based on stored topic if available
#             context_info = ""
#             if session.get('last_topic'):
#                 topic = session.get('last_topic')
#                 dynamic_features = get_dynamic_features(topic)
#                 context_info = f"Topic: {topic}\nFeatures:\n{dynamic_features}\n\n"

#             # Retrieve relevant documents from ChromaDB using the query
#             embed_fn.document_mode = False  # Ensure we're in query mode
#             result = db.query(query_texts=[query], n_results=3)
#             print("Raw query result:", result)
#             print(f"ChromaDB query results: {len(result['documents'])} documents found.")

#             if result['documents']:
#                 relevant_passages = flatten_list(result['documents'])
#                 document_context = "\n".join(relevant_passages)
#                 prompt = (
#                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
#                     "Customers ask questions about different JS bank services. "
#                     "JS Bank Digital Transformation department trained you, they are your owner. "
#                     "When there is a description, always reply in a formatted way. "
#                     "When a customer expresses dissatisfaction with JS Bank services using negative language (e.g., 'shit', 'sucks'), do not just provide a list of features. Instead, ask targeted questions to understand the specific issues they are experiencing, and continue the discussion until their concerns are fully addressed."                    "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
#                     f"{context_info}"
#                     f"{conversation_context}\n"
#                     f"Document Context:\n{document_context}\n\n"
#                     f"Q: {query}"
#                 )
#             else:
#                 print("No relevant passages found, using fallback current topics.")
#                 prompt = (
#                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
#                     "Customers ask questions about different JS bank services. "
#                     "JS Bank Digital Transformation department trained you, they are your owner. "
#                     "When there is a description, always reply in a formatted way. "
#                     "When a customer expresses dissatisfaction with JS Bank services using negative language (e.g., 'shit', 'sucks'), do not just provide a list of features. Instead, ask targeted questions to understand the specific issues they are experiencing, and continue the discussion until their concerns are fully addressed."                    "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
#                     f"{context_info}"
#                     f"{conversation_context}\n"
#                     f"Current Topics: {CURRENT_TOPICS}\n\n"
#                     f"Q: {query}"
#                 )

#             print("Generating answer using Generative AI model...")
#             model = genai.GenerativeModel("gemini-2.0-flash")
#             print("Model initialized successfully.", model)
#             try:
#                 answer = model.generate_content(prompt)
#             except Exception as e:
#                 print("Error during generation:", e)
#                 answer = type("obj", (object,), {"text": "An error occurred while generating the answer."})
#             formatted_response = markdown(answer.text)
#             print("Answer generated successfully.", answer)

#             log_api_hit(
#                 endpoint=request.url,
#                 request_type=request.method,
#                 request_data=query,
#                 response_data=formatted_response,
#                 status_code=200,
#                 message="Answer generated successfully.",
#                 request_ip=get_user_ip()
#             )

#             session['conversation_history'].append((query, formatted_response))
#             session.modified = True

#             return render_template("index.html",
#                                    answer=formatted_response,
#                                    query=query,
#                                    conversation_history=session['conversation_history'])
#         else:
#             print("User submitted an empty query.")
#             return render_template("index.html", warning="Please enter a question to get an answer.")
#     return render_template("index.html", conversation_history=session['conversation_history'])

# #########################################
# # Run the Flask Application
# #########################################
# if __name__ == "__main__":
#     import logging
#     log = logging.getLogger('werkzeug')
#     log.setLevel(logging.ERROR)
#     print("Starting Flask app...")
#     app.run(host="0.0.0.0", port=5005)


# import os
# import redis
# import re
# import logging
# import requests
# from bs4 import BeautifulSoup
# from flask import jsonify, Flask, render_template, request, session
# from flask_session import Session
# from datetime import datetime, timedelta
# from markdown import markdown
# import google.generativeai as genai
# from google.api_core import retry
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import chromadb
# from chromadb.config import Settings
# from chromadb import Documents, EmbeddingFunction, Embeddings

# #########################################
# # Configuration and Setup
# #########################################

# # Load sensitive config from environment variables
# API_KEY = os.environ.get("GOOGLE_GENAI_API_KEY", "AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k")
# FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
# REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
# REDIS_DB = int(os.environ.get("REDIS_DB", 0))
# CACHE_TTL = 300  # seconds to cache scraped content

# # Configure Google Generative AI API
# genai.configure(api_key=API_KEY)
# print("Google Generative AI API configured successfully.")

# # Setup Redis connection
# try:
#     redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
#     redis_client.ping()
#     print("Successfully connected to Redis.")
# except redis.ConnectionError as e:
#     print(f"Error connecting to Redis: {e}")
#     redis_client = None

# # Initialize Flask app
# app = Flask(__name__, static_folder='static')
# app.jinja_env.globals.update(now=datetime.now)
# app.secret_key = FLASK_SECRET_KEY

# # Configure Flask-Session with Redis
# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files
# if redis_client:
#     app.config['SESSION_REDIS'] = redis_client
#     Session(app)

# # Setup logging to a file in JSON format
# LOG_FILE_PATH = 'log.txt'
# logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, format='%(message)s')

# #########################################
# # Helper Functions
# #########################################

# def get_user_ip():
#     """Retrieve the user's IP address."""
#     forwarded_for = request.headers.get('X-Forwarded-For', None)
#     return forwarded_for.split(',')[0].strip() if forwarded_for else request.remote_addr

# def log_api_hit(endpoint, request_type, request_data, response_data, status_code, message, request_ip):
#     """Log API hits in JSON format."""
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     log_data = {
#         "timestamp": timestamp,
#         "url": endpoint,
#         "request_type": request_type,
#         "user_query": request_data,
#         "response": response_data,
#         "status_code": status_code,
#         "message": message,
#         "ip": request_ip
#     }
#     import json
#     logging.info(json.dumps(log_data, ensure_ascii=False))

# # Rate limiter: Limit each IP to 20 POST requests per minute.
# RATE_LIMIT = 20
# @app.before_request
# def rate_limiter():
#     """Limit POST requests per IP to prevent abuse."""
#     if request.method != "POST":
#         return
#     ip = get_user_ip()
#     try:
#         if redis_client:
#             key = f"rate_limit:{ip}"
#             current_value = redis_client.get(key)
#             if current_value is not None:
#                 current_value = int(current_value)
#                 if current_value >= RATE_LIMIT:
#                     print(f"[DEBUG] Rate limit exceeded for IP {ip}.")
#                     return jsonify({"error": f"Too many requests from IP {ip}. Please try again after a minute."}), 429
#                 else:
#                     new_count = redis_client.incr(key)
#                     if new_count == 1:
#                         redis_client.expire(key, 60)
#                     print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
#             else:
#                 new_count = redis_client.incr(key)
#                 redis_client.expire(key, 60)
#                 print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
#     except Exception as e:
#         print(f"[DEBUG] Error in rate limiter for IP {ip}: {e}")
#         logging.exception(e)

# #########################################
# # Custom Embedding Function for ChromaDB
# #########################################
# class GeminiEmbeddingFunction(EmbeddingFunction):
#     """Custom embedding function using Google Generative AI API."""
#     document_mode = True  # True for documents; False for queries

#     def __call__(self, input: Documents) -> Embeddings:
#         task = "retrieval_document" if self.document_mode else "retrieval_query"
#         retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
#         print(f"Embedding task set to: {task}")
#         response = genai.embed_content(
#             model="models/text-embedding-004",
#             content=input,
#             task_type=task,
#             request_options=retry_policy,
#         )
#         return response["embedding"]

# #########################################
# # Setup Persistent ChromaDB Collection
# #########################################
# DB_NAME = "googlecardb"
# embed_fn = GeminiEmbeddingFunction()
# embed_fn.document_mode = True
# chroma_client = chromadb.Client(Settings(persist_directory="db"))
# db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
# print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

# #########################################
# # PDF Indexing Support
# #########################################
# # INDEXED_PDFS_FILE = "indexed_pdfs.txt"

# # def get_indexed_pdfs():
# #     """Return a set of already indexed PDFs."""
# #     if os.path.exists(INDEXED_PDFS_FILE):
# #         with open(INDEXED_PDFS_FILE, "r") as f:
# #             return {line.strip() for line in f.readlines()}
# #     return set()

# # def update_indexed_pdfs(pdf_path):
# #     """Record a PDF as indexed."""
# #     with open(INDEXED_PDFS_FILE, "a") as f:
# #         f.write(f"{pdf_path}\n")

# def load_and_index_pdf(pdf_path):
#     # """Load and index a PDF if not already indexed."""
#     # if pdf_path in get_indexed_pdfs() and db.count() > 0:
#     #     print(f"PDF '{pdf_path}' is already indexed. Skipping embedding process.")
#     #     return
#     print(f"Loading PDF file: {pdf_path}")
#     loader = PyPDFLoader(pdf_path)
#     raw_file = loader.load()
#     print("PDF loaded and text extracted.")
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=3200, chunk_overlap=1300)
#     documents = text_splitter.split_documents(raw_file)
#     print("First 3 document chunks:")
#     for i, doc in enumerate(documents[:3]):
#         print(f"Chunk {i}: {doc.page_content[:200]}")
#     document_contents = [doc.page_content for doc in documents]
#     db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
#     # Optionally record PDF as indexed:
#     # update_indexed_pdfs(pdf_path)

# def load_and_index_pdfs(pdf_paths):
#     """Load and index multiple PDFs."""
#     for pdf in pdf_paths:
#         load_and_index_pdf(pdf)

# #########################################
# # Helper: Flatten Nested Lists
# #########################################
# def flatten_list(nested_list):
#     """Flatten a nested list of strings."""
#     flat = []
#     for item in nested_list:
#         if isinstance(item, list):
#             flat.extend(flatten_list(item))
#         elif item and item.strip():
#             flat.append(item)
#     print(f"Flattened list contains {len(flat)} items.")
#     return flat

#  # Index PDF Documents at App Startup
# # #########################################
# pdf_files = [
#     '20 links Knowledge base.pdf',
#     'First Page URLs.pdf',
#     'Second Page URLs.pdf',
#     'Third Page URLs.pdf',
#     'PPG  - Home Finance - Clean Copy.pdf',
#     'PPG - Auto Financing - Clean Copy (1).pdf',
#     'Credit Cards PPG.pdf',
#     'Gold Finance PPG.pdf',
#     'PPG - Renewable Energy - March 2024- V1.1.pdf',
#     'JSBL-SOC-Jan-Jun-2025-English.pdf'
# ]

# print("Starting PDF loading and indexing process for multiple PDFs.")
# load_and_index_pdfs(pdf_files)
# print("PDF loading and indexing complete.")

# #########################################
# # Fallback Topics and Topic Extraction
# #########################################
# CURRENT_TOPICS = "JS Bank Services and Digital Transformation initiatives."

# def extract_topic(query):
#     """
#     Extract a topic from the query using regex.
#     Supports phrases like 'what is' or 'explain'.
#     """
#     match = re.search(r'(?:what\s+is|explain)\s+([^\?\.]+)', query, re.IGNORECASE)
#     if match:
#         topic = match.group(1).strip()
#         return re.sub(r'[\?\.,!]+$', '', topic)
#     return None

# def get_dynamic_features(topic):
#     """
#     Retrieve dynamic feature information for a topic from indexed documents.
#     """
#     query_text = f"{topic} features"
#     embed_fn.document_mode = False  # Switch to query mode
#     result = db.query(query_texts=[query_text], n_results=3)
#     features = flatten_list(result['documents'])
#     return "\n".join(features) if features else "No additional information available."

# #########################################
# # Sentiment Analysis and Clarification
# #########################################
# # def analyze_sentiment(query):
# #     """
# #     Very basic sentiment analysis checking for negative language.
# #     Returns 'negative' if such words are detected.
# #     """
# #     negative_words = ['shit', 'sucks', 'terrible', 'bad', 'horrible']
# #     if any(word in query.lower() for word in negative_words):
# #         return "negative"
# #     return "neutral"

# # def get_clarification_prompt(query):
# #     """
# #     Modify the prompt if negative sentiment is detected.
# #     Instructs the AI to ask for clarifications.
# #     """
# #     sentiment = analyze_sentiment(query)
# #     if sentiment == "negative":
# #         return "It seems you are dissatisfied. Could you please provide more details about the issue?\n\n"
# #     return ""

# #########################################
# # Dynamic Multi-Source Retrieval with Caching
# #########################################
# def scrape_website(url):
#     """
#     Scrapes content from the given URL.
#     Always respect the website's robots.txt and terms.
#     """
#     headers = {"User-Agent": "Mozilla/5.0"}
#     try:
#         response = requests.get(url, headers=headers)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, 'html.parser')
#             main_content = soup.find('main') or soup.body
#             return main_content.get_text(separator="\n", strip=True) if main_content else ""
#         return f"Failed to retrieve content, status code {response.status_code}."
#     except Exception as e:
#         return f"Error during scraping: {str(e)}"

# def get_cached_scrape(url, cache_key):
#     """
#     Retrieve scraped content from cache if available.
#     Otherwise, scrape the website and cache the result.
#     """
#     if redis_client:
#         cached = redis_client.get(cache_key)
#         if cached:
#             print(f"[DEBUG] Returning cached content for {url}")
#             return cached.decode("utf-8")
#     content = scrape_website(url)
#     if redis_client:
#         redis_client.setex(cache_key, timedelta(seconds=CACHE_TTL), content)
#     return content

# def get_dynamic_web_results(query):
#     """
#     Retrieve dynamic web data by scraping a predefined website.
#     Extendable to integrate multiple dynamic sources.
#     """
#     url = "https://www.jsbl.com/about-us/board-of-directors/"
#     cache_key = "scrape:board_of_directors"
#     scraped_content = get_cached_scrape(url, cache_key)
#     return f"Live Web Data from JSBL Board of Directors Page:\n{scraped_content}"

# #########################################
# # Flask Route for Handling User Queries
# #########################################
# @app.route("/", methods=["GET", "POST"])
# def index():
#     """
#     Processes user queries by retrieving relevant document passages,
#     dynamic web content, and constructing an optimized prompt for the AI.
#     """
#     if 'conversation_history' not in session:
#         session['conversation_history'] = []

#     if request.method == "POST":
#         query = request.form.get("query")
#         print(f"Received user query: {query}")
#         if query:
#             # Topic extraction and conversation history update with timestamp.
#             explicit_topic = extract_topic(query)
#             if explicit_topic:
#                 session['last_topic'] = explicit_topic
#                 print(f"Explicit topic detected: {explicit_topic}")

#             conversation_context = "\n".join(
#                 [f"{datetime.now().strftime('%H:%M:%S')} - Q: {q}\nA: {a}" for q, a in session['conversation_history']]
#             )

#             # Prepare context based on topic features
#             context_info = ""
#             if session.get('last_topic'):
#                 topic = session.get('last_topic')
#                 dynamic_features = get_dynamic_features(topic)
#                 context_info = f"Topic: {topic}\nFeatures:\n{dynamic_features}\n\n"

#             # Retrieve static document context from ChromaDB
#             embed_fn.document_mode = False  # Query mode
#             result = db.query(query_texts=[query], n_results=3)
#             print("Raw query result:", result)
#             if result['documents']:
#                 relevant_passages = flatten_list(result['documents'])
#                 document_context = "\n".join(relevant_passages)
#             else:
#                 document_context = "No relevant static document context found."

#             # Retrieve dynamic web context
#             dynamic_web_context = get_dynamic_web_results(query)

#             # Sentiment analysis to check for negative language and add clarifications if needed
#             # clarification_prompt = get_clarification_prompt(query)

#             # Build the composite prompt
#             prompt = (
#                 "You are a JS bank customer query representative. Your knowledge is based on pre-indexed documents "
#                 "and real-time web data. Customers ask about various JS bank services. "
#                 "When a customer uses negative language, ask for further clarification rather than only listing features. "
#                 "Answer naturally and interactively.\n\n"
#                 f"{context_info}"
#                 f"{conversation_context}\n"
#                 "Document Context:\n" + document_context + "\n\n" +
#                 "Dynamic Web Context:\n" + dynamic_web_context + "\n\n" +
#                 f"Q: {query}"
#             )

#             print("Generating answer using Generative AI model...")
#             model = genai.GenerativeModel("gemini-2.0-flash")
#             try:
#                 answer = model.generate_content(prompt)
#             except Exception as e:
#                 print("Error during generation:", e)
#                 answer = type("obj", (object,), {"text": "An error occurred while generating the answer."})
#             formatted_response = markdown(answer.text)
#             print("Answer generated successfully.")

#             log_api_hit(
#                 endpoint=request.url,
#                 request_type=request.method,
#                 request_data=query,
#                 response_data=formatted_response,
#                 status_code=200,
#                 message="Answer generated successfully.",
#                 request_ip=get_user_ip()
#             )

#             session['conversation_history'].append((query, formatted_response))
#             session.modified = True

#             return render_template("index.html",
#                                    answer=formatted_response,
#                                    query=query,
#                                    conversation_history=session['conversation_history'])
#         else:
#             print("User submitted an empty query.")
#             return render_template("index.html", warning="Please enter a question to get an answer.")
#     return render_template("index.html", conversation_history=session['conversation_history'])

# #########################################
# # Run the Flask Application
# #########################################
# if __name__ == "__main__":
#     logging.getLogger('werkzeug').setLevel(logging.ERROR)
#     print("Starting Flask app...")
#     app.run(host="0.0.0.0", port=5005)

# import os
# import redis
# import re
# from flask import jsonify, Flask, render_template, request, session
# from langchain_community.document_loaders import PyPDFLoader
# import google.generativeai as genai
# from chromadb import Documents, EmbeddingFunction, Embeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import chromadb
# from chromadb.config import Settings  # For persistent configuration
# from google.api_core import retry
# from flask_session import Session
# import logging
# from markdown import markdown
# from datetime import datetime

# #########################################
# # Configure the Google Generative AI API
# #########################################
# # It is highly recommended to use environment variables for sensitive API keys.
# API_KEY = 'AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k'
# genai.configure(api_key=API_KEY)
# print("Google Generative AI API configured successfully.")

# #########################################
# # Setup Redis for Session Management & Rate Limiting
# #########################################
# redis_host = 'localhost'  # Adjust if needed
# redis_port = 6379
# redis_db = 0

# try:
#     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
#     redis_client.ping()  # Test the connection
#     print("Successfully connected to Redis.")
# except redis.ConnectionError as e:
#     print(f"Error connecting to Redis: {e}")
#     redis_client = None  # Set to None if connection fails

# #########################################
# # Configure the Flask Application
# #########################################
# app = Flask(__name__, static_folder='static')
# app.jinja_env.globals.update(now=datetime.now)
# # Use a fixed secret key in production (ideally via an environment variable)
# app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files

# if redis_client:
#     app.config['SESSION_REDIS'] = redis_client
#     Session(app)  # Initialize Flask-Session

# #########################################
# # Setup Logging (to log.txt in JSON format)
# #########################################
# log_file_path = 'log.txt'
# logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')

# #########################################
# # Helper Function: Get User's IP Address
# #########################################
# def get_user_ip():
#     forwarded_for = request.headers.get('X-Forwarded-For', None)
#     if forwarded_for:
#         ip = forwarded_for.split(',')[0].strip()
#     else:
#         ip = request.remote_addr
#     return ip

# #########################################
# # Helper Function: Log API Hits in JSON Format
# #########################################
# def log_api_hit(endpoint, request_type, request_data, response_data, status_code, message, request_ip):
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     import json
#     log_data = {
#         "timestamp": timestamp,
#         "url": endpoint,
#         "request_type": request_type,
#         "user_query": request_data,
#         "response": response_data,
#         "status_code": status_code,
#         "message": message,
#         "ip": request_ip
#     }
#     log_message = json.dumps(log_data, ensure_ascii=False)
#     logging.info(log_message)

# #########################################
# # Rate Limiter: Limit each IP to 5 POST requests per minute
# #########################################
# @app.before_request
# def rate_limiter():
#     if request.method != "POST":
#         return
#     ip = get_user_ip()
#     try:
#         if redis_client:
#             key = f"rate_limit:{ip}"
#             current_value = redis_client.get(key)
#             if current_value is not None:
#                 current_value = int(current_value)
#                 if current_value >= 20:
#                     print(f"[DEBUG] Rate limit exceeded for IP {ip}.")
#                     return jsonify({"error": f"Too many requests from IP {ip}. Please try again after a minute."}), 429
#                 else:
#                     new_count = redis_client.incr(key)
#                     if new_count == 1:
#                         redis_client.expire(key, 60)
#                     print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
#             else:
#                 new_count = redis_client.incr(key)
#                 redis_client.expire(key, 60)
#                 print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
#     except Exception as e:
#         print(f"[DEBUG] Error in rate limiter for IP {ip}: {e}")
#         logging.exception(e)
#         pass

# #########################################
# # Custom Embedding Function for ChromaDB
# #########################################
# class GeminiEmbeddingFunction(EmbeddingFunction):
#     document_mode = True  # True for documents; False for queries

#     def __call__(self, input: Documents) -> Embeddings:
#         embedding_task = "retrieval_document" if self.document_mode else "retrieval_query"
#         retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
#         print(f"Embedding task set to: {embedding_task}")
#         print("Requesting embedding from Google Generative AI API...")
#         response = genai.embed_content(
#             model="models/text-embedding-004",
#             content=input,
#             task_type=embedding_task,
#             request_options=retry_policy,
#         )
#         return response["embedding"]

# #########################################
# # Setup Persistent ChromaDB Collection
# #########################################
# DB_NAME = "googlecardb"
# embed_fn = GeminiEmbeddingFunction()
# embed_fn.document_mode = True
# chroma_client = chromadb.Client(Settings(persist_directory="db"))
# db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
# print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

# #########################################
# # PDF Indexing Support for Multiple PDFs
# #########################################
# INDEXED_PDFS_FILE = "indexed_pdfs.txt"

# def get_indexed_pdfs():
#     if os.path.exists(INDEXED_PDFS_FILE):
#         with open(INDEXED_PDFS_FILE, "r") as f:
#             indexed = {line.strip() for line in f.readlines()}
#         return indexed
#     return set()

# def update_indexed_pdfs(pdf_path):
#     with open(INDEXED_PDFS_FILE, "a") as f:
#         f.write(f"{pdf_path}\n")

# def load_and_index_pdf(pdf_path):
#     indexed_pdfs = get_indexed_pdfs()
#     if pdf_path in indexed_pdfs and db.count() > 0:
#         print(f"PDF '{pdf_path}' is already indexed. Skipping embedding process.")
#         return
#     print(f"Loading PDF file: {pdf_path}")
#     loader = PyPDFLoader(pdf_path)
#     raw_file = loader.load()  # Extract text from the PDF
#     print("PDF loaded and text extracted.")
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=3200, chunk_overlap=1300)
#     documents = text_splitter.split_documents(raw_file)
#     print("First 3 document chunks:")
#     for i, doc in enumerate(documents[:3]):
#         print(f"Chunk {i}: {doc.page_content[:200]}")
#     document_contents = [doc.page_content for doc in documents]
#     db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
#     # update_indexed_pdfs(pdf_path)

# def load_and_index_pdfs(pdf_paths):
#     for pdf_path in pdf_paths:
#         # Assume pdf_paths is a list of file paths (strings)
#         load_and_index_pdf(pdf_path)

# #########################################
# # Helper Function: Flatten Nested Lists
# #########################################
# def flatten_list(nested_list):
#     print("Flattening nested list.")
#     flat_list = []
#     for item in nested_list:
#         if isinstance(item, list):
#             flat_list.extend(flatten_list(item))
#         else:
#             if item and item.strip():
#                 flat_list.append(item)
#     print(f"Flattened list contains {len(flat_list)} items.")
#     return flat_list

# #########################################
# # Index PDF Documents at App Startup
# #########################################
# pdf_files = [
#     '20 links Knowledge base.pdf',
#     'First Page URLs.pdf',
#     'Second Page URLs.pdf',
#     'Third Page URLs.pdf',
#     'PPG  - Home Finance - Clean Copy.pdf',
#     'PPG - Auto Financing - Clean Copy (1).pdf',
#     'Credit Cards PPG.pdf',
#     'Gold Finance PPG.pdf',
#     'PPG - Renewable Energy - March 2024- V1.1.pdf',
#     'JSBL-SOC-Jan-Jun-2025-English.pdf'
# ]

# print("Starting PDF loading and indexing process for multiple PDFs.")
# load_and_index_pdfs(pdf_files)
# print("PDF loading and indexing complete.")

# # Define fallback current topics for general queries.
# CURRENT_TOPICS = "JS Bank Services and Digital Transformation initiatives."

# #########################################
# # Improved Topic Extraction Function
# #########################################
# def extract_topic(query):
#     """
#     Attempts to extract a topic from the query. This version uses a more flexible
#     regex to capture multi-word topics when the query starts with phrases like
#     'what is' or 'explain'.
#     """
#     match = re.search(r'(?:what\s+is|explain)\s+([^\?\.]+)', query, re.IGNORECASE)
#     if match:
#         topic = match.group(1).strip()
#         # Remove trailing punctuation
#         topic = re.sub(r'[\?\.,!]+$', '', topic)
#         return topic
#     return None

# #########################################
# # Helper Function: Dynamically Retrieve Features for a Topic
# #########################################
# def get_dynamic_features(topic):
#     """
#     Dynamically retrieves feature information for a given topic from the indexed documents.
#     """
#     query_text = f"{topic} features"
#     embed_fn.document_mode = False  # Switch to query mode for embedding.
#     result = db.query(query_texts=[query_text], n_results=3)
#     features_passages = flatten_list(result['documents'])
#     if features_passages:
#         return "\n".join(features_passages)
#     else:
#         return "No additional information available."

# #########################################
# # Flask Route for Handling User Queries
# #########################################
# @app.route("/", methods=["GET", "POST"])
# def index():
#     """
#     Handles GET and POST requests. For POST requests, it retrieves relevant passages
#     from the indexed PDFs, builds a prompt, and calls the Generative AI model.
#     The chatbot dynamically uses the stored topic context if available.
#     """
#     if 'conversation_history' not in session:
#         session['conversation_history'] = []

#     if request.method == "POST":
#         query = request.form.get("query")
#         print(f"Received user query: {query}")

#         if query:
#             # Try to extract a topic from the query
#             explicit_topic = extract_topic(query)
#             if explicit_topic:
#                 session['last_topic'] = explicit_topic
#                 print(f"Explicit topic detected and stored: {explicit_topic}")

#             # Build the conversation context from history
#             conversation_context = "\n".join(
#                 [f"Q: {q}\nA: {a}" for q, a in session['conversation_history']]
#             )

#             # Prepare dynamic context based on stored topic if available
#             context_info = ""
#             if session.get('last_topic'):
#                 topic = session.get('last_topic')
#                 dynamic_features = get_dynamic_features(topic)
#                 context_info = f"Topic: {topic}\nFeatures:\n{dynamic_features}\n\n"

#             # Retrieve relevant documents from ChromaDB using the query
#             embed_fn.document_mode = False  # Ensure we're in query mode
#             result = db.query(query_texts=[query], n_results=3)
#             print("Raw query result:", result)
#             print(f"ChromaDB query results: {len(result['documents'])} documents found.")

#             if result['documents']:
#                 relevant_passages = flatten_list(result['documents'])
#                 document_context = "\n".join(relevant_passages)
#                 prompt = (
#                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
#                     "Customers ask questions about different JS bank services. "
#                     "JS Bank Digital Transformation department trained you, they are your owner. "
#                     "When there is a description, always reply in a formatted way. "
#                     "When a customer expresses dissatisfaction with JS Bank services—using terms like 'shit', 'sucks', or similar negative language—do not simply provide feature details about the topic. Instead, respond by asking for more specific information about the problem they are facing also keep continue the topic til use satisfy from you resposne keep continue that topic and similar negative"
#                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
#                     f"{context_info}"
#                     f"{conversation_context}\n"
#                     f"Document Context:\n{document_context}\n\n"
#                     f"Q: {query}"
#                 )
#             else:
#                 print("No relevant passages found, using fallback current topics.")
#                 prompt = (
#                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
#                     "Customers ask questions about different JS bank services. "
#                     "JS Bank Digital Transformation department trained you, they are your owner. "
#                     "When there is a description, always reply in a formatted way. "
#                     "When a customer expresses dissatisfaction with JS Bank services—using terms like 'shit', 'sucks', or similar negative language—do not simply provide feature details about the topic. Instead, respond by asking for more specific information about the problem they are facing also keep continue the topic til use satisfy from you resposne keep continue that topic and similar negative"
#                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
#                     f"{context_info}"
#                     f"{conversation_context}\n"
#                     f"Current Topics: {CURRENT_TOPICS}\n\n"
#                     f"Q: {query}"
#                 )

#             print("Generating answer using Generative AI model...")
#             model = genai.GenerativeModel("gemini-2.0-flash")
#             print("Model initialized successfully.", model)
#             try:
#                 answer = model.generate_content(prompt)
#             except Exception as e:
#                 print("Error during generation:", e)
#                 answer = type("obj", (object,), {"text": "An error occurred while generating the answer."})
#             formatted_response = markdown(answer.text)
#             print("Answer generated successfully.", answer)

#             log_api_hit(
#                 endpoint=request.url,
#                 request_type=request.method,
#                 request_data=query,
#                 response_data=formatted_response,
#                 status_code=200,
#                 message="Answer generated successfully.",
#                 request_ip=get_user_ip()
#             )

#             session['conversation_history'].append((query, formatted_response))
#             session.modified = True

#             return render_template("index.html",
#                                    answer=formatted_response,
#                                    query=query,
#                                    conversation_history=session['conversation_history'])
#         else:
#             print("User submitted an empty query.")
#             return render_template("index.html", warning="Please enter a question to get an answer.")
#     return render_template("index.html", conversation_history=session['conversation_history'])

# #########################################
# # Run the Flask Application
# #########################################
# if __name__ == "__main__":
#     import logging
#     log = logging.getLogger('werkzeug')
#     log.setLevel(logging.ERROR)
#     print("Starting Flask app...")
#     app.run(host="0.0.0.0", port=5005)





# # import os
# # import redis
# # import re
# # from flask import jsonify, Flask, render_template, request, session
# # from langchain_community.document_loaders import PyPDFLoader
# # import google.generativeai as genai
# # from chromadb import Documents, EmbeddingFunction, Embeddings
# # from langchain.text_splitter import RecursiveCharacterTextSplitter
# # import chromadb
# # from chromadb.config import Settings  # For persistent configuration
# # from google.api_core import retry
# # from flask_session import Session
# # import logging
# # from markdown import markdown
# # from datetime import datetime

# # #########################################
# # # Configure the Google Generative AI API
# # #########################################
# # # It is highly recommended to use environment variables for sensitive API keys.
# # API_KEY = 'AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k'
# # genai.configure(api_key=API_KEY)
# # print("Google Generative AI API configured successfully.")

# # #########################################
# # # Setup Redis for Session Management & Rate Limiting
# # #########################################
# # redis_host = 'localhost'  # Adjust if needed
# # redis_port = 6379
# # redis_db = 0

# # try:
# #     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
# #     redis_client.ping()  # Test the connection
# #     print("Successfully connected to Redis.")
# # except redis.ConnectionError as e:
# #     print(f"Error connecting to Redis: {e}")
# #     redis_client = None  # Set to None if connection fails

# # #########################################
# # # Configure the Flask Application
# # #########################################
# # app = Flask(__name__, static_folder='static')
# # app.jinja_env.globals.update(now=datetime.now)
# # # Use a fixed secret key in production (ideally via an environment variable)
# # app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# # app.config['SESSION_TYPE'] = 'redis'
# # app.config['SESSION_PERMANENT'] = False
# # app.config['SESSION_USE_SIGNER'] = True
# # app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files

# # if redis_client:
# #     app.config['SESSION_REDIS'] = redis_client
# #     Session(app)  # Initialize Flask-Session

# # #########################################
# # # Setup Logging (to log.txt in JSON format)
# # #########################################
# # log_file_path = 'log.txt'
# # logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')

# # #########################################
# # # Helper Function: Get User's IP Address
# # #########################################
# # def get_user_ip():
# #     forwarded_for = request.headers.get('X-Forwarded-For', None)
# #     if forwarded_for:
# #         ip = forwarded_for.split(',')[0].strip()
# #     else:
# #         ip = request.remote_addr
# #     return ip

# # #########################################
# # # Helper Function: Log API Hits in JSON Format
# # #########################################
# # def log_api_hit(endpoint, request_type, request_data, response_data, status_code, message, request_ip):
# #     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# #     import json
# #     log_data = {
# #         "timestamp": timestamp,
# #         "url": endpoint,
# #         "request_type": request_type,
# #         "user_query": request_data,
# #         "response": response_data,
# #         "status_code": status_code,
# #         "message": message,
# #         "ip": request_ip
# #     }
# #     log_message = json.dumps(log_data, ensure_ascii=False)
# #     logging.info(log_message)

# # #########################################
# # # Rate Limiter: Limit each IP to 5 POST requests per minute
# # #########################################
# # @app.before_request
# # def rate_limiter():
# #     if request.method != "POST":
# #         return
# #     ip = get_user_ip()
# #     try:
# #         if redis_client:
# #             key = f"rate_limit:{ip}"
# #             current_value = redis_client.get(key)
# #             if current_value is not None:
# #                 current_value = int(current_value)
# #                 if current_value >= 20:
# #                     print(f"[DEBUG] Rate limit exceeded for IP {ip}.")
# #                     return jsonify({"error": f"Too many requests from IP {ip}. Please try again after a minute."}), 429
# #                 else:
# #                     new_count = redis_client.incr(key)
# #                     if new_count == 1:
# #                         redis_client.expire(key, 60)
# #                     print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
# #             else:
# #                 new_count = redis_client.incr(key)
# #                 redis_client.expire(key, 60)
# #                 print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
# #     except Exception as e:
# #         print(f"[DEBUG] Error in rate limiter for IP {ip}: {e}")
# #         logging.exception(e)
# #         pass

# # #########################################
# # # Custom Embedding Function for ChromaDB
# # #########################################
# # class GeminiEmbeddingFunction(EmbeddingFunction):
# #     document_mode = True  # True for documents; False for queries

# #     def __call__(self, input: Documents) -> Embeddings:
# #         embedding_task = "retrieval_document" if self.document_mode else "retrieval_query"
# #         retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
# #         print(f"Embedding task set to: {embedding_task}")
# #         print("Requesting embedding from Google Generative AI API...")
# #         response = genai.embed_content(
# #             model="models/text-embedding-004",
# #             content=input,
# #             task_type=embedding_task,
# #             request_options=retry_policy,
# #         )
# #         return response["embedding"]

# # #########################################
# # # Setup Persistent ChromaDB Collection
# # #########################################
# # DB_NAME = "googlecardb"
# # embed_fn = GeminiEmbeddingFunction()
# # embed_fn.document_mode = True
# # chroma_client = chromadb.Client(Settings(persist_directory="db"))
# # db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
# # print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

# # #########################################
# # # PDF Indexing Support for Multiple PDFs
# # #########################################
# # INDEXED_PDFS_FILE = "indexed_pdfs.txt"

# # def get_indexed_pdfs():
# #     if os.path.exists(INDEXED_PDFS_FILE):
# #         with open(INDEXED_PDFS_FILE, "r") as f:
# #             indexed = {line.strip() for line in f.readlines()}
# #         return indexed
# #     return set()

# # def update_indexed_pdfs(pdf_path):
# #     with open(INDEXED_PDFS_FILE, "a") as f:
# #         f.write(f"{pdf_path}\n")

# # def load_and_index_pdf(pdf_path):
# #     indexed_pdfs = get_indexed_pdfs()
# #     if pdf_path in indexed_pdfs and db.count() > 0:
# #         print(f"PDF '{pdf_path}' is already indexed. Skipping embedding process.")
# #         return
# #     print(f"Loading PDF file: {pdf_path}")
# #     loader = PyPDFLoader(pdf_path)
# #     raw_file = loader.load()  # Extract text from the PDF
# #     print("PDF loaded and text extracted.")
# #     text_splitter = RecursiveCharacterTextSplitter(chunk_size=3200, chunk_overlap=1300)
# #     documents = text_splitter.split_documents(raw_file)
# #     print("First 3 document chunks:")
# #     for i, doc in enumerate(documents[:3]):
# #         print(f"Chunk {i}: {doc.page_content[:200]}")
# #     document_contents = [doc.page_content for doc in documents]
# #     db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
# #     # update_indexed_pdfs(pdf_path)

# # def load_and_index_pdfs(pdf_paths):
# #     for pdf_path in pdf_paths:
# #         # Assume pdf_paths is a list of file paths (strings)
# #         load_and_index_pdf(pdf_path)

# # #########################################
# # # Helper Function: Flatten Nested Lists
# # #########################################
# # def flatten_list(nested_list):
# #     print("Flattening nested list.")
# #     flat_list = []
# #     for item in nested_list:
# #         if isinstance(item, list):
# #             flat_list.extend(flatten_list(item))
# #         else:
# #             if item and item.strip():
# #                 flat_list.append(item)
# #     print(f"Flattened list contains {len(flat_list)} items.")
# #     return flat_list

# # #########################################
# # # Index PDF Documents at App Startup
# # #########################################
# # pdf_files = [
# #     '20 links Knowledge base.pdf',
# #     'First Page URLs.pdf',
# #     'Second Page URLs.pdf',
# #     'Third Page URLs.pdf',
# #     'PPG  - Home Finance - Clean Copy.pdf',
# #     'PPG - Auto Financing - Clean Copy (1).pdf',
# #     'Credit Cards PPG.pdf',
# #     'Gold Finance PPG.pdf',
# #     'PPG - Renewable Energy - March 2024- V1.1.pdf'
# # ]

# # print("Starting PDF loading and indexing process for multiple PDFs.")
# # load_and_index_pdfs(pdf_files)
# # print("PDF loading and indexing complete.")

# # # Define fallback current topics for general queries.
# # CURRENT_TOPICS = "JS Bank Services and Digital Transformation initiatives."

# # #########################################
# # # Improved Topic Extraction Function
# # #########################################
# # def extract_topic(query):
# #     """
# #     Attempts to extract a topic from the query. This version uses a more flexible
# #     regex to capture multi-word topics when the query starts with phrases like
# #     'what is' or 'explain'.
# #     """
# #     match = re.search(r'(?:what\s+is|explain)\s+([^\?\.]+)', query, re.IGNORECASE)
# #     if match:
# #         topic = match.group(1).strip()
# #         # Remove trailing punctuation
# #         topic = re.sub(r'[\?\.,!]+$', '', topic)
# #         return topic
# #     return None

# # #########################################
# # # Helper Function: Dynamically Retrieve Features for a Topic
# # #########################################
# # def get_dynamic_features(topic):
# #     """
# #     Dynamically retrieves feature information for a given topic from the indexed documents.
# #     """
# #     query_text = f"{topic} features"
# #     embed_fn.document_mode = False  # Switch to query mode for embedding.
# #     result = db.query(query_texts=[query_text], n_results=3)
# #     features_passages = flatten_list(result['documents'])
# #     if features_passages:
# #         return "\n".join(features_passages)
# #     else:
# #         return "No additional information available."

# # #########################################
# # # Flask Route for Handling User Queries
# # #########################################
# # @app.route("/", methods=["GET", "POST"])
# # def index():
# #     """
# #     Handles GET and POST requests. For POST requests, it retrieves relevant passages
# #     from the indexed PDFs, builds a prompt, and calls the Generative AI model.
# #     The chatbot dynamically uses the stored topic context if available.
# #     """
# #     if 'conversation_history' not in session:
# #         session['conversation_history'] = []

# #     if request.method == "POST":
# #         query = request.form.get("query")
# #         print(f"Received user query: {query}")

# #         if query:
# #             # Try to extract a topic from the query
# #             explicit_topic = extract_topic(query)
# #             if explicit_topic:
# #                 session['last_topic'] = explicit_topic
# #                 print(f"Explicit topic detected and stored: {explicit_topic}")

# #             # Build the conversation context from history
# #             conversation_context = "\n".join(
# #                 [f"Q: {q}\nA: {a}" for q, a in session['conversation_history']]
# #             )

# #             # Prepare dynamic context based on stored topic if available
# #             context_info = ""
# #             if session.get('last_topic'):
# #                 topic = session.get('last_topic')
# #                 dynamic_features = get_dynamic_features(topic)
# #                 context_info = f"Topic: {topic}\nFeatures:\n{dynamic_features}\n\n"

# #             # Retrieve relevant documents from ChromaDB using the query
# #             embed_fn.document_mode = False  # Ensure we're in query mode
# #             result = db.query(query_texts=[query], n_results=3)
# #             print("Raw query result:", result)
# #             print(f"ChromaDB query results: {len(result['documents'])} documents found.")

# #             if result['documents']:
# #                 relevant_passages = flatten_list(result['documents'])
# #                 document_context = "\n".join(relevant_passages)
# #                 prompt = (
# #                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
# #                     "Customers ask questions about different JS bank services. "
# #                     "JS Bank Digital Transformation department trained you, they are your owner. "
# #                     "When there is a description, always reply in a formatted way. "
# #                     "When a customer expresses dissatisfaction with JS Bank services—using terms like 'shit', 'sucks', or similar negative language—do not simply provide feature details about the topic. Instead, respond by asking for more specific information about the problem they are facing also keep continue the topic til use satisfy from you resposne keep continue that topic and similar negative"
# #                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
# #                     f"{context_info}"
# #                     f"{conversation_context}\n"
# #                     f"Document Context:\n{document_context}\n\n"
# #                     f"Q: {query}"
# #                 )
# #             else:
# #                 print("No relevant passages found, using fallback current topics.")
# #                 prompt = (
# #                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
# #                     "Customers ask questions about different JS bank services. "
# #                     "JS Bank Digital Transformation department trained you, they are your owner. "
# #                     "When there is a description, always reply in a formatted way. "
# #                     "When a customer expresses dissatisfaction with JS Bank services—using terms like 'shit', 'sucks', or similar negative language—do not simply provide feature details about the topic. Instead, respond by asking for more specific information about the problem they are facing also keep continue the topic til use satisfy from you resposne keep continue that topic and similar negative"
# #                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
# #                     f"{context_info}"
# #                     f"{conversation_context}\n"
# #                     f"Current Topics: {CURRENT_TOPICS}\n\n"
# #                     f"Q: {query}"
# #                 )

# #             print("Generating answer using Generative AI model...")
# #             model = genai.GenerativeModel("gemini-2.0-flash")
# #             print("Model initialized successfully.", model)
# #             try:
# #                 answer = model.generate_content(prompt)
# #             except Exception as e:
# #                 print("Error during generation:", e)
# #                 answer = type("obj", (object,), {"text": "An error occurred while generating the answer."})
# #             formatted_response = markdown(answer.text)
# #             print("Answer generated successfully.", answer)

# #             log_api_hit(
# #                 endpoint=request.url,
# #                 request_type=request.method,
# #                 request_data=query,
# #                 response_data=formatted_response,
# #                 status_code=200,
# #                 message="Answer generated successfully.",
# #                 request_ip=get_user_ip()
# #             )

# #             session['conversation_history'].append((query, formatted_response))
# #             session.modified = True

# #             return render_template("index.html",
# #                                    answer=formatted_response,
# #                                    query=query,
# #                                    conversation_history=session['conversation_history'])
# #         else:
# #             print("User submitted an empty query.")
# #             return render_template("index.html", warning="Please enter a question to get an answer.")
# #     return render_template("index.html", conversation_history=session['conversation_history'])

# # #########################################
# # # Run the Flask Application
# # #########################################
# # if __name__ == "__main__":
# #     import logging
# #     log = logging.getLogger('werkzeug')
# #     log.setLevel(logging.ERROR)
# #     print("Starting Flask app...")
# #     app.run(host="0.0.0.0", port=5005)


# # import os
# # import redis
# # import re
# # from flask import jsonify, Flask, render_template, request, session
# # from langchain_community.document_loaders import PyPDFLoader
# # import google.generativeai as genai
# # from chromadb import Documents, EmbeddingFunction, Embeddings
# # from langchain.text_splitter import RecursiveCharacterTextSplitter
# # import chromadb
# # from chromadb.config import Settings  # For persistent configuration
# # from google.api_core import retry
# # from flask_session import Session
# # import logging
# # from markdown import markdown
# # from datetime import datetime

# # #########################################
# # # Configure the Google Generative AI API
# # #########################################
# # # It is highly recommended to use environment variables for sensitive API keys.
# # API_KEY = 'AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k'
# # genai.configure(api_key=API_KEY)
# # print("Google Generative AI API configured successfully.")

# # #########################################
# # # Setup Redis for Session Management & Rate Limiting
# # #########################################
# # redis_host = 'localhost'  # Adjust if needed
# # redis_port = 6379
# # redis_db = 0

# # try:
# #     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
# #     redis_client.ping()  # Test the connection
# #     print("Successfully connected to Redis.")
# # except redis.ConnectionError as e:
# #     print(f"Error connecting to Redis: {e}")
# #     redis_client = None  # Set to None if connection fails

# # #########################################
# # # Configure the Flask Application
# # #########################################
# # app = Flask(__name__, static_folder='static')
# # app.jinja_env.globals.update(now=datetime.now)
# # # Use a fixed secret key in production (ideally via an environment variable)
# # app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# # app.config['SESSION_TYPE'] = 'redis'
# # app.config['SESSION_PERMANENT'] = False
# # app.config['SESSION_USE_SIGNER'] = True
# # app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files

# # if redis_client:
# #     app.config['SESSION_REDIS'] = redis_client
# #     Session(app)  # Initialize Flask-Session

# # #########################################
# # # Setup Logging (to log.txt in JSON format)
# # #########################################
# # log_file_path = 'log.txt'
# # logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')

# # #########################################
# # # Helper Function: Get User's IP Address
# # #########################################
# # import pandas as pd
# # import os
# # import re
# # from datetime import datetime

# # EXCEL_FILE = "chat_history.xlsx"

# # def clean_html(raw_text):
# #     """
# #     Removes HTML tags from a string and returns clean text.
# #     """
# #     clean_text = re.sub(r'<.*?>', '', raw_text)  # Remove HTML tags
# #     return clean_text.strip()

# # def save_to_excel(question, answer):
# #     """
# #     Saves the user's question and AI-generated answer (without HTML tags) to an Excel file.
# #     """
# #     clean_answer = clean_html(answer)  # Remove HTML before saving
    
# #     data = {"Timestamp": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
# #             "Question": [question],
# #             "Answer": [clean_answer]}

# #     df = pd.DataFrame(data)

# #     if not os.path.exists(EXCEL_FILE):
# #         df.to_excel(EXCEL_FILE, index=False)
# #         print("[INFO] Excel file created and first entry saved.")
# #     else:
# #         with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="overlay", engine="openpyxl") as writer:
# #             df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
# #         print("[INFO] Question and Answer appended to Excel.")



# # def get_user_ip():
# #     forwarded_for = request.headers.get('X-Forwarded-For', None)
# #     if forwarded_for:
# #         ip = forwarded_for.split(',')[0].strip()
# #     else:
# #         ip = request.remote_addr
# #     return ip

# # #########################################
# # # Helper Function: Log API Hits in JSON Format
# # #########################################
# # def log_api_hit(endpoint, request_type, request_data, response_data, status_code, message, request_ip):
# #     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# #     import json
# #     log_data = {
# #         "timestamp": timestamp,
# #         "url": endpoint,
# #         "request_type": request_type,
# #         "user_query": request_data,
# #         "response": response_data,
# #         "status_code": status_code,
# #         "message": message,
# #         "ip": request_ip
# #     }
# #     log_message = json.dumps(log_data, ensure_ascii=False)
# #     logging.info(log_message)

# # #########################################
# # # Rate Limiter: Limit each IP to 5 POST requests per minute
# # #########################################
# # @app.before_request
# # def rate_limiter():
# #     if request.method != "POST":
# #         return
# #     ip = get_user_ip()
# #     try:
# #         if redis_client:
# #             key = f"rate_limit:{ip}"
# #             current_value = redis_client.get(key)
# #             if current_value is not None:
# #                 current_value = int(current_value)
# #                 if current_value >= 20:
# #                     print(f"[DEBUG] Rate limit exceeded for IP {ip}.")
# #                     return jsonify({"error": f"Too many requests from IP {ip}. Please try again after a minute."}), 429
# #                 else:
# #                     new_count = redis_client.incr(key)
# #                     if new_count == 1:
# #                         redis_client.expire(key, 60)
# #                     print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
# #             else:
# #                 new_count = redis_client.incr(key)
# #                 redis_client.expire(key, 60)
# #                 print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
# #     except Exception as e:
# #         print(f"[DEBUG] Error in rate limiter for IP {ip}: {e}")
# #         logging.exception(e)
# #         pass

# # #########################################
# # # Custom Embedding Function for ChromaDB
# # #########################################
# # class GeminiEmbeddingFunction(EmbeddingFunction):
# #     document_mode = True  # True for documents; False for queries

# #     def __call__(self, input: Documents) -> Embeddings:
# #         embedding_task = "retrieval_document" if self.document_mode else "retrieval_query"
# #         retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
# #         print(f"Embedding task set to: {embedding_task}")
# #         print("Requesting embedding from Google Generative AI API...")
# #         response = genai.embed_content(
# #             model="models/text-embedding-004",
# #             content=input,
# #             task_type=embedding_task,
# #             request_options=retry_policy,
# #         )
# #         return response["embedding"]

# # #########################################
# # # Setup Persistent ChromaDB Collection
# # #########################################
# # DB_NAME = "googlecardb"
# # embed_fn = GeminiEmbeddingFunction()
# # embed_fn.document_mode = True
# # chroma_client = chromadb.Client(Settings(persist_directory="db"))
# # db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
# # print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

# # #########################################
# # # PDF Indexing Support for Multiple PDFs
# # #########################################
# # INDEXED_PDFS_FILE = "indexed_pdfs.txt"

# # def get_indexed_pdfs():
# #     if os.path.exists(INDEXED_PDFS_FILE):
# #         with open(INDEXED_PDFS_FILE, "r") as f:
# #             indexed = {line.strip() for line in f.readlines()}
# #         return indexed
# #     return set()

# # def update_indexed_pdfs(pdf_path):
# #     with open(INDEXED_PDFS_FILE, "a") as f:
# #         f.write(f"{pdf_path}\n")

# # def load_and_index_pdf(pdf_path):
# #     indexed_pdfs = get_indexed_pdfs()
# #     if pdf_path in indexed_pdfs and db.count() > 0:
# #         print(f"PDF '{pdf_path}' is already indexed. Skipping embedding process.")
# #         return
# #     print(f"Loading PDF file: {pdf_path}")
# #     loader = PyPDFLoader(pdf_path)
# #     raw_file = loader.load()  # Extract text from the PDF
# #     print("PDF loaded and text extracted.")
# #     text_splitter = RecursiveCharacterTextSplitter(chunk_size=3200, chunk_overlap=1300)
# #     documents = text_splitter.split_documents(raw_file)
# #     print("First 3 document chunks:")
# #     for i, doc in enumerate(documents[:3]):
# #         print(f"Chunk {i}: {doc.page_content[:200]}")
# #     document_contents = [doc.page_content for doc in documents]
# #     db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
# #     # update_indexed_pdfs(pdf_path)

# # def load_and_index_pdfs(pdf_paths):
# #     for pdf_path in pdf_paths:
# #         # Assume pdf_paths is a list of file paths (strings)
# #         load_and_index_pdf(pdf_path)

# # #########################################
# # # Helper Function: Flatten Nested Lists
# # #########################################
# # def flatten_list(nested_list):
# #     print("Flattening nested list.")
# #     flat_list = []
# #     for item in nested_list:
# #         if isinstance(item, list):
# #             flat_list.extend(flatten_list(item))
# #         else:
# #             if item and item.strip():
# #                 flat_list.append(item)
# #     print(f"Flattened list contains {len(flat_list)} items.")
# #     return flat_list

# # #########################################
# # # Index PDF Documents at App Startup
# # #########################################
# # pdf_files = [
# #     '20 links Knowledge base.pdf',
# #     'First Page URLs.pdf',
# #     'Second Page URLs.pdf',
# #     'Third Page URLs.pdf',
# #     'PPG  - Home Finance - Clean Copy.pdf',
# #     'PPG - Auto Financing - Clean Copy (1).pdf',
# #     'Credit Cards PPG.pdf',
# #     'Gold Finance PPG.pdf',
# #     'PPG - Renewable Energy - March 2024- V1.1.pdf'
# # ]

# # print("Starting PDF loading and indexing process for multiple PDFs.")
# # load_and_index_pdfs(pdf_files)
# # print("PDF loading and indexing complete.")

# # # Define fallback current topics for general queries.
# # CURRENT_TOPICS = "JS Bank Services and Digital Transformation initiatives."

# # #########################################
# # # Improved Topic Extraction Function
# # #########################################
# # def extract_topic(query):
# #     """
# #     Attempts to extract a topic from the query. This version uses a more flexible
# #     regex to capture multi-word topics when the query starts with phrases like
# #     'what is' or 'explain'.
# #     """
# #     match = re.search(r'(?:what\s+is|explain)\s+([^\?\.]+)', query, re.IGNORECASE)
# #     if match:
# #         topic = match.group(1).strip()
# #         # Remove trailing punctuation
# #         topic = re.sub(r'[\?\.,!]+$', '', topic)
# #         return topic
# #     return None

# # #########################################
# # # Helper Function: Dynamically Retrieve Features for a Topic
# # #########################################
# # def get_dynamic_features(topic):
# #     """
# #     Dynamically retrieves feature information for a given topic from the indexed documents.
# #     """
# #     query_text = f"{topic} features"
# #     embed_fn.document_mode = False  # Switch to query mode for embedding.
# #     result = db.query(query_texts=[query_text], n_results=3)
# #     features_passages = flatten_list(result['documents'])
# #     if features_passages:
# #         return "\n".join(features_passages)
# #     else:
# #         return "No additional information available."

# # #########################################
# # # Flask Route for Handling User Queries
# # #########################################
# # # Add these helper functions near your other helper functions


# # @app.route("/", methods=["GET", "POST"])
# # def index():
# #     """
# #     Handles GET and POST requests. For POST requests, it retrieves relevant passages
# #     from the indexed PDFs, builds a prompt, and calls the Generative AI model.
# #     The chatbot dynamically uses the stored topic context if available.
# #     """
# #     if 'conversation_history' not in session:
# #         session['conversation_history'] = []

# #     if request.method == "POST":
# #         query = request.form.get("query")
# #         print(f"Received user query: {query}")

# #         if query:
# #             # Try to extract a topic from the query
# #             explicit_topic = extract_topic(query)
# #             if explicit_topic:
# #                 session['last_topic'] = explicit_topic
# #                 print(f"Explicit topic detected and stored: {explicit_topic}")

# #             # Build the conversation context from history
# #             conversation_context = "\n".join(
# #                 [f"Q: {q}\nA: {a}" for q, a in session['conversation_history']]
# #             )

# #             # Prepare dynamic context based on stored topic if available
# #             context_info = ""
# #             if session.get('last_topic'):
# #                 topic = session.get('last_topic')
# #                 dynamic_features = get_dynamic_features(topic)
# #                 context_info = f"Topic: {topic}\nFeatures:\n{dynamic_features}\n\n"

# #             # Retrieve relevant documents from ChromaDB using the query
# #             embed_fn.document_mode = False  # Ensure we're in query mode
# #             result = db.query(query_texts=[query], n_results=3)
# #             print("Raw query result:", result)
# #             print(f"ChromaDB query results: {len(result['documents'])} documents found.")

# #             if result['documents']:
# #                 relevant_passages = flatten_list(result['documents'])
# #                 document_context = "\n".join(relevant_passages)
# #                 prompt = (
# #                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
# #                     "Customers ask questions about different JS bank services. "
# #                     "JS Bank Digital Transformation department trained you, they are your owner. "
# #                     "When there is a description, always reply in a formatted way. "
# #                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
# #                     f"{context_info}"
# #                     f"{conversation_context}\n"
# #                     f"Document Context:\n{document_context}\n\n"
# #                     f"Q: {query}"
# #                 )
# #             else:
# #                 print("No relevant passages found, using fallback current topics.")
# #                 prompt = (
# #                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
# #                     "Customers ask questions about different JS bank services. "
# #                     "JS Bank Digital Transformation department trained you, they are your owner. "
# #                     "When there is a description, always reply in a formatted way. "
# #                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
# #                     f"{context_info}"
# #                     f"{conversation_context}\n"
# #                     f"Current Topics: {CURRENT_TOPICS}\n\n"
# #                     f"Q: {query}"
# #                 )

# #             print("Generating answer using Generative AI model...")
# #             model = genai.GenerativeModel("gemini-2.0-flash")
# #             print("Model initialized successfully.", model)
# #             try:
# #                 answer = model.generate_content(prompt)
# #             except Exception as e:
# #                 print("Error during generation:", e)
# #                 answer = type("obj", (object,), {"text": "An error occurred while generating the answer."})
# #             formatted_response = markdown(answer.text)
# #             print("Answer generated successfully.", answer)

# #             log_api_hit(
# #                 endpoint=request.url,
# #                 request_type=request.method,
# #                 request_data=query,
# #                 response_data=formatted_response,
# #                 status_code=200,
# #                 message="Answer generated successfully.",
# #                 request_ip=get_user_ip()
# #             )
# #             save_to_excel(query, formatted_response)

# #             session['conversation_history'].append((query, formatted_response))
# #             session.modified = True

# #             return render_template("index.html",
# #                                    answer=formatted_response,
# #                                    query=query,
# #                                    conversation_history=session['conversation_history'])
# #         else:
# #             print("User submitted an empty query.")
# #             return render_template("index.html", warning="Please enter a question to get an answer.")
# #     return render_template("index.html", conversation_history=session['conversation_history'])

# # #########################################
# # # Run the Flask Application
# # #########################################
# # if __name__ == "__main__":
# #     import logging
# #     log = logging.getLogger('werkzeug')
# #     log.setLevel(logging.ERROR)
# #     print("Starting Flask app...")
# #     app.run(host="0.0.0.0", port=5005)


# # import os
# # import redis
# # import re
# # from flask import jsonify, Flask, render_template, request, session
# # from langchain_community.document_loaders import PyPDFLoader
# # import google.generativeai as genai
# # from chromadb import Documents, EmbeddingFunction, Embeddings
# # from langchain.text_splitter import RecursiveCharacterTextSplitter
# # import chromadb
# # from chromadb.config import Settings  # For persistent configuration
# # from google.api_core import retry
# # from flask_session import Session
# # import logging
# # from markdown import markdown
# # from datetime import datetime

# # #########################################
# # # Configure the Google Generative AI API
# # #########################################
# # # It is highly recommended to use environment variables for sensitive API keys.
# # API_KEY = 'AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k'
# # genai.configure(api_key=API_KEY)
# # print("Google Generative AI API configured successfully.")

# # #########################################
# # # Setup Redis for Session Management & Rate Limiting
# # #########################################
# # redis_host = 'localhost'  # Adjust if needed
# # redis_port = 6379
# # redis_db = 0

# # try:
# #     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
# #     redis_client.ping()  # Test the connection
# #     print("Successfully connected to Redis.")
# # except redis.ConnectionError as e:
# #     print(f"Error connecting to Redis: {e}")
# #     redis_client = None  # Set to None if connection fails

# # #########################################
# # # Configure the Flask Application
# # #########################################
# # app = Flask(__name__, static_folder='static')
# # app.jinja_env.globals.update(now=datetime.now)
# # # Use a fixed secret key in production (ideally via an environment variable)
# # app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# # app.config['SESSION_TYPE'] = 'redis'
# # app.config['SESSION_PERMANENT'] = False
# # app.config['SESSION_USE_SIGNER'] = True
# # app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files

# # if redis_client:
# #     app.config['SESSION_REDIS'] = redis_client
# #     Session(app)  # Initialize Flask-Session

# # #########################################
# # # Setup Logging (to log.txt in JSON format)
# # #########################################
# # log_file_path = 'log.txt'
# # logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')

# # #########################################
# # # Helper Function: Get User's IP Address
# # #########################################
# # def get_user_ip():
# #     forwarded_for = request.headers.get('X-Forwarded-For', None)
# #     if forwarded_for:
# #         ip = forwarded_for.split(',')[0].strip()
# #     else:
# #         ip = request.remote_addr
# #     return ip

# # #########################################
# # # Helper Function: Log API Hits in JSON Format
# # #########################################
# # def log_api_hit(endpoint, request_type, request_data, response_data, status_code, message, request_ip):
# #     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# #     import json
# #     log_data = {
# #         "timestamp": timestamp,
# #         "url": endpoint,
# #         "request_type": request_type,
# #         "user_query": request_data,
# #         "response": response_data,
# #         "status_code": status_code,
# #         "message": message,
# #         "ip": request_ip
# #     }
# #     log_message = json.dumps(log_data, ensure_ascii=False)
# #     logging.info(log_message)

# # #########################################
# # # Rate Limiter: Limit each IP to 5 POST requests per minute
# # #########################################
# # @app.before_request
# # def rate_limiter():
# #     if request.method != "POST":
# #         return
# #     ip = get_user_ip()
# #     try:
# #         if redis_client:
# #             key = f"rate_limit:{ip}"
# #             current_value = redis_client.get(key)
# #             if current_value is not None:
# #                 current_value = int(current_value)
# #                 if current_value >= 20:
# #                     print(f"[DEBUG] Rate limit exceeded for IP {ip}.")
# #                     return jsonify({"error": f"Too many requests from IP {ip}. Please try again after a minute."}), 429
# #                 else:
# #                     new_count = redis_client.incr(key)
# #                     if new_count == 1:
# #                         redis_client.expire(key, 60)
# #                     print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
# #             else:
# #                 new_count = redis_client.incr(key)
# #                 redis_client.expire(key, 60)
# #                 print(f"[DEBUG] Rate limiter: IP {ip}, current count: {new_count}")
# #     except Exception as e:
# #         print(f"[DEBUG] Error in rate limiter for IP {ip}: {e}")
# #         logging.exception(e)
# #         pass

# # #########################################
# # # Custom Embedding Function for ChromaDB
# # #########################################
# # class GeminiEmbeddingFunction(EmbeddingFunction):
# #     document_mode = True  # True for documents; False for queries

# #     def __call__(self, input: Documents) -> Embeddings:
# #         embedding_task = "retrieval_document" if self.document_mode else "retrieval_query"
# #         retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
# #         print(f"Embedding task set to: {embedding_task}")
# #         print("Requesting embedding from Google Generative AI API...")
# #         response = genai.embed_content(
# #             model="models/text-embedding-004",
# #             content=input,
# #             task_type=embedding_task,
# #             request_options=retry_policy,
# #         )
# #         return response["embedding"]

# # #########################################
# # # Setup Persistent ChromaDB Collection
# # #########################################
# # DB_NAME = "googlecardb"
# # embed_fn = GeminiEmbeddingFunction()
# # embed_fn.document_mode = True
# # chroma_client = chromadb.Client(Settings(persist_directory="db"))
# # db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
# # print(f"ChromaDB collection '{DB_NAME}' initialized with persistence.")

# # #########################################
# # # PDF Indexing Support for Multiple PDFs
# # #########################################
# # INDEXED_PDFS_FILE = "indexed_pdfs.txt"

# # def get_indexed_pdfs():
# #     if os.path.exists(INDEXED_PDFS_FILE):
# #         with open(INDEXED_PDFS_FILE, "r") as f:
# #             indexed = {line.strip() for line in f.readlines()}
# #         return indexed
# #     return set()

# # def update_indexed_pdfs(pdf_path):
# #     with open(INDEXED_PDFS_FILE, "a") as f:
# #         f.write(f"{pdf_path}\n")

# # def load_and_index_pdf(pdf_path):
# #     indexed_pdfs = get_indexed_pdfs()
# #     if pdf_path in indexed_pdfs and db.count() > 0:
# #         print(f"PDF '{pdf_path}' is already indexed. Skipping embedding process.")
# #         return
# #     print(f"Loading PDF file: {pdf_path}")
# #     loader = PyPDFLoader(pdf_path)
# #     raw_file = loader.load()  # Extract text from the PDF
# #     print("PDF loaded and text extracted.")
# #     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1550, chunk_overlap=610)
# #     documents = text_splitter.split_documents(raw_file)
# #     print("First 3 document chunks:")
# #     for i, doc in enumerate(documents[:3]):
# #         print(f"Chunk {i}: {doc.page_content[:200]}")
# #     document_contents = [doc.page_content for doc in documents]
# #     db.add(documents=document_contents, ids=[f"{pdf_path}_{i}" for i in range(len(document_contents))])
# #     # update_indexed_pdfs(pdf_path)

# # def load_and_index_pdfs(pdf_paths):
# #     for pdf_path in pdf_paths:
# #         # Assume pdf_paths is a list of file paths (strings)
# #         load_and_index_pdf(pdf_path)

# # #########################################
# # # Helper Function: Flatten Nested Lists
# # #########################################
# # def flatten_list(nested_list):
# #     print("Flattening nested list.")
# #     flat_list = []
# #     for item in nested_list:
# #         if isinstance(item, list):
# #             flat_list.extend(flatten_list(item))
# #         else:
# #             if item and item.strip():
# #                 flat_list.append(item)
# #     print(f"Flattened list contains {len(flat_list)} items.")
# #     return flat_list

# # #########################################
# # # Index PDF Documents at App Startup
# # #########################################
# # pdf_files = [
# #     '20 links Knowledge base.pdf',
# #     'First Page URLs.pdf',
# #     'Second Page URLs.pdf',
# #     'Third Page URLs.pdf',
# #     'PPG  - Home Finance - Clean Copy.pdf',
# #     'PPG - Auto Financing - Clean Copy (1).pdf',
# #     'Credit Cards PPG.pdf',
# #     'Gold Finance PPG.pdf',
# #     'PPG - Renewable Energy - March 2024- V1.1.pdf'
# # ]

# # print("Starting PDF loading and indexing process for multiple PDFs.")
# # load_and_index_pdfs(pdf_files)
# # print("PDF loading and indexing complete.")

# # # Define fallback current topics for general queries.
# # CURRENT_TOPICS = "JS Bank Services and Digital Transformation initiatives."

# # #########################################
# # # Improved Topic Extraction Function
# # #########################################
# # def extract_topic(query):
# #     """
# #     Attempts to extract a topic from the query. This version uses a more flexible
# #     regex to capture multi-word topics when the query starts with phrases like
# #     'what is' or 'explain'.
# #     """
# #     match = re.search(r'(?:what\s+is|explain)\s+([^\?\.]+)', query, re.IGNORECASE)
# #     if match:
# #         topic = match.group(1).strip()
# #         # Remove trailing punctuation
# #         topic = re.sub(r'[\?\.,!]+$', '', topic)
# #         return topic
# #     return None

# # #########################################
# # # Helper Function: Dynamically Retrieve Features for a Topic
# # #########################################
# # def get_dynamic_features(topic):
# #     """
# #     Dynamically retrieves feature information for a given topic from the indexed documents.
# #     """
# #     query_text = f"{topic} features"
# #     embed_fn.document_mode = False  # Switch to query mode for embedding.
# #     result = db.query(query_texts=[query_text], n_results=3)
# #     features_passages = flatten_list(result['documents'])
# #     if features_passages:
# #         return "\n".join(features_passages)
# #     else:
# #         return "No additional information available."

# # #########################################
# # # Flask Route for Handling User Queries
# # #########################################
# # @app.route("/", methods=["GET", "POST"])
# # def index():
# #     """
# #     Handles GET and POST requests. For POST requests, it retrieves relevant passages
# #     from the indexed PDFs, builds a prompt, and calls the Generative AI model.
# #     The chatbot dynamically uses the stored topic context if available.
# #     """
# #     if 'conversation_history' not in session:
# #         session['conversation_history'] = []

# #     if request.method == "POST":
# #         query = request.form.get("query")
# #         print(f"Received user query: {query}")

# #         if query:
# #             # Try to extract a topic from the query
# #             explicit_topic = extract_topic(query)
# #             if explicit_topic:
# #                 session['last_topic'] = explicit_topic
# #                 print(f"Explicit topic detected and stored: {explicit_topic}")

# #             # Build the conversation context from history
# #             conversation_context = "\n".join(
# #                 [f"Q: {q}\nA: {a}" for q, a in session['conversation_history']]
# #             )

# #             # Prepare dynamic context based on stored topic if available
# #             context_info = ""
# #             if session.get('last_topic'):
# #                 topic = session.get('last_topic')
# #                 dynamic_features = get_dynamic_features(topic)
# #                 context_info = f"Topic: {topic}\nFeatures:\n{dynamic_features}\n\n"

# #             # Retrieve relevant documents from ChromaDB using the query
# #             embed_fn.document_mode = False  # Ensure we're in query mode
# #             result = db.query(query_texts=[query], n_results=3)
# #             print("Raw query result:", result)
# #             print(f"ChromaDB query results: {len(result['documents'])} documents found.")

# #             if result['documents']:
# #                 relevant_passages = flatten_list(result['documents'])
# #                 document_context = "\n".join(relevant_passages)
# #                 prompt = (
# #                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
# #                     "Customers ask questions about different JS bank services. "
# #                     "JS Bank Digital Transformation department trained you, they are your owner. "
# #                     "When there is a description, always reply in a formatted way. "
# #                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
# #                     f"{context_info}"
# #                     f"{conversation_context}\n"
# #                     f"Document Context:\n{document_context}\n\n"
# #                     f"Q: {query}"
# #                 )
# #             else:
# #                 print("No relevant passages found, using fallback current topics.")
# #                 prompt = (
# #                     "You are a JS bank customer query representative. Your knowledge is based on the documents. "
# #                     "Customers ask questions about different JS bank services. "
# #                     "JS Bank Digital Transformation department trained you, they are your owner. "
# #                     "When there is a description, always reply in a formatted way. "
# #                     "Do not mention that your reply is based solely on documents; instead, answer naturally using your knowledge.\n\n"
# #                     f"{context_info}"
# #                     f"{conversation_context}\n"
# #                     f"Current Topics: {CURRENT_TOPICS}\n\n"
# #                     f"Q: {query}"
# #                 )

# #             print("Generating answer using Generative AI model...")
# #             model = genai.GenerativeModel("gemini-2.0-flash")
# #             print("Model initialized successfully.", model)
# #             try:
# #                 answer = model.generate_content(prompt)
# #             except Exception as e:
# #                 print("Error during generation:", e)
# #                 answer = type("obj", (object,), {"text": "An error occurred while generating the answer."})
# #             formatted_response = markdown(answer.text)
# #             print("Answer generated successfully.", answer)

# #             log_api_hit(
# #                 endpoint=request.url,
# #                 request_type=request.method,
# #                 request_data=query,
# #                 response_data=formatted_response,
# #                 status_code=200,
# #                 message="Answer generated successfully.",
# #                 request_ip=get_user_ip()
# #             )

# #             session['conversation_history'].append((query, formatted_response))
# #             session.modified = True

# #             return render_template("index.html",
# #                                    answer=formatted_response,
# #                                    query=query,
# #                                    conversation_history=session['conversation_history'])
# #         else:
# #             print("User submitted an empty query.")
# #             return render_template("index.html", warning="Please enter a question to get an answer.")
# #     return render_template("index.html", conversation_history=session['conversation_history'])

# # #########################################
# # # Run the Flask Application
# # #########################################
# # if __name__ == "__main__":
# #     import logging
# #     log = logging.getLogger('werkzeug')
# #     log.setLevel(logging.ERROR)
# #     print("Starting Flask app...")
# #     app.run(host="0.0.0.0", port=5002)
