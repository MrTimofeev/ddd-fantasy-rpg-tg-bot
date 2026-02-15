from abc import ABC, abstractmethod

class RandomProvider(ABC):
    @abstractmethod
    def randint(self, a: int, b: int) -> int:
        raise NotImplementedError
    
    @abstractmethod
    def choice(self, seq):
        pass
    