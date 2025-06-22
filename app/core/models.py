from pydantic import BaseModel
from typing import List


class QAPair(BaseModel):
    """Model representing a single question-answer pair."""
    
    question: str
    answer: str
    

class QAPairs(BaseModel):
    """Model representing a collection of question-answer pairs."""
    
    pairs: List[QAPair]
    

class TagList(BaseModel):
    """Model representing a list of tags."""
    
    tags: List[str] 