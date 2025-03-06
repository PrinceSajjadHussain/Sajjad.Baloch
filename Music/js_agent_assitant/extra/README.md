# Flask Web Application for Question Answering using Generative AI

This Flask application provides a web interface for users to ask questions and receive answers based on the content of indexed PDF documents. It leverages Google Generative AI for natural language processing and ChromaDB for efficient document retrieval.

## Features

- **Question Answering:** Answers user queries based on indexed PDF documents using Google Generative AI.
- **PDF Indexing:** Indexes multiple PDF documents to build a knowledge base.
- **Contextual Understanding:** Uses ChromaDB to find relevant passages from the indexed documents to provide context for the AI model.
- **Conversation History:** Maintains a conversation history to provide more context-aware answers in subsequent turns.
- **Rate Limiting:** Implements rate limiting to prevent abuse, allowing 5 POST requests per minute per IP address using Redis.
- **API Logging:** Logs API requests and responses in JSON format to `log.txt`.
- **Session Management:** Uses Flask sessions to manage conversation history.

## Prerequisites

- Python 3.x
- pip package manager
- Redis (for session management and rate limiting)
- Google Generative AI API Key
- Libraries listed in `requirements.txt`

## Setup

1. **Install Redis:**
   - Ensure Redis server is installed and running on your local machine or accessible.

2. **Set up Google Generative AI API Key:**
   - Obtain an API key from Google Generative AI and set it as an environment variable named `GOOGLE_API_KEY`. Or, you can directly replace `"AIzaSyCqaDGFoeDZXXSCd8bv0JSxPBzQbaxx0-k"` in `app.py` with your actual API key. **Note:** It's recommended to use environment variables for security.

3. **Install Python Dependencies:**
   - Navigate to the application directory in your terminal.
   - Run `pip install -r requirements.txt` to install the required Python libraries.

4. **Run the Flask Application:**
   - In your terminal, from the application directory, run `python app.py`.
   - The application will start running on `http://0.0.0.0:5001/`.

## Usage

1. Open your web browser and go to `http://0.0.0.0:5001/`.
2. You will see a simple web interface with a text input field.
3. Enter your question in the input field and click "Get Answer".
4. The application will process your query, retrieve relevant information from the indexed PDFs, and generate an answer using the Generative AI model.
5. The answer will be displayed on the page, along with the conversation history.

## PDF Documents

The application is configured to index the following PDF documents at startup:

- `20 links Knowledge base.pdf`
- `First Page URLs.pdf`
- `Second Page URLs.pdf`
- `Third Page URLs.pdf`

These files should be present in the same directory as `app.py` for indexing to work correctly.

## Logging

API requests and responses are logged in JSON format in the `log.txt` file. This includes timestamps, request details, response data, status codes, and user IP addresses.

## Rate Limiting

To prevent abuse, the application limits each IP address to 5 POST requests per minute. If this limit is exceeded, the application will return a 429 error.

## Persistent ChromaDB

The ChromaDB database is configured for persistent storage. The database files are stored in the `db` directory in the application root.

## Customization

- **API Key:**  Ensure you have correctly configured the Google Generative AI API key.
- **PDF Files:** You can modify the `pdf_files` list in `app.py` to include different PDF documents for indexing.
- **Prompt:** The prompt used for the Generative AI model can be customized in the `index()` route to adjust the behavior and personality of the chatbot.
- **Chunk Size and Overlap:** The `chunk_size` and `chunk_overlap` in `RecursiveCharacterTextSplitter` can be adjusted to optimize document chunking for better retrieval.
- **Rate Limit:** The rate limit (5 requests per minute) can be adjusted in the `rate_limiter()` function.
- **Redis Configuration:**  Modify `redis_host`, `redis_port`, and `redis_db` variables in `app.py` to match your Redis server configuration.

##  Directory Structure

```
.
├── 20 links Knowledge base.pdf
├── First Page URLs.pdf
├── README.md          // This README file
├── Second Page URLs.pdf
├── Third Page URLs.pdf
├── app.py             // Flask application code
├── db/                // ChromaDB persistent storage directory
├── log.txt            // Log file for API requests
├── requirements.txt   // Python dependencies
├── static/            // Static files (like images)
└── templates/         // HTML templates
    └── index.html     // Main HTML template
