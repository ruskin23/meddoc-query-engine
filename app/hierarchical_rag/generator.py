from typing import Any

from app.core.prompting import PromptProcessor, PromptPayload
from .models import QAPairs, TagList

class PromptService:
    def __init__(self, processor: PromptProcessor):
        self.processor = processor

    def questions_for_page(self, page_text: str) -> Any:
        payload = PromptPayload(
            prompt_key="page_questions",
            output_format=QAPairs,
            inputs={"page_text": page_text}
        )
        return self.processor.process(payload)

    def tags_for_page(self, page_text: str) -> Any:
        payload = PromptPayload(
            prompt_key="body_tags_page",
            output_format=TagList,
            inputs={"page_text": page_text}
        )
        return self.processor.process(payload)

    def tags_from_query(self, query: str) -> Any:
        payload = PromptPayload(
            prompt_key="body_tags_query",
            output_format=TagList,
            inputs={"query": query}
        )
        return self.processor.process(payload)
    
    def questions_from_query(self, query: str, n_questions:int = 15) -> Any:
        payload = PromptPayload(
            prompt_key="questions_query",
            output_format=TagList,
            inputs={"query": query, "n_questions": n_questions}
        )
        return self.processor.process(payload)
    

    def available_prompts(self) -> list:
        return list(self.processor.templates.keys())
