from typing import List, Dict, Any
from abc import ABC, abstractmethod

from app.core import PineconeRetriever
from .generator import PromptService


class QuestionExpander(ABC):
    @abstractmethod
    def expand(self, query: str, n: int) -> List[str]: ...

class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int, filter: dict = None) -> List[Dict[str, Any]]: ...

class Reranker(ABC):
    @abstractmethod
    def rerank(self, results: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]: ...



class PromptBasedExpander(QuestionExpander):
    def __init__(self, prompt_service: PromptService):
        self.prompt_service = prompt_service

    def expand(self, query: str, n: int = 15) -> List[str]:
        return self.prompt_service.questions_from_query(query, n)

class PineconeRetrieverAdapter(Retriever):
    def __init__(self, retriever: PineconeRetriever):
        self.retriever = retriever

    def retrieve(self, query: str, top_k: int, filter: dict = None) -> List[Dict[str, Any]]:
        return self.retriever.retrieve(query, top_k=top_k, filter=filter)

class ScoreReranker(Reranker):
    def rerank(self, results: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)[:top_n]

class HierarchicalRetriever:
    def __init__(
        self,
        expander: QuestionExpander,
        question_retriever: Retriever,
        chunk_retriever: Retriever,
        reranker: Reranker,
    ):
        self.expander = expander
        self.question_retriever = question_retriever
        self.chunk_retriever = chunk_retriever
        self.reranker = reranker

    def get_context_chunks(self, query: str, top_n: int = 15) -> List[Dict[str, Any]]:
        questions = self.expander.expand(query)

        question_to_pages = {
            q: self._get_page_ids(q)
            for q in questions
        }

        all_chunks = self._get_chunks(question_to_pages)
        top_chunks = self.reranker.rerank(all_chunks, top_n)

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
        matches = self.question_retriever.retrieve(question, top_k=top_k)
        page_scores = {}
        for match in matches:
            page_id = match.get("metadata", {}).get("page_id")
            if page_id:
                score = match.get("score", 0)
                if page_id not in page_scores or score > page_scores[page_id]:
                    page_scores[page_id] = score
        return sorted(page_scores, key=page_scores.get, reverse=True)

    def _get_chunks(self, question_to_pages: Dict[str, List[int]], chunks_per_page: int = 3):
        results = []
        for question, page_ids in question_to_pages.items():
            for page_id in page_ids:
                matches = self.chunk_retriever.retrieve(question, top_k=chunks_per_page, filter={"page_id": page_id})
                for m in matches:
                    m["question"] = question
                    results.append(m)
        return results



