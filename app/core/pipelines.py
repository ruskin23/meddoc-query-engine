from abc import ABC, abstractmethod
from typing import List

class Generate(ABC):
    @abstractmethod
    def run(self):
        ...

class Index(ABC):
    @abstractmethod
    def run(self):
        ...

class Retreive(ABC):
    @abstractmethod 
    def run(self, query: str, top_n: int = 15) -> List[str]:
        ...
