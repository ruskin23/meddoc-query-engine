from pydantic import BaseModel
from typing import List

class QAPair:
    question: str
    answer: str
    
class QAPairs:
    pairs: List[QAPair]
    
class TagList:
    tags: List[str]