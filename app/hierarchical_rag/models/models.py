from pydantic import BaseModel
from typing import List

class QAPair(BaseModel):
    question: str
    answer: str
    
class QAPairs(BaseModel):
    pairs: List[QAPair]
    
class TagList(BaseModel):
    tags: List[str]