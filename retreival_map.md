# Retrieval Class/Object Mapping for Medical Document Query Engine

This document maps the complete class/object structure for the retrieval process, showing how classes are instantiated and called step-by-step to build the response.

## Overview

The retrieval process follows a hierarchical RAG (Retrieval-Augmented Generation) pattern that:
1. Expands the user query into multiple related questions
2. Retrieves relevant page IDs using question-based retrieval
3. Retrieves relevant chunks from those pages
4. Reranks and formats the results

## API Entry Point

### 1. FastAPI Route Handler
```python
# File: app/api/routes/retrieve.py
@router.get("/", response_model=RetrievalResponse)
def retrieve_endpoint(query: str, top_n: int) -> RetrievalResponse
```

**Input Models:**
- `query`: String parameter from URL query
- `top_n`: Integer parameter from URL query

**Output Models:**
- `RetrievalResponse`: Contains query, results, total_results, processing_time_ms
- `RetrievalResult`: Individual result with chunk, score, page_id, file_id, metadata

## Step-by-Step Class Flow

### 2. Configuration & Settings
```python
# File: app/core/config.py
Settings(BaseSettings)
```
- Loads configuration from environment variables
- Provides: `openai_api_key`, `openai_model`, `question_index_name`, `chunk_index_name`, `embedding_model`

### 3. Workflow Entry Point
```python
# File: app/workflows/retreive.py
retreive(query, client, model, question_index_name, chunk_index_name, embedding_model_name, top_n)
```

This function orchestrates the entire retrieval process by:

#### 3.1 Creating Core Services
- **OpenAI Client**: `OpenAI(api_key=settings.openai_api_key)`
- **Pinecone Indexes**: 
  - `question_index = pinecone.Index(question_index_name)`
  - `chunk_index = pinecone.Index(chunk_index_name)`

#### 3.2 Embedding Service
```python
# File: app/core/embedding.py
EmbeddingService(model=embedding_model_name)
```
- **Purpose**: Converts text queries into vector embeddings
- **Method**: `embed(texts: List[str]) -> List[List[float]]`
- **Uses**: OpenAI's embedding API

#### 3.3 Prompt Service Creation
```python
# File: app/hierarchical_rag/modules/generator.py
PromptService(processor: PromptProcessor)
```

**Dependencies created:**
- **PromptRunner** (`app/core/prompting.py`):
  ```python
  PromptRunner(client=client, model=model)
  ```
  - Executes prompts using OpenAI client
  - Method: `generate(template, output_format, **inputs)`

- **PromptProcessor** (`app/core/prompting.py`):
  ```python
  PromptProcessor(generator=runner, templates=TEMPLATES)
  ```
  - Processes prompt payloads using templates
  - Method: `process(payload: PromptPayload)`

- **TEMPLATES** (`app/hierarchical_rag/modules/prompts.py`):
  ```python
  {
    "questions_query": PromptTemplate(...),
    "page_questions": PromptTemplate(...),
    "body_tags_page": PromptTemplate(...),
    "body_tags_query": PromptTemplate(...)
  }
  ```

#### 3.4 Retriever Adapters
```python
# File: app/hierarchical_rag/modules/retreiver.py
PineconeRetrieverAdapter(PineconeRetriever)
```

**For each index (question and chunk):**
- **PineconeRetriever** (`app/core/retreival.py`):
  ```python
  PineconeRetriever(index=pinecone_index, embedding_service=embedding_service)
  ```
  - **Method**: `retrieve(query, top_k, filter, namespace, include_metadata)`
  - **Process**: Embeds query → Queries Pinecone → Returns matches

- **PineconeRetrieverAdapter**:
  ```python
  PineconeRetrieverAdapter(retriever: PineconeRetriever)
  ```
  - **Purpose**: Adapts PineconeRetriever to match Retriever interface
  - **Method**: `retrieve(query, top_k, filter)`

### 4. Hierarchical Retriever Assembly
```python
# File: app/hierarchical_rag/modules/retreiver.py
HierarchicalRetriever(expander, question_retriever, chunk_retriever, reranker)
```

**Components:**

#### 4.1 Query Expander
```python
PromptBasedExpander(prompt_service: PromptService)
```
- **Purpose**: Expands user query into multiple related questions
- **Method**: `expand(query: str, n: int) -> List[str]`
- **Process**: Uses "questions_query" template to generate N questions

#### 4.2 Question Retriever
```python
PineconeRetrieverAdapter(question_retriever)
```
- **Purpose**: Finds relevant page IDs using expanded questions
- **Target**: Question index in Pinecone

#### 4.3 Chunk Retriever
```python
PineconeRetrieverAdapter(chunk_retriever)
```
- **Purpose**: Retrieves actual content chunks from relevant pages
- **Target**: Chunk index in Pinecone

#### 4.4 Reranker
```python
ScoreReranker()
```
- **Purpose**: Sorts results by relevance score
- **Method**: `rerank(results: List[Dict[str, Any]], top_n: int)`
- **Logic**: Sorts by score in descending order, takes top N

### 5. Retrieval Pipeline Execution
```python
# File: app/hierarchical_rag/pipelines/retreiver.py
RetrievalPipeline(retriever: HierarchicalRetriever)
```
- **Method**: `run(query: str, top_n: int) -> List[Dict[str, Any]]`
- **Delegates to**: `retriever.get_context_chunks(query, top_n)`

### 6. Hierarchical Retrieval Process
```python
# File: app/hierarchical_rag/modules/retreiver.py
HierarchicalRetriever.get_context_chunks(query: str, top_n: int)
```

**Step-by-step execution:**

1. **Query Expansion**: 
   - `expander.expand(query)` → List of related questions
   - Uses PromptBasedExpander → PromptService → PromptProcessor → PromptRunner

2. **Question-to-Page Mapping**:
   - For each expanded question: `_get_page_ids(question)`
   - Uses question_retriever (PineconeRetrieverAdapter → PineconeRetriever)
   - Returns relevant page IDs ranked by score

3. **Chunk Retrieval**:
   - `_get_chunks(question_to_pages)` for each relevant page
   - Uses chunk_retriever with page_id filters
   - Aggregates chunks from all relevant pages

4. **Reranking**:
   - `reranker.rerank(all_chunks, top_n)`
   - Sorts by relevance score, returns top N results

### 7. Response Formatting
Back in the API route (`app/api/routes/retrieve.py`):

```python
# Convert results to response format
for result in results:
    RetrievalResult(
        chunk=result.get('chunk', ''),
        score=result.get('score', 0.0),
        page_id=result.get('page_id', 0),
        file_id=result.get('file_id', 0),
        metadata=result.get('metadata', {})
    )

# Final response
RetrievalResponse(
    query=query,
    results=retrieval_results,
    total_results=len(retrieval_results),
    processing_time_ms=processing_time
)
```

## Class Dependency Diagram

```
RetrievalResponse
├── RetrievalResult[]
│
API Route (retrieve_endpoint)
├── Settings (configuration)
├── OpenAI (client)
└── retreive() workflow
    ├── EmbeddingService
    ├── PromptService
    │   ├── PromptProcessor
    │   │   ├── PromptRunner
    │   │   └── TEMPLATES (PromptTemplate[])
    │   └── PromptPayload
    ├── PineconeRetrieverAdapter[]
    │   └── PineconeRetriever
    │       ├── pinecone.Index
    │       └── EmbeddingService
    ├── HierarchicalRetriever
    │   ├── PromptBasedExpander (QuestionExpander)
    │   ├── PineconeRetrieverAdapter (question_retriever)
    │   ├── PineconeRetrieverAdapter (chunk_retriever)
    │   └── ScoreReranker (Reranker)
    └── RetrievalPipeline
        └── HierarchicalRetriever
```

## Key Interfaces and Abstract Classes

### Abstract Base Classes
- **QuestionExpander**: Interface for query expansion
- **Retriever**: Interface for document retrieval
- **Reranker**: Interface for result reranking
- **GenerationTask**: Interface for content generation tasks

### Concrete Implementations
- **PromptBasedExpander**: Expands queries using prompts
- **PineconeRetrieverAdapter**: Adapts PineconeRetriever to Retriever interface
- **ScoreReranker**: Reranks by relevance score
- **HierarchicalRetriever**: Orchestrates the entire retrieval process

## Data Flow Summary

1. **User Query** → API Route
2. **Configuration Loading** → Settings class
3. **Service Initialization** → OpenAI, Pinecone, Embedding, Prompt services
4. **Query Expansion** → PromptBasedExpander generates related questions
5. **Question Retrieval** → Find relevant page IDs using question index
6. **Chunk Retrieval** → Get content chunks from relevant pages using chunk index
7. **Reranking** → Sort results by relevance score
8. **Response Formatting** → Convert to API response models
9. **Return** → RetrievalResponse with RetrievalResult[]

This hierarchical approach ensures high-quality retrieval by first identifying relevant document sections through question-based matching, then retrieving the most relevant content chunks from those sections. 