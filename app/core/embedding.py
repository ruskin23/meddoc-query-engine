from typing import List
import openai

class EmbeddingService:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        response = openai.Embedding.create(
            input=texts,
            model=self.model
        )
        return [item["embedding"] for item in response["data"]]
