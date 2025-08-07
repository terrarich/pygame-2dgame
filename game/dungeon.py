import random
from typing import List, Tuple, Dict

from .constants import (
    GRID_WIDTH,
    GRID_HEIGHT,
    TILE_WALL,
    TILE_FLOOR,
    TILE_SHOP,
    TILE_STAIRS,
)
from .entities import Item
from .constants import COLOR_ITEM_COMMON, COLOR_ITEM_RARE, COLOR_ITEM_EPIC


ItemDef = Dict[str, object]

ITEM_POOL: List[ItemDef] = [
    {"name": "Copper Coin", "value": 1, "weight": 30, "color": COLOR_ITEM_COMMON},
    {"name": "Silver Coin", "value": 3, "weight": 20, "color": COLOR_ITEM_COMMON},
    {"name": "Gold Coin", "value": 7, "weight": 15, "color": COLOR_ITEM_RARE},
    {"name": "Jeweled Ring", "value": 20, "weight": 7, "color": COLOR_ITEM_RARE},
    {"name": "Ancient Idol", "value": 50, "weight": 3, "color": COLOR_ITEM_EPIC},
]


def weighted_choice(items: List[ItemDef]) -> ItemDef:
    weights = [i["weight"] for i in items]
    return random.choices(items, weights=weights, k=1)[0]


class Dungeon:
    def __init__(self, level: int = 1, rng_seed: int | None = None) -> None:
        self.level = level
        if rng_seed is not None:
            random.seed(rng_seed)
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.tiles: List[List[int]] = [[TILE_WALL for _ in range(self.width)] for _ in range(self.height)]
        self.items_by_pos: Dict[Tuple[int, int], Item] = {}
        self.player_start: Tuple[int, int] = (1, 1)
        self.shop_pos: Tuple[int, int] | None = None
        self.stairs_pos: Tuple[int, int] | None = None
        self._generate_map()
        self._place_shop_and_stairs()
        self._scatter_items()

    def _carve_room(self, x: int, y: int, w: int, h: int) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < self.width and 0 <= yy < self.height:
                    self.tiles[yy][xx] = TILE_FLOOR

    def _carve_h_corridor(self, x1: int, x2: int, y: int) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = TILE_FLOOR

    def _carve_v_corridor(self, y1: int, y2: int, x: int) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = TILE_FLOOR

    def _generate_map(self) -> None:
        rooms: List[Tuple[int, int, int, int]] = []
        max_rooms = 12
        min_size, max_size = 4, 8

        for _ in range(max_rooms):
            w = random.randint(min_size, max_size)
            h = random.randint(min_size, max_size)
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)

            new_room = (x, y, w, h)
            # Check overlap
            failed = False
            for other in rooms:
                if not (x + w + 1 < other[0] or x - 1 > other[0] + other[2] or y + h + 1 < other[1] or y - 1 > other[1] + other[3]):
                    failed = True
                    break
            if failed:
                continue

            self._carve_room(x, y, w, h)
            if rooms:
                # connect to previous room center
                prev_x, prev_y = self._room_center(rooms[-1])
                new_x, new_y = self._room_center(new_room)
                if random.random() < 0.5:
                    self._carve_h_corridor(prev_x, new_x, prev_y)
                    self._carve_v_corridor(prev_y, new_y, new_x)
                else:
                    self._carve_v_corridor(prev_y, new_y, prev_x)
                    self._carve_h_corridor(prev_x, new_x, new_y)
            else:
                self.player_start = self._room_center(new_room)
            rooms.append(new_room)

        if not rooms:
            # fallback carve central area
            self._carve_room(self.width // 3, self.height // 3, self.width // 3, self.height // 3)
            self.player_start = (self.width // 2, self.height // 2)

        # Ensure borders are walls
        for x in range(self.width):
            self.tiles[0][x] = TILE_WALL
            self.tiles[self.height - 1][x] = TILE_WALL
        for y in range(self.height):
            self.tiles[y][0] = TILE_WALL
            self.tiles[y][self.width - 1] = TILE_WALL

    def _room_center(self, room: Tuple[int, int, int, int]) -> Tuple[int, int]:
        x, y, w, h = room
        return x + w // 2, y + h // 2

    def _random_floor_tile(self) -> Tuple[int, int]:
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.tiles[y][x] == TILE_FLOOR and (x, y) != self.player_start and (x, y) not in self.items_by_pos:
                return x, y

    def _place_shop_and_stairs(self) -> None:
        # Place shop near player start
        px, py = self.player_start
        candidates = [
            (px + dx, py + dy)
            for dx in range(-3, 4)
            for dy in range(-3, 4)
            if not (dx == 0 and dy == 0)
        ]
        random.shuffle(candidates)
        for (x, y) in candidates:
            if 1 <= x < self.width - 1 and 1 <= y < self.height - 1 and self.tiles[y][x] == TILE_FLOOR:
                self.tiles[y][x] = TILE_SHOP
                self.shop_pos = (x, y)
                break
        # Place stairs far from player start
        far_candidates = [
            (x, y)
            for y in range(1, self.height - 1)
            for x in range(1, self.width - 1)
            if self.tiles[y][x] == TILE_FLOOR and abs(x - px) + abs(y - py) > (self.width + self.height) // 4
        ]
        if far_candidates:
            self.stairs_pos = random.choice(far_candidates)
            sx, sy = self.stairs_pos
            self.tiles[sy][sx] = TILE_STAIRS

    def _scatter_items(self) -> None:
        num_items = 18 + self.level * 2
        for _ in range(num_items):
            x, y = self._random_floor_tile()
            base = weighted_choice(ITEM_POOL)
            # slightly scale value by level
            value = int(base["value"] * (1.0 + 0.1 * (self.level - 1)))
            item = Item(name=base["name"], value=value, color=base["color"]) 
            self.items_by_pos[(x, y)] = item

    def tile_is_walkable(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.tiles[y][x] in (TILE_FLOOR, TILE_SHOP, TILE_STAIRS)

    def try_pick_item(self, x: int, y: int) -> Item | None:
        return self.items_by_pos.pop((x, y), None)