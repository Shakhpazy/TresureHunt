from abc import ABC, abstractmethod

Coord = tuple[int, int]
VisitedMap = dict[Coord, Coord]


class SearchAlgorith(ABC):

    @abstractmethod
    def search(
        self,
        grid,
        startr: int,
        startc: int,
    ) -> tuple[VisitedMap, Coord | tuple[()]]:
        ...