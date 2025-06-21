from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Generate(ABC):
    """Abstract base class for content generation pipelines."""
    
    @abstractmethod
    def run(self) -> None:
        """Run the generation pipeline."""
        ...

class Index(ABC):
    """Abstract base class for indexing pipelines."""
    
    @abstractmethod
    def run(self) -> None:
        """Run the indexing pipeline."""
        ...

class Retreive(ABC):
    """Abstract base class for retrieval pipelines."""
    
    @abstractmethod 
    def run(self, query: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """Run the retrieval pipeline.
        
        Args:
            query: Search query
            top_n: Number of results to return
            
        Returns:
            List of retrieved documents
        """
        ...
