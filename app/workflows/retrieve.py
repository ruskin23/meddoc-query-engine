from openai import OpenAI
import pinecone
from typing import List, Dict, Any

from app.core import EmbeddingService, PromptProcessor, PromptRunner, PineconeRetriever, TEMPLATES
from app.core.models import Questions
from app.core.prompting import PromptPayload


class HierarchicalRetriever:
    """Simplified hierarchical retriever that implements the core strategy without unnecessary abstractions."""
    
    def __init__(self, client: OpenAI, model: str, question_index, chunk_index, embedding_service: EmbeddingService):
        """Initialize the hierarchical retriever with core dependencies.
        
        Args:
            client: OpenAI client for query expansion
            model: Model name for query expansion
            question_index: Pinecone index for questions
            chunk_index: Pinecone index for chunks  
            embedding_service: Service for generating embeddings
        """
        # Create prompt processor for query expansion
        runner = PromptRunner(client=client, model=model)
        self.prompt_processor = PromptProcessor(generator=runner, templates=TEMPLATES)
        
        # Create direct retrievers
        self.question_retriever = PineconeRetriever(question_index, embedding_service)
        self.chunk_retriever = PineconeRetriever(chunk_index, embedding_service)
    
    def retrieve(self, query: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """Retrieve relevant context chunks using hierarchical strategy.
        
        Args:
            query: User query to search for
            top_n: Number of top results to return
            
        Returns:
            List of relevant context chunks with metadata
        """
        # Step 1: Expand query into multiple related questions
        questions = self._expand_query(query)
        
        # Step 2: Find relevant page IDs using question-based retrieval
        relevant_page_ids = self._get_relevant_pages(questions)
        
        # Step 3: Get chunks from relevant pages using chunk-based retrieval  
        all_chunks = self._get_chunks_from_pages(questions, relevant_page_ids)
        
        # Step 4: Sort by relevance score and return top N
        return self._rank_and_format_results(all_chunks, top_n)
    
    def _expand_query(self, query: str, n_questions: int = 15) -> List[str]:
        """Expand user query into multiple related questions."""
        payload = PromptPayload(
            prompt_key="questions_query",
            output_format=Questions,
            inputs={"query": query, "n_questions": n_questions}
        )
        result = self.prompt_processor.process(payload)
        return result.questions if hasattr(result, 'questions') else []
    
    def _get_relevant_pages(self, questions: List[str], pages_per_question: int = 5) -> set:
        """Get unique page IDs that are relevant to the expanded questions."""
        relevant_page_ids = set()
        
        for question in questions:
            matches = self.question_retriever.retrieve(question, top_k=pages_per_question)
            for match in matches:
                page_id = match.get("metadata", {}).get("page_id")
                if page_id:
                    relevant_page_ids.add(page_id)
        
        return relevant_page_ids
    
    def _get_chunks_from_pages(self, questions: List[str], page_ids: set, chunks_per_question: int = 50) -> List[Dict[str, Any]]:
        """Get chunks from relevant pages for each question."""
        all_chunks = []
        page_id_list = list(page_ids)
        
        for question in questions:
            if not page_id_list:
                continue
                
            # Filter chunks to only those from relevant pages
            page_filter = {"page_id": {"$in": page_id_list}}
            chunks = self.chunk_retriever.retrieve(
                question, 
                top_k=chunks_per_question, 
                filter=page_filter
            )
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def _rank_and_format_results(self, chunks: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
        """Sort chunks by relevance score and format for API response."""
        # Remove duplicates while preserving highest scores
        unique_chunks = {}
        for chunk in chunks:
            chunk_text = chunk.get("metadata", {}).get("chunk", "")
            page_id = chunk.get("metadata", {}).get("page_id")
            
            # Use combination of chunk text and page_id as unique key
            key = f"{page_id}:{hash(chunk_text)}"
            
            if key not in unique_chunks or chunk.get("score", 0) > unique_chunks[key].get("score", 0):
                unique_chunks[key] = chunk
        
        # Sort by score and take top N
        sorted_chunks = sorted(
            unique_chunks.values(), 
            key=lambda x: x.get("score", 0), 
            reverse=True
        )[:top_n]
        
        # Format for API response
        return [
            {
                "chunk": match.get("metadata", {}).get("chunk", ""),
                "page_id": match.get("metadata", {}).get("page_id", 0),
                "file_id": match.get("metadata", {}).get("pdf_id", 0),  # Note: using pdf_id as file_id
                "score": match.get("score", 0.0),
                "metadata": match.get("metadata", {})
            }
            for match in sorted_chunks
        ]


def retrieve(
    query: str,
    client: OpenAI,
    model: str,
    question_index_name: str,
    chunk_index_name: str,
    embedding_model_name: str,
    top_n: int = 15
) -> List[Dict[str, Any]]:
    """Retrieval workflow that implements hierarchical RAG strategy.
    
    Args:
        query: User query to search for
        client: OpenAI client instance
        model: Model name for query expansion
        question_index_name: Name of the question index
        chunk_index_name: Name of the chunk index
        embedding_model_name: Model name for embeddings
        top_n: Number of top results to return
        
    Returns:
        List of relevant context chunks with metadata
    """
    # Initialize core services
    question_index = pinecone.Index(question_index_name)
    chunk_index = pinecone.Index(chunk_index_name)
    embedding_service = EmbeddingService(model=embedding_model_name)

    # Create and use hierarchical retriever
    retriever = HierarchicalRetriever(
        client=client,
        model=model,
        question_index=question_index,
        chunk_index=chunk_index,
        embedding_service=embedding_service
    )

    return retriever.retrieve(query, top_n=top_n)
