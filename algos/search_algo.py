from abc import ABC, abstractmethod

class SearchAlgorith(ABC):

    @abstractmethod
    def search(self, grid, startr, startc) -> dict[tuple[int, int], tuple[int, int]]:
        ...