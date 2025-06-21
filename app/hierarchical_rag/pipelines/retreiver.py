from typing import List, Dict, Any

from app.core import Retreive


class RetrievalPipeline(Retreive):
    """Pipeline for retrieving relevant context chunks using hierarchical retrieval."""
    
    def __init__(self, retriever) -> None:
        """Initialize the retrieval pipeline.
        
        Args:
            retriever: Hierarchical retriever for finding relevant content
        """
        self.retriever = retriever

    def run(self, query: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """Run the retrieval pipeline to find relevant context chunks.
        
        Args:
            query: User query to search for
            top_n: Number of top results to return
            
        Returns:
            List of relevant context chunks with metadata
        """
        return self.retriever.get_context_chunks(query, top_n=top_n)
