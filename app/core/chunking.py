from typing import List, Callable, Dict
import re
import tiktoken


class ChunkService:
    """Service for splitting text into chunks using various strategies."""
    
    def __init__(self, method: str = "recursive", chunk_size: int = 500, chunk_overlap: int = 50, model: str = "gpt-3.5-turbo") -> None:
        """Initialize the chunking service.
        
        Args:
            method: Chunking strategy ('fixed', 'recursive', 'sentence', 'tokens')
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
            model: Model name for token-based chunking
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)

        # Available chunking strategies
        self.strategies: Dict[str, Callable[[str], List[str]]] = {
            "fixed": self._fixed_chunks,
            "recursive": self._recursive_chunks,
            "sentence": self._sentence_chunks,
            "tokens": self._token_chunks
        }

        if method not in self.strategies:
            raise ValueError(f"Unsupported chunking method: {method}")

        self.chunk_fn = self.strategies[method]

    def chunks_for_page(self, text: str) -> List[str]:
        """Split page text into chunks using the configured strategy.
        
        Args:
            text: Text content to chunk
            
        Returns:
            List of text chunks
        """
        return self.chunk_fn(text)

    def _fixed_chunks(self, text: str) -> List[str]:
        """Split text into fixed-size chunks without considering word boundaries."""
        return [
            text[i:i + self.chunk_size]
            for i in range(0, len(text), self.chunk_size)
        ]

    def _recursive_chunks(self, text: str) -> List[str]:
        """Split text recursively using natural separators."""
        separators = ["\n\n", "\n", ".", " ", ""]
        return self._recursive_split(text, separators)

    def _sentence_chunks(self, text: str) -> List[str]:
        """Split text into chunks based on sentence boundaries."""
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks, current, current_len = [], [], 0

        for sentence in sentences:
            current.append(sentence)
            current_len += len(sentence)
            if current_len >= self.chunk_size:
                chunks.append(" ".join(current))
                current, current_len = [], 0

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _token_chunks(self, text: str) -> List[str]:
        """Split text into chunks based on token count."""
        tokens = self.encoding.encode(text)
        chunks = []
        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        return chunks

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using the best available separator."""
        for sep in separators:
            if sep and sep in text:
                parts = text.split(sep)
                chunks, current = [], ""
                for part in parts:
                    if len(current) + len(part) + len(sep) <= self.chunk_size:
                        current += part + sep
                    else:
                        if current:
                            chunks.append(current.strip())
                        current = part + sep
                if current:
                    chunks.append(current.strip())

                # Add overlap between chunks
                final_chunks = []
                for i in range(len(chunks)):
                    if i == 0:
                        final_chunks.append(chunks[i])
                    else:
                        overlap = chunks[i - 1][-self.chunk_overlap:] if self.chunk_overlap else ""
                        final_chunks.append(overlap + chunks[i])
                return final_chunks

        return self._fixed_chunks(text)  # fallback
