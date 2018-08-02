from typing import Dict, List, Optional, Set, Tuple


class Row(int):
    """Type object for row data"""
    pass


class Column(int):
    """Type object for column data"""
    pass


class GridLocation(object):
    """
    Type object representing a location on a grid
    """
    def __init__(self, row : Row, column : Column) -> None:
        self.row : Row = row
        self.col : Column = column

    def __eq__(self, other) -> bool:
        return self.row == other.row and self.col == other.col

    def __hash__(self) -> int:
        return(hash((self.row, self.col)))

    def __repr__(self) -> str:
        return ("[GridLocation] Row: " + str(self.row) +
                " Column: " + str(self.col))


class BaseGridSystem(object):
    """
    Actual grid systems inherit this class.
    """
    def __init__(self, rows : int,
                 columns : int,
                 center_on_origin: bool = True) -> None:
        self.rows : int = rows
        self.cols : int = columns
        self.center_on_origin : bool = center_on_origin
        self.origin : Tuple[int, int] = (0, 0)
        super().__init__()

    def indices(self) -> List[Tuple[int, int]]:
        """
        Returns indices of all grid locations (row, column)
        """
        if self.center_on_origin:
            return [(r, c) for r in range((-self.rows), self.rows + 1)
                           for c in range((-self.cols), self.cols + 1)]
        else:
            return [(r, c) for r in range(0, self.rows)
                           for c in range(0, self.cols)]

    def neighbours(self, grid_location: GridLocation) -> List[GridLocation]:
        """
        Given a GridLocation returns all neighbours of that location
        """
        raise NotImplementedError

    def _is_within_bounds(self, grid_loc: GridLocation) -> bool:
        """
        Checks if GridLocation is within the grids borders 
        """
        top_bound : int = self.cols
        bottom_bound : int = (-self.cols) if self.center_on_origin else 0
        left_bound : int = (-self.rows) if self.center_on_origin else 0
        right_bound : int = self.rows
        return ((left_bound <= grid_loc.col <= right_bound) and
                (top_bound >= grid_loc.row >= bottom_bound))

    def _new_gl(self, row: int, col: int) -> GridLocation:
        return GridLocation(Row(row), Column(col))


class OctagonalGridSystem(BaseGridSystem):
    """
    Octagonal implementation of the AbstractGridSystem
    Each tile (except those on the borders) is connected to
    eight other neighbouring tiles
    """
    directions = [(1, 0), (1, 1), (0, 1), (-1, 1),
                  (-1, 0), (-1, -1), (0, -1), (1, -1)]

    def neighbours(self, grid_loc: GridLocation) -> List[GridLocation]:
        return [self._new_gl(grid_loc.row + r, grid_loc.col + c)
                for (r, c) in OctagonalGridSystem.directions
                if self._is_within_bounds(self._new_gl(grid_loc.row + r,
                                                       grid_loc.col + c))]


class HHexagonalGridSystem(BaseGridSystem):
    """
    Horizonal hexagonal implementation of the AbstractGridSystem
    Each tile (except those on the borders) is connected to
    six other neighbouring tiles.
    Tiles below the horizontal axis of the reference tile
    which are connected via the its diagonal sides have the same 
    y value as the reference.
    """
    directions = [(0, 1), (1, 1), (1, 0), (0, -1), (-1, 0), (-1, 1)]

    def neighbours(self, grid_loc: GridLocation) -> List[GridLocation]:
        return [self._new_gl(grid_loc.row + r, grid_loc.col + c)
                for (r, c) in HHexagonalGridSystem.directions
                if self._is_within_bounds(self._new_gl(grid_loc.row + r,
                                                       grid_loc.col + c))]
