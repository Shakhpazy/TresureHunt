from abc import ABC, abstractmethod

Coord = tuple[int, int]
VisitedMap = dict[Coord, Coord]
TreasureLocations = tuple[Coord, ...]
SearchResult = tuple[VisitedMap, TreasureLocations, int]
WeightedSearchResult = tuple[VisitedMap, TreasureLocations, int, int | None]


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
    ) -> SearchResult | WeightedSearchResult:
        # (cell -> parent, treasure locations, nodes expanded), with an
        # optional fourth total-cost value for weighted searches such as UCS.
        ...
