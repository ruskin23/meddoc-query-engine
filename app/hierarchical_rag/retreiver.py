from typing import List, Dict, Any

from app.core.retreival import PineconeRetriever
from .generator import PromptService

class HierarchicalRetriever:
    def __init__(self, 
                 prompt_service: PromptService, 
                 question_retriever: PineconeRetriever, 
                 chunk_retriever: PineconeRetriever):
        self.prompt_service = prompt_service
        self.question_retriever = question_retriever
        self.chunk_retriever = chunk_retriever

    def expand_questions(self, query: str, n_questions: int = 15) -> List[str]:
        return self.prompt_service.questions_from_query(query, n_questions=n_questions)

    def retrieve_pages_for_questions(
        self,
        questions: List[str],
        top_k_per_question: int = 5
    ) -> Dict[str, List[int]]:
        """
        Returns a mapping of each sub-question → list of top unique page_ids (ranked).
        """
        question_to_pages = {}

        for q in questions:
            matches = self.question_retriever.retrieve(q, top_k=top_k_per_question)
            page_scores = {}

            for match in matches:
                metadata = match.get("metadata", {})
                page_id = metadata.get("page_id")
                if not page_id:
                    continue

                score = match.get("score", 0)
                # keep highest score for each page
                if page_id not in page_scores or score > page_scores[page_id]:
                    page_scores[page_id] = score

            # sort by score descending and keep unique page IDs
            sorted_pages = sorted(page_scores.items(), key=lambda x: x[1], reverse=True)
            question_to_pages[q] = [page_id for page_id, _ in sorted_pages]

        return question_to_pages

    def retrieve_chunks_for_questions(
        self,
        question_to_pages: Dict[str, List[int]],
        chunks_per_page: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks from the chunk index for each question restricted to specific pages.

        Returns a flat list of matches with metadata, scores, and associated question.
        """
        all_chunks = []

        for question, page_ids in question_to_pages.items():
            for page_id in page_ids:
                matches = self.chunk_retriever.retrieve(
                    query=question,
                    top_k=chunks_per_page,
                    filter={"page_id": page_id}
                )

                for match in matches:
                    match["question"] = question
                    all_chunks.append(match)

        return all_chunks

    def rerank_top_chunks(
        self,
        all_chunks: List[Dict[str, Any]],
        top_n: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Rerank all retrieved chunks across all sub-questions and return the top N.
        """
        # Sort by score (highest first)
        sorted_chunks = sorted(all_chunks, key=lambda x: x.get("score", 0), reverse=True)

        return sorted_chunks[:top_n]
    
    def get_context_chunks(self, query: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """
        Run full hierarchical retrieval and return formatted chunks
        for downstream use (e.g. generation or display).
        Internal steps like sub-questions are abstracted away.
        """
        questions = self.expand_questions(query)
        question_to_pages = self.retrieve_pages_for_questions(questions)
        all_chunks = self.retrieve_chunks_for_questions(question_to_pages)
        top_chunks = self.rerank_top_chunks(all_chunks, top_n=top_n)

        return [
            {
                "chunk": match["metadata"].get("chunk"),
                "page_id": match["metadata"].get("page_id"),
                "pdf_id": match["metadata"].get("pdf_id"),
                "score": match.get("score")
            }
            for match in top_chunks
        ]
