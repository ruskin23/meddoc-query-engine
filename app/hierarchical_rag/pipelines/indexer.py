from app.core import Index
from app.hierarchical_rag.modules.indexer import HierarchicalIndexer


class IndexingPipeline(Index):
    def __init__(self, indexer: HierarchicalIndexer):
        self.indexer = indexer

    def run(self):
        self.indexer.index_all()
        