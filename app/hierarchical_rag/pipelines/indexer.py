from app.core import Index
from app.hierarchical_rag import HierarchicalIndexer


class IndexingPipeline(Index):
    """Pipeline for indexing generated content into vector databases."""
    
    def __init__(self, indexer: HierarchicalIndexer) -> None:
        """Initialize the indexing pipeline.
        
        Args:
            indexer: Hierarchical indexer for processing PDF files
        """
        self.indexer = indexer

    def run(self) -> None:
        """Run the indexing pipeline on all generated but unindexed PDF files."""
        self.indexer.index_all()
        