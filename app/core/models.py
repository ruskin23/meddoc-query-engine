from pydantic import BaseModel
from typing import List


class Questions(BaseModel):
    """Model representing a list of questions."""
    
    questions: List[str]


class TagList(BaseModel):
    """Model representing a list of tags."""
    
    tags: List[str] 