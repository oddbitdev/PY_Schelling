import operator
import random
from typing import Dict, List, Optional, Set, Tuple

from grid_models import Column, GridLocation, OctagonalGridSystem, Row
from tile_model import RandomTileTypeGenerator, Tile, TileSystem, TileType


class World(object):
    def __init__(self, rows: int, cols: int, centered: bool,
                 tile_weights: Dict[TileType, int],
                 tiles: List[Tile]=None) -> None:
        """
        Creates a grid system and a tile system that are used
        to compute the tile movements across the grid
        If the centered parameter is True the generated grid
        system will be centered on the origin (0, 0),
        otherwise the system with the origin on (0, 0) will
        expand only in on the positive x and y axis

        e.g.: given a system of 2 rows and 2 cols

            (-2, 2)  (-1, 2)  (0, 2)  (1, 2)  (2, 2)
            (-2, 1)  (-1, 1)  (0, 1)  (1, 1)  (2, 1)
            (-2, 0)  (-1, 0)  (0, 0)  (1, 0)  (2, 0)
            (-2, -1) (-1, -1) (0, -1) (1, -1) (2, -1)
            (-2, -2) (-1, -2) (0, -2) (1, -2) (2, -2)

        and for a non-centered system of 2 rows and 2 cols

            (2, 0) (1, 2), (2, 2)
            (1, 0) (1, 1), (2, 1)
            (0, 0) (1, 0), (2, 0)

        If no list of tiles is provided the random tile generator
        will be used to generate a random world.
        """
        self.grid : OctagonalGridSystem = OctagonalGridSystem(rows, cols,
                                                              centered)
        self.rtg : RandomTileTypeGenerator = RandomTileTypeGenerator(
            tile_weights)

        indices : List[Tuple[int, int]] = self.grid.indices()

        if tiles:
            self.tile_system = TileSystem(tiles)
        else:
            ts : List[Tile] = [Tile(self.rtg.get_random_tile(),
                                    GridLocation(Row(j[0]), Column(j[1])), i)
                               for i, j in enumerate(indices)]
            self.tile_system = TileSystem(ts)
 
    def run_step(self) -> None:
        """
        For each tile in the tile system the desirability of its current
        location is calculated and then the desirability of its empty
        neighbours. If a better location is available the tiles will
        switch places. In case two or more tiles want to move to the same
        location the one with the lower self desirability will move to the
        new location, otherwise no tile moves.
        """
        movement_matrix : List[Tuple[Tuple[Tile, float], Tile]] = []
        for tile in self.tile_system.tiles_dict.values():
            self_des = self.tile_desirability(tile, tile.tile_type, True)
            des_tile : Optional[Tile] = self.wants_to_move_to_tile(tile)
            if des_tile is not None:
                movement_matrix.append(((tile, self_des), des_tile))
        non_dups : List[Tuple[Tile, Tile]] = self.rem_dups(movement_matrix)
        [self.tile_system.switch_tiles(t[0], t[1]) for t in non_dups]
        return None

    def rem_dups(self,
                 mm: List[Tuple[Tuple[Tile, float],
                                Tile]]) -> List[Tuple[Tile, Tile]]:
        """
        Selects the single tile pairs that want to switch and then 
        removes duplicates from the desirability matrix by figuring which
        tile has the lowest self desirability and allowing it to move to
        the new location, when two or more tiles have the same self
        desirability and want to move to the same location then neither
        will move and will be removed from the matrix.
        """
        known_duplicates : List[Tile] = []
        non_duplicates   : List[Tuple[Tile, Tile]] = []
        conflicts        : Dict[Tile, List[Tuple[Tile, float]]]
        conflicts = {}
        while mm:
            last : Tuple[Tuple[Tile, float], Tile] = mm.pop()
            if last[1] in known_duplicates:
                conflicts[last[1]].append(last[0])
            elif last[1] in [t[1] for t in mm]:
                known_duplicates.append(last[1])
                conflicts[last[1]] = [last[0]]
            else:
                non_duplicates.append((last[0][0], last[1]))
        for t, c in conflicts.items():
            unique : Optional[Tile] = self.unique_min_des(c)
            if unique:
                non_duplicates.append((unique, t))
        return non_duplicates

    def unique_min_des(self,
                       conflicts: List[Tuple[Tile, float]]) -> Optional[Tile]:
        """
        When there are multiple tiles that want to move to another tile
        this method will return the one that has the lowest self desirability,
        If more than one tiles have the same min value of self desirability
        no tile will be returned.
        """
        min_ : Tuple[Tile, float] = min(conflicts, key=operator.itemgetter(1))
        candidates = [t[0] for t in conflicts if t[1] == min_[1]]
        if len(candidates) > 1:
            return None
        else:
            return min_[0]

    def tile_desirability(self, tile: Tile,
                          tile_type: TileType,
                          self_des: bool=False) -> float:
        if tile.tile_type == TileType.Empty and self_des:
            return 0
        ns : List[Tile] = self.tile_neighbours(tile)
        same  = len([t for t in ns if t.tile_type == tile_type])
        empty = len([t for t in ns if t.tile_type == TileType.Empty])
        diff  = len([t for t in ns if t.tile_type != tile_type and
                                      t.tile_type != TileType.Empty])
        same  = same if self_des else (same - 1)
        empty = empty if self_des else (empty + 1)
        return (2 * same - 2 * diff + empty) / (2 * len(ns))

    def desirability_matrix(self, tile: Tile) -> List[Tuple[Tile, float]]:
        ns : List[Tile] = self.tile_neighbours(tile)
        return [(t, self.tile_desirability(t, tile.tile_type))
                for t in ns if t.tile_type == TileType.Empty]

    def wants_to_move_to_tile(self, tile: Tile) -> Optional[Tile]:
        if tile.tile_type == TileType.Empty:
            return None
        self_des : float = self.tile_desirability(tile, tile.tile_type, True)
        des_mat : List[Tuple[Tile, float]]
        des_mat = self.desirability_matrix(tile)
        if not des_mat:
            return None
        max_ : Tuple[Tile, float] = max(des_mat, key=operator.itemgetter(1))
        if max_[1] > self_des:
            return max_[0]
        else:
            return None

    def tile_neighbours(self, tile: Tile) -> List[Tile]:
        ns_loc : List[GridLocation] = self.grid.neighbours(tile.tile_position)
        ns : List[Optional[Tile]]   = [self.tile_system.tile_at_loc(loc)
                                       for loc in ns_loc]
        nsf : List[Tile]            = list(filter(None, ns))
        return nsf
