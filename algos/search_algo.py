from abc import ABC, abstractmethod

Coord = tuple[int, int]
VisitedMap = dict[Coord, Coord]


class SearchAlgorith(ABC):

    # Only the heuristic searches (A*, GBFS) set this, to a list of
    # ((row, col), h) pairs, one per expanded cell in expansion order.
    heuristic_values = None

    @abstractmethod
    def search(
        self,
        grid,
        startr: int,
        startc: int,
        treasures: list[Coord] | None
    ) -> tuple[VisitedMap, Coord | tuple[()], int]:
        # (cell -> parent, treasure location or (), nodes expanded);
        # weighted searches add their total path cost as a fourth value
        ...