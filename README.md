# DocuChat - AI-Powered PDF Question Answering System

DocuChat is an AI-powered document question-answering application that allows users to upload PDF documents and ask questions about their contents using natural language.

It uses Retrieval-Augmented Generation (RAG) to extract document content, split it into smaller chunks, store vector embeddings, retrieve relevant information, and generate answers using Google's Gemini model.

## Features

- **PDF Upload:** Upload PDF documents through a React interface.
- **Text Extraction:** Extract text from PDF documents using PyPDF.
- **Document Chunking:** Split extracted text into smaller chunks with configurable overlap.
- **Vector Storage:** Store document embeddings and metadata using ChromaDB.
- **AI-Powered Q&A:** Ask natural-language questions about uploaded documents.
- **Source References:** Return source document and page information with answers.
- **Document Isolation:** Assign a unique ID to every upload, allowing separate handling of documents with identical filenames.
- **Document-Specific Retrieval:** Retrieve information from the selected document rather than mixing content across documents.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React.js, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| PDF Processing | PyPDF |
| Text Splitting | LangChain Text Splitters |
| Embeddings | LangChain HuggingFace integration |
| Vector Database | ChromaDB |
| LLM | Google Gemini |
| API Communication | REST API |

## System Architecture

```text
                  USER
                   |
                   v
            React Frontend
                   |
             PDF Upload
                   |
                   v
             FastAPI Backend
                   |
                   v
              PDF Processor
                   |
             Text Extraction
                   |
                   v
             Text Chunking
                   |
                   v
          Embedding Generation
                   |
                   v
               ChromaDB
                   |
              User Question
                   |
                   v
          Document Retrieval
                   |
                   v
           Relevant Context
                   |
                   v
             Gemini LLM
                   |
                   v
          Generated Answer
                   |
                   v
             React Frontend
```

## Project Structure

```text
Docu-Chat/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── document_processor.py
│   │   │   ├── embeddings.py
│   │   │   ├── llm.py
│   │   │   ├── retriever.py
│   │   │   └── vector_store.py
│   │   └── models/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── package-lock.json
│
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Buvashid9579/DocuChat.git
cd DocuChat
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file inside the `backend` directory using `.env.example` as a template.

Add your Google Gemini API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

Never commit your actual `.env` file or API key to GitHub.

### 4. Start the Backend

From the backend directory:

```bash
python -m uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL provided by Vite, normally:

```text
http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check backend health |
| POST | `/documents/upload` | Upload a PDF document |
| POST | `/chat/` | Ask questions about a selected document |

Interactive API documentation is available at `/docs`.

## How RAG Works in DocuChat

DocuChat follows a Retrieval-Augmented Generation workflow:

1. The user uploads a PDF document.
2. The backend extracts its text.
3. Extracted text is divided into smaller chunks.
4. Embeddings are generated and stored in ChromaDB along with document metadata.
5. The user submits a question.
6. The retriever searches for relevant chunks using the selected document ID.
7. Retrieved context is passed to the Gemini model.
8. Gemini generates an answer based on the retrieved context.
9. The frontend displays the answer and available source references.

Each uploaded document receives a unique document ID to prevent retrieval conflicts when multiple documents have the same filename.

## Running Tests

From the backend directory:

```bash
python -m pytest -v
```

The current automated test suite covers:

- Chat API behavior and validation
- PDF upload validation
- PDF text processing
- Unique document ID generation
- Vector-store metadata and filtering
- ChromaDB document isolation
- Backend health checks

## Current Limitations

- Only PDF documents are currently supported.
- Scanned and image-only PDFs are not supported because OCR has not been implemented.
- Complex tables, diagrams, and image-based content may not be extracted accurately.
- Uploaded document selections are maintained in frontend state and are not restored after a page refresh.
- Large-document performance limits have not yet been benchmarked.
- Document deletion and persistent document-management features are not yet implemented.

## Future Enhancements

- OCR support for scanned PDFs.
- Improved extraction of tables and complex layouts.
- Image and diagram understanding.
- Support for DOCX and other document formats.
- Persistent document history and management.
- Large-document processing optimization.
- Improved retrieval and response evaluation.

## Project Status

**Current Status: Working MVP**

The application has passed its current backend automated test suite and has been manually tested for PDF upload, question answering, and isolation of documents with identical filenames.

The project will continue to evolve with additional document-processing and retrieval capabilities.

---

**Built with Python, FastAPI, React, ChromaDB, LangChain, and Google Gemini.**