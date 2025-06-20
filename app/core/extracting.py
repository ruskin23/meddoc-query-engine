from typing import List, Tuple
import fitz


class TextExtraction:
    def __init__(self):
        pass

    def extract(self, filepath: str) -> List[Tuple[int, str]]:
        doc = fitz.open(filepath)
        return [(i + 1, page.get_text()) for i, page in enumerate(doc)]
