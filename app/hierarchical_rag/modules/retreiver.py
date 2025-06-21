from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from app.core import PineconeRetriever
from .generator import PromptService


class QuestionExpander(ABC):
    """Abstract base class for expanding queries into multiple questions."""
    
    @abstractmethod
    def expand(self, query: str, n: int) -> List[str]:
        """Expand a query into multiple related questions.
        
        Args:
            query: Original query
            n: Number of questions to generate
            
        Returns:
            List of expanded questions
        """
        ...


class Retriever(ABC):
    """Abstract base class for document retrieval."""
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve documents based on a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of retrieved documents
        """
        ...


class Reranker(ABC):
    """Abstract base class for reranking search results."""
    
    @abstractmethod
    def rerank(self, results: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
        """Rerank search results.
        
        Args:
            results: List of search results
            top_n: Number of top results to return
            
        Returns:
            Reranked list of results
        """
        ...


class PromptBasedExpander(QuestionExpander):
    """Expander that uses prompt-based generation to create questions."""
    
    def __init__(self, prompt_service: PromptService) -> None:
        """Initialize the prompt-based expander.
        
        Args:
            prompt_service: Service for prompt-based generation
        """
        self.prompt_service = prompt_service

    def expand(self, query: str, n: int = 15) -> List[str]:
        """Expand a query using prompt-based question generation.
        
        Args:
            query: Original query
            n: Number of questions to generate
            
        Returns:
            List of generated questions
        """
        return self.prompt_service.questions_from_query(query, n)


class PineconeRetrieverAdapter(Retriever):
    """Adapter for Pinecone retriever to match the Retriever interface."""
    
    def __init__(self, retriever: PineconeRetriever) -> None:
        """Initialize the Pinecone retriever adapter.
        
        Args:
            retriever: Pinecone retriever instance
        """
        self.retriever = retriever

    def retrieve(self, query: str, top_k: int, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve documents using the underlying Pinecone retriever.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of retrieved documents
        """
        return self.retriever.retrieve(query, top_k=top_k, filter=filter)


class ScoreReranker(Reranker):
    """Reranker that sorts results by score in descending order."""
    
    def rerank(self, results: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
        """Rerank results by score in descending order.
        
        Args:
            results: List of search results
            top_n: Number of top results to return
            
        Returns:
            Top N results sorted by score
        """
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)[:top_n]


class HierarchicalRetriever:
    """Hierarchical retriever that combines question expansion, retrieval, and reranking."""
    
    def __init__(
        self,
        expander: QuestionExpander,
        question_retriever: Retriever,
        chunk_retriever: Retriever,
        reranker: Reranker,
    ) -> None:
        """Initialize the hierarchical retriever.
        
        Args:
            expander: Service for expanding queries into questions
            question_retriever: Retriever for question documents
            chunk_retriever: Retriever for chunk documents
            reranker: Service for reranking results
        """
        self.expander = expander
        self.question_retriever = question_retriever
        self.chunk_retriever = chunk_retriever
        self.reranker = reranker

    def get_context_chunks(self, query: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """Get relevant context chunks for a query using hierarchical retrieval.
        
        Args:
            query: User query
            top_n: Number of top results to return
            
        Returns:
            List of relevant context chunks with metadata
        """
        # Expand query into multiple questions
        questions = self.expander.expand(query)

        # Map questions to relevant page IDs
        question_to_pages = {
            q: self._get_page_ids(q)
            for q in questions
        }

        # Get chunks from relevant pages
        all_chunks = self._get_chunks(question_to_pages)
        top_chunks = self.reranker.rerank(all_chunks, top_n)

        # Format results
        return [
            {
                "chunk": match["metadata"].get("chunk"),
                "page_id": match["metadata"].get("page_id"),
                "pdf_id": match["metadata"].get("pdf_id"),
                "score": match.get("score")
            }
            for match in top_chunks
        ]

    def _get_page_ids(self, question: str, top_k: int = 5) -> List[int]:
        """Get page IDs that are most relevant to a question.
        
        Args:
            question: Question to search for
            top_k: Number of top results to consider
            
        Returns:
            List of page IDs sorted by relevance
        """
        matches = self.question_retriever.retrieve(question, top_k=top_k)
        page_scores = {}
        for match in matches:
            page_id = match.get("metadata", {}).get("page_id")
            if page_id:
                score = match.get("score", 0)
                if page_id not in page_scores or score > page_scores[page_id]:
                    page_scores[page_id] = score
        return sorted(page_scores, key=page_scores.get, reverse=True)

    def _get_chunks(self, question_to_pages: Dict[str, List[int]], chunks_per_page: int = 3) -> List[Dict[str, Any]]:
        """Get chunks from pages based on question-page mappings.
        
        Args:
            question_to_pages: Mapping of questions to relevant page IDs
            chunks_per_page: Number of chunks to retrieve per page
            
        Returns:
            List of chunk documents with question context
        """
        results = []
        for question, page_ids in question_to_pages.items():
            for page_id in page_ids:
                matches = self.chunk_retriever.retrieve(question, top_k=chunks_per_page, filter={"page_id": page_id})
                for m in matches:
                    m["question"] = question
                    results.append(m)
        return results



