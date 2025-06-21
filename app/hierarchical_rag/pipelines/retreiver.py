from typing import List, Dict, Any

from app.core import Retreive

class RetrievalPipeline(Retreive):
    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, query: str, top_n: int = 15) -> List[Dict[str, Any]]:
        return self.retriever.get_context_chunks(query, top_n=top_n)
