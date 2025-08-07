from dataclasses import dataclass, field
from typing import List, Tuple, Optional

from .constants import TILE_SIZE


@dataclass
class Item:
    name: str
    value: int
    color: Tuple[int, int, int]


@dataclass
class Inventory:
    items: List[Item] = field(default_factory=list)

    def add(self, item: Item) -> None:
        self.items.append(item)

    def total_value(self) -> int:
        return sum(i.value for i in self.items)

    def clear(self) -> None:
        self.items.clear()

    def counts_by_name(self) -> List[Tuple[str, int, int]]:
        summary = {}
        for i in self.items:
            if i.name not in summary:
                summary[i.name] = {"count": 0, "value": i.value}
            summary[i.name]["count"] += 1
        # returns list of (name, count, single_value)
        return [(n, d["count"], d["value"]) for n, d in summary.items()]


@dataclass
class Player:
    x: int
    y: int
    gold: int = 0
    inventory: Inventory = field(default_factory=Inventory)

    def pos_px(self) -> Tuple[int, int]:
        return self.x * TILE_SIZE, self.y * TILE_SIZE