It was coming like a long time ago.
---

# **Flask Application for PDF-Based Customer Query Bot**

This project is a **Flask-based chatbot** that uses **Google Generative AI** to answer customer queries based on a PDF knowledge base. It combines the power of **Google Generative AI API**, **LangChain**, and **ChromaDB** for document embedding and conversational AI.

---

## **Features**

1. **PDF Upload and Indexing**:
   - The app processes a PDF document and indexes its content for efficient retrieval.
2. **Conversational Interface**:
   - Users can interact with a chatbot to get answers to their queries.
3. **Integration with Google Generative AI**:
   - The app generates answers using Google Generative AI's embedding and content generation capabilities.
4. **ChromaDB for Document Storage**:
   - Indexed documents are stored in a vector database for efficient querying.
5. **Session History**:
   - The chatbot maintains a session-based conversation history.

---

## **Architecture**

### **Flow Diagram**

```
User -> Flask App -> PDF Loader -> ChromaDB -> Google Generative AI -> Response to User
```

1. **User Interaction**:
   - Users enter their queries via the web interface.
2. **PDF Processing**:
   - The app loads and splits PDF content for storage.
3. **ChromaDB**:
   - Stores and retrieves document embeddings.
4. **Google Generative AI**:
   - Processes queries and generates conversational responses.

---

## **Step-by-Step Explanation**

### **1. Setup Google Generative AI API**
- API Key is configured at the start of the app:
  ```python
  genai.configure(api_key="YOUR_API_KEY")
  ```

### **2. Custom Embedding Function**
- The `GeminiEmbeddingFunction` class is used to generate embeddings for both documents and queries:
  ```python
  class GeminiEmbeddingFunction(EmbeddingFunction):
      def __call__(self, input: Documents) -> Embeddings:
          response = genai.embed_content(model="models/text-embedding-004", content=input, task_type="retrieval_document")
          return response["embedding"]
  ```

### **3. PDF Loading and Indexing**
- The `load_and_index_pdf` function processes the PDF:
  ```python
  def load_and_index_pdf(pdf_path):
      loader = PyPDFLoader(pdf_path)
      raw_file = loader.load()
      text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
      documents = text_splitter.split_documents(raw_file)
      db.add(documents=[doc.page_content for doc in documents], ids=[str(i) for i in range(len(documents))])
  ```
- **Explanation**:
  - PDF is split into chunks for better indexing and retrieval.
  - Indexed data is stored in ChromaDB.

### **4. Query Handling**
- Queries are processed with ChromaDB:
  ```python
  result = db.query(query_texts=[query], n_results=3)
  context = "\n".join(flatten_list(result['documents']))
  ```
- The context is passed to Google Generative AI for generating responses.

### **5. Chatbot Conversation**
- A conversational prompt is built dynamically:
  ```python
  prompt = f"Document: {context}\n\nQ: {query}"
  answer = model.generate_content(prompt)
  ```
- The response is displayed to the user.

### **6. Flask Web Interface**
- **HTML Templates**:
  - The app uses a template (`index.html`) for user interaction.
- **Routes**:
  - `/` handles user queries.
  - `/clear-history` clears the chat history.

---

## **Code Walkthrough**

### **Main Components**

1. **Initialization**:
   - Google Generative AI and ChromaDB are configured.

2. **PDF Loading**:
   - PDF content is loaded and indexed during app startup.

3. **Embedding Function**:
   - Custom embeddings are generated for documents and queries.

4. **Querying ChromaDB**:
   - Relevant passages are retrieved based on the user's query.

5. **Response Generation**:
   - Google Generative AI generates answers using the context from ChromaDB.

6. **Flask App**:
   - Handles HTTP requests and renders responses.

---

## **Usage**

### **1. Prerequisites**
- Install dependencies:
  ```bash
  pip install flask google-generativeai langchain chromadb
  ```

### **2. Running the App**
- Start the Flask app:
  ```bash
  python app.py
  ```
- Open the app in a browser at `http://localhost:5000`.

### **3. Interacting with the Chatbot**
- Upload a PDF file (already handled in the script as `20 links Knowledge base.pdf`).
- Ask questions related to the PDF content.

---

## **Example Interaction**

### **Input PDF**: 
"20 links Knowledge base.pdf" containing information about JS Bank services.

### **User Query**:
*“What is the process for opening a new account?”*

### **Response**:
*“To open a new account, you need to visit your nearest JS Bank branch with valid ID documents, proof of address, and two passport-size photographs. Our representatives will assist you in completing the required forms.”*

---

## **Folder Structure**

```
project/
├── app.py                # Main Flask application
├── templates/
│   └── index.html        # HTML template for the web interface
├── static/
│   └── styles.css        # Optional CSS for styling
└── 20 links Knowledge base.pdf # Example PDF file
```

---

## **Future Improvements**

1. **Dynamic PDF Uploads**:
   - Allow users to upload their own PDFs during runtime.
2. **Authentication**:
   - Secure access with user login.
3. **Enhanced UI**:
   - Add CSS for better user experience.
4. **Error Handling**:
   - Handle invalid queries and API failures gracefully.

---
