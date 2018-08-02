import operator
import random
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from grid_models import GridLocation


class TileType(Enum):
    Empty = 1
    Green = 2
    Blue = 3


class RandomTileTypeGenerator(object):
    """
    Given tile types and their respective weights the RTTG can
    generate random tile types on demand
    """
    def __init__(self, type_weight_dict: Dict[TileType, int]) -> None:
        self.type_weight_dict : Dict[TileType, int] = type_weight_dict
        self.type_prob : Dict[TileType, Tuple[float, float]]
        self.type_prob = self._norm_weight_prob()

    def _norm_weight_prob(self) -> Dict[TileType, Tuple[float, float]]:
        """
        Function normalizes the weights for the tile types and produces
        a probability range for each tile type

        e.g.: Given a weight dict like
        {Empty: 5, Green: 3, Blue: 2}
        the function will produce the following probability range for 
        the given tile types:
        {Blue: (0, 0.2), Green: (0.2, 0.5), Empty: (0.5, 1)}
        """
        norm = sum(self.type_weight_dict.values())
        dct : Dict[TileType, float]
        dct = {t: v/norm for (t, v) in self.type_weight_dict.items()}
        sorted_t_list : List[Tuple[TileType, float]]
        sorted_t_list = sorted(dct.items(), key=operator.itemgetter(1))
        prob_list     : List[float]
        prob_list     = [v[1] for v in sorted_t_list]
        range_list    : List[List[float]]
        range_list    = [prob_list[0:i] for i in range(len(prob_list))]
        markers       : List[float]
        markers       = list(map(sum, range_list)) + [1]
        ranges        : List[Tuple[float, float]]
        ranges        = list(zip(markers, markers[1:]))
        return {sorted_t_list[i][0]: ranges[i] for i in range(len(dct))}

    def get_random_tile(self) -> TileType:
        """
        Gets a random number in the range (0, 1) and returns the
        tile type with the probability range that contains that number 

        e.g.: given a tile type probability range like
        {Blue: (0, 0.2), Green: (0.2, 0.5), Empty: (0.5, 1)}
        and for a random number of 0.34356
        the function will return the Green tile type
        """
        r = random.random()
        for tile_type, prob_range in self.type_prob.items():
            if prob_range[0] <= r <= prob_range[1]:
                return tile_type
        return TileType.Empty 


class Tile(object):
    def __init__(self,
                 tile_type: TileType,
                 tile_position: GridLocation,
                 tile_id: int) -> None:
        self.tile_type     : TileType     = tile_type
        self.tile_position : GridLocation = tile_position
        self.tile_id       : int          = tile_id

    def __eq__(self, other) -> bool:
        return self.tile_id == other.tile_id

    def __hash__(self) -> int:
        return hash(self.tile_position)

    def __repr__(self) -> str:
        return ("Tile type: " + str(self.tile_type) +
                " | Tile position: " + str(self.tile_position) +
                " | Tile id: " + str(self.tile_id))


class TileSystem(object):
    def __init__(self, tiles: List[Tile]) -> None:
        self.tiles_dict : Dict[GridLocation, Tile]
        self.tiles_dict = {t.tile_position: t for t in tiles}

    def tile_at_loc(self, loc: GridLocation) -> Optional[Tile]:
        return self.tiles_dict.get(loc, None)
    
    def tile_by_id(self, tile_id: int) -> Optional[Tile]:
        for tile in self.tiles_dict.values():
            if tile.tile_id == tile_id:
                return tile
        return None

    def switch_tiles(self, t1: Tile, t2: Tile) -> None:
        t1.tile_type, t2.tile_type = t2.tile_type, t1.tile_type
        t1.tile_id  , t2.tile_id   = t2.tile_id  , t1.tile_id
        return None

    def __repr__(self) -> str:
        return str(self.tiles_dict.values())
