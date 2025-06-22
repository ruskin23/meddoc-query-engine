# MedDoc Query Engine

This project is a semantic search engine designed to query a library of medical PDF documents. It uses a sophisticated Retrieval-Augmented Generation (RAG) pipeline to understand user queries and retrieve relevant text excerpts from the documents.

## 1. Overview

The core purpose of this application is to provide an accurate, semantic search experience for complex medical documents. Instead of relying on simple keyword matching, it leverages Large Language Models (LLMs) to understand the context and intent behind a user's query, ensuring that the returned results are highly relevant.

The system returns:
1.  Text excerpts that semantically match the search query.
2.  The specific pages from which the excerpts were extracted.

## 2. Architecture & Strategy

The application is built around a **Hierarchical RAG** strategy with a clean, simplified architecture that focuses on core functionality without unnecessary abstractions.

### Processing Workflow

The system follows a **three-stage processing pipeline**:

1.  **Extraction** (`/extract`): PDF files are ingested and their text content is extracted on a page-by-page basis and stored in a database. Files are marked as `extracted = True`.

2.  **Generation** (`/index/generate`): For each extracted page, an LLM (e.g., GPT-4) generates:
    *   A list of potential questions that the page content can answer.
    *   A set of granular text chunks.
    *   Relevant tags for the content.
    Files are marked as `generated = True`.

3.  **Indexing** (`/index/index`): The generated content is embedded and stored in two separate vector indexes (e.g., using Pinecone):
    *   **Question Index**: Contains the embeddings of the generated questions, linking back to their source page.
    *   **Chunk Index**: Contains the embeddings of the text chunks, also linked to their source page.
    Files are marked as `indexed = True`.

### Retrieval Workflow

1.  **Query Expansion**: When a user submits a query, an LLM expands it into a set of more specific, related questions.
2.  **Page Retrieval**: The expanded questions are used to search the **Question Index**. This step identifies the most relevant pages across all documents.
3.  **Chunk Retrieval**: The same expanded questions are then used to search the **Chunk Index**, but the search is filtered to only include chunks from the relevant pages identified in the previous step.
4.  **Reranking**: The retrieved chunks are reranked based on their semantic similarity score to the original query.
5.  **Response**: The top-ranked chunks, along with their source page and document ID, are returned to the user.

This two-stage process ensures that the search is both efficient and highly accurate, first narrowing down the search space to relevant pages and then pinpointing the most relevant information within them.

## 3. API Endpoints

The application is served via a FastAPI server.

-   `POST /ingest/`
    -   Ingests PDF files from a specified directory into the system.
    -   **Body**: `{"directory_path": "/path/to/your/pdfs"}`

-   `POST /extract/`
    -   Extracts text content from the ingested PDFs and stores it in the database.

-   `GET /index/status`
    -   Returns the current status of the processing pipeline, showing how many files are in each stage.

-   `POST /index/generate`
    -   Generates questions, tags, and chunks for extracted PDFs using LLM processing.

-   `POST /index/index`
    -   Indexes the generated content into the vector database.

-   `POST /index/`
    -   Runs the complete generation and indexing pipeline in sequence.

-   `GET /retrieve/`
    -   Performs a semantic search based on a user query.
    -   **Query Params**:
        -   `query` (str): The search query.
        -   `top_n` (int, optional): The number of results to return. Defaults to 5.

## 4. Setup and Usage

### Prerequisites

-   Python 3.12+
-   Access to an OpenAI API key.
-   A Pinecone account for vector storage.

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd meddoc-query-engine
    ```

2.  Install dependencies using `pip`:
    ```bash
    pip install -e .
    ```

### Configuration

1.  Create a `.env` file in the root of the project.

2.  Add the following environment variables. You will need to create two indexes in your Pinecone project with dimensions corresponding to your chosen embedding model (e.g., 1536 for `text-embedding-3-small`).

    ```env
    # Database Configuration
    DATABASE_URL=sqlite:///./meddoc.db

    # OpenAI Configuration
    OPENAI_API_KEY=your-openai-api-key-here
    OPENAI_MODEL=gpt-4-turbo

    # Embedding Model Configuration
    EMBEDDING_MODEL=text-embedding-3-small

    # Pinecone Configuration
    PINECONE_API_KEY=your-pinecone-api-key-here
    PINECONE_ENVIRONMENT=your-pinecone-environment-here
    QUESTION_INDEX_NAME=your-question-index-name
    CHUNK_INDEX_NAME=your-chunk-index-name
    ```

    **Required Variables:**
    - `OPENAI_API_KEY`: Your OpenAI API key (required)
    - `QUESTION_INDEX_NAME`: Name of your Pinecone question index (required)
    - `CHUNK_INDEX_NAME`: Name of your Pinecone chunk index (required)

    **Optional Variables (with defaults):**
    - `DATABASE_URL`: Database connection string (default: `sqlite:///./meddoc.db`)
    - `OPENAI_MODEL`: OpenAI model to use (default: `gpt-4-turbo`)
    - `EMBEDDING_MODEL`: Embedding model to use (default: `text-embedding-3-small`)
    - `PINECONE_API_KEY`: Pinecone API key (uses default if not set)
    - `PINECONE_ENVIRONMENT`: Pinecone environment (uses default if not set)


### Running the Application

1.  Initialize the database. You may need to run your database migration tool if you are using one like Alembic. For `sqlite`, the file will be created automatically.

2.  Start the FastAPI server:
    ```bash
    python main.py
    ```
    The application will be available at `http://127.0.0.1:8000`.

### Example Workflow using cURL

1.  **Check Status** (to see current pipeline state)
    ```bash
    curl -X GET http://127.0.0.1:8000/index/status
    ```

2.  **Ingest PDFs** (replace with the actual path to your PDFs)
    ```bash
    curl -X POST -H "Content-Type: application/json" \
      -d '{"directory_path": "path/to/medical_pdfs"}' \
      http://127.0.0.1:8000/ingest/
    ```

3.  **Extract Text**
    ```bash
    curl -X POST http://127.0.0.1:8000/extract/
    ```

4.  **Generate Content** (This may take some time depending on document size)
    ```bash
    curl -X POST http://127.0.0.1:8000/index/generate
    ```

5.  **Index Content**
    ```bash
    curl -X POST http://127.0.0.1:8000/index/index
    ```

6.  **Retrieve Information**
    ```bash
    curl -X GET "http://127.0.0.1:8000/retrieve/?query=information%20on%20spinal%20treatment&top_n=5"
    ```

**Alternative**: You can run the complete pipeline in one step:
```bash
curl -X POST http://127.0.0.1:8000/index/
```
