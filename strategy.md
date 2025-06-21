# Medical Document Query Engine: Hierarchical RAG Strategy

## Problem Context

Medical documents contain complex, interconnected information that requires semantic understanding beyond simple keyword matching. The challenge is to build a system that can:

1. **Extract meaningful information** from diverse medical PDFs
2. **Index content efficiently** for fast retrieval
3. **Understand semantic queries** and return relevant excerpts
4. **Provide accurate results** with source attribution (page numbers and document references)

This document outlines the **Hierarchical Retrieval-Augmented Generation (RAG)** strategy implemented to address these challenges.

## Core Strategy: Hierarchical RAG

The system employs a **hierarchical approach** that processes content at multiple levels of granularity and uses a two-stage retrieval mechanism to maximize both efficiency and accuracy.

### Key Innovation: Dual-Index Architecture

Instead of a single vector index, the system maintains **two separate vector databases**:

1. **Question Index**: Contains embeddings of AI-generated questions that each page can answer
2. **Chunk Index**: Contains embeddings of granular text chunks from the same pages

This dual-index design enables a **coarse-to-fine retrieval strategy** that first identifies relevant document sections, then pinpoints the most relevant content within those sections.

## Indexing Strategy

The indexing process follows a **three-stage pipeline** designed to extract maximum semantic value from medical documents:

### Stage 1: Extraction
- **Objective**: Convert PDF documents into structured, searchable text
- **Process**: 
  - PDFs are ingested and parsed page-by-page
  - Text content is extracted and stored in a relational database
  - Each page becomes a discrete unit for processing
- **Output**: Page-level text content linked to source documents
- **Status Tracking**: Files marked as `extracted = True`

### Stage 2: Content Generation
- **Objective**: Create rich semantic representations of each page's content using LLM processing
- **Process**: For each extracted page, GPT-4 generates:
  
  **Question Generation**:
  - Multiple questions that the page content can answer
  - Questions capture the key medical concepts and information
  - Example: For a hip surgery page → "What are the rehabilitation steps after hip replacement?"
  
  **Tag Generation**:
  - Anatomical tags and medical categories
  - Body parts, systems, and medical specialties mentioned
  - Example: "hip", "joint", "orthopedic", "rehabilitation"
  
  **Text Chunking**:
  - Granular text segments with semantic coherence
  - Chunks sized for optimal embedding and retrieval
  
- **Rationale**: Questions act as semantic "keys" that unlock relevant content, while chunks provide the actual retrievable content
- **Status Tracking**: Files marked as `generated = True`

### Stage 3: Vector Indexing
- **Objective**: Convert generated content into searchable vector embeddings
- **Process**:
  - **Question Embeddings**: Each generated question is embedded and stored in the Question Index with metadata linking back to its source page
  - **Chunk Embeddings**: Each text chunk is embedded and stored in the Chunk Index with the same page linkage
  - Both indexes include metadata: `page_id`, `pdf_id`, `tags`
- **Vector Database**: Pinecone (though adaptable to other vector databases)
- **Embedding Model**: OpenAI's `text-embedding-3-small` (configurable)
- **Status Tracking**: Files marked as `indexed = True`

### Database Schema Design

The system uses a relational database to track processing states and maintain data relationships:

```
PdfFile (id, filepath, extracted, generated, indexed, timestamps)
├── PdfPages (id, file_id, page_number, page_text)
    ├── PageQuestions (id, page_id, file_id, question)
    ├── PageTags (id, page_id, file_id, tag)
    └── PageChunks (id, page_id, file_id, chunk)
```

This design enables:
- **Pipeline State Management**: Track which files are at which processing stage
- **Data Lineage**: Maintain relationships between generated content and source pages
- **Incremental Processing**: Process only new or updated content

## Retrieval Strategy

The retrieval process implements a **four-stage hierarchical approach** that progressively narrows the search space:

### Stage 1: Query Expansion
- **Objective**: Transform user queries into multiple semantic variants for comprehensive matching
- **Process**: 
  - User query is sent to GPT-4 with the prompt template `questions_query`
  - LLM generates multiple related questions (typically 15)
  - Example: "hip surgery" → ["What are the risks of hip replacement?", "How long is hip surgery recovery?", "What are alternatives to hip surgery?"]
- **Rationale**: Medical queries can be expressed in many ways; expansion ensures comprehensive coverage

### Stage 2: Page-Level Retrieval
- **Objective**: Identify the most relevant document pages across the entire corpus
- **Process**:
  - Each expanded question is embedded and queried against the **Question Index**
  - Vector similarity search returns pages whose generated questions match the expanded queries
  - Page IDs are ranked by similarity scores and deduplicated
- **Result**: A ranked list of relevant pages from across all documents
- **Efficiency**: This stage dramatically reduces the search space from potentially thousands of chunks to a manageable set of relevant pages

### Stage 3: Chunk-Level Retrieval
- **Objective**: Extract the most relevant content from the identified pages
- **Process**:
  - The same expanded questions are used to query the **Chunk Index**
  - Search is **filtered** to only include chunks from the pages identified in Stage 2
  - Multiple chunks per page are retrieved (typically 3 per page)
  - Results are aggregated across all relevant pages
- **Result**: A collection of text chunks that are both topically relevant (from Stage 2 filtering) and semantically similar (from embedding matching)

### Stage 4: Reranking and Response Assembly
- **Objective**: Select and rank the final results for optimal user experience
- **Process**:
  - All retrieved chunks are reranked by their semantic similarity scores
  - Top N chunks are selected (user-configurable, default 5-15)
  - Results include:
    - **Text excerpt**: The actual chunk content
    - **Source attribution**: Page number and document ID
    - **Relevance score**: Semantic similarity score
    - **Metadata**: Tags and other contextual information

## Technical Architecture

### Modular Design Pattern

The system employs a **modular, interface-driven architecture** that separates concerns:

**Abstract Interfaces**:
- `QuestionExpander`: For query expansion strategies
- `Retriever`: For document retrieval implementations
- `Reranker`: For result ranking strategies
- `GenerationTask`: For content generation tasks

**Concrete Implementations**:
- `PromptBasedExpander`: Uses LLM prompts for query expansion
- `PineconeRetrieverAdapter`: Adapts Pinecone to the retriever interface
- `ScoreReranker`: Ranks results by similarity scores
- `HierarchicalRetriever`: Orchestrates the complete retrieval process

### Pipeline Architecture

**Generation Pipeline**:
```
PDF Files → ExtractionPipeline → GenerationPipeline → IndexingPipeline
```

**Retrieval Pipeline**:
```
User Query → QueryExpansion → PageRetrieval → ChunkRetrieval → Reranking → Response
```

### Configuration Management

The system uses environment-based configuration for flexibility:
- **OpenAI Settings**: API key, model selection
- **Vector Database**: Pinecone indexes and credentials
- **Embedding Models**: Configurable embedding providers
- **Database**: Flexible database connection strings

## Advantages of This Strategy

### 1. **Semantic Understanding**
- LLM-generated questions capture diverse ways medical concepts can be expressed
- Vector embeddings enable semantic similarity matching beyond keyword overlap

### 2. **Scalability**
- Two-stage retrieval reduces computational complexity
- Page-level filtering dramatically narrows search space before expensive chunk retrieval
- Modular architecture allows component optimization independently

### 3. **Accuracy**
- Question-based indexing creates multiple "entry points" to relevant content
- Hierarchical filtering ensures results are both topically and semantically relevant
- Reranking provides final relevance optimization

### 4. **Flexibility**
- Abstract interfaces allow swapping implementations (different LLMs, vector databases)
- Configurable parameters enable tuning for different use cases
- Pipeline architecture supports incremental processing

### 5. **Transparency**
- Complete source attribution (page numbers, document IDs)
- Relevance scores provide confidence indicators
- Database tracking enables audit trails

## Performance Characteristics

### Indexing Performance
- **Time Complexity**: O(n × p) where n = documents, p = pages per document
- **Space Complexity**: Dual indexes require ~2x storage vs. single index
- **Processing**: Batch processing with state tracking enables resume after interruption

### Retrieval Performance
- **Query Time**: Typically 1-3 seconds for complex queries
- **Accuracy**: High precision due to two-stage filtering
- **Scalability**: Performance degrades gracefully with corpus size

## Addressing the Original Problem

This hierarchical RAG strategy directly addresses the original requirements:

### 1. **Semantic Search Beyond Keywords**
- ✅ LLM-based query expansion generates semantic variants
- ✅ Vector embeddings capture semantic relationships
- ✅ Question-based indexing provides multiple conceptual access points

### 2. **Accurate Page and Excerpt Retrieval**
- ✅ Two-stage approach first identifies relevant pages, then extracts precise excerpts
- ✅ Complete source attribution with page numbers and document IDs
- ✅ Relevance scoring provides confidence measures

### 3. **Medical Domain Optimization**
- ✅ Prompt templates optimized for medical content
- ✅ Anatomical tagging and medical concept extraction
- ✅ Question generation captures medical information needs

### 4. **API Integration**
- ✅ FastAPI implementation with clean REST endpoints
- ✅ Configurable response formats and result counts
- ✅ Error handling and validation

## Example Workflow

**Input**: User query "hip surgery"

**Query Expansion**: 
- "What are the risks of hip replacement surgery?"
- "How long does hip surgery recovery take?"
- "What preparation is needed for hip surgery?"
- [... 12 more related questions]

**Page Retrieval**: 
- Search Question Index with expanded queries
- Identify pages 23, 45, 67, 89 from documents A, B, C as most relevant

**Chunk Retrieval**:
- Search Chunk Index with same expanded queries
- Filter to only chunks from pages 23, 45, 67, 89
- Retrieve 3 best chunks per page = 12 total chunks

**Reranking**:
- Sort 12 chunks by similarity scores
- Return top 5 chunks with source attribution

**Response**:
```json
{
  "query": "hip surgery",
  "results": [
    {
      "chunk": "Hip replacement surgery typically requires 2-3 hours...",
      "score": 0.89,
      "page_id": 23,
      "file_id": 1,
      "metadata": {"tags": ["hip", "surgery", "orthopedic"]}
    }
  ],
  "total_results": 5,
  "processing_time_ms": 1250
}
```

## Conclusion

The hierarchical RAG strategy provides a robust solution for semantic search over medical documents by:

1. **Indexing content at multiple semantic levels** (questions and chunks)
2. **Using two-stage retrieval** to balance efficiency and accuracy
3. **Leveraging LLM capabilities** for content understanding and query expansion
4. **Maintaining complete data lineage** for transparency and debugging
5. **Providing a flexible, modular architecture** for future enhancements

This approach successfully transforms the challenge of medical document search from a keyword-matching problem into a semantic understanding problem, delivering accurate, contextual results with complete source attribution. 