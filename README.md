## Treasure Dungeons (Pygame)

A simple 2D dungeon-looting game built with Pygame.
- Explore the dungeon
- Pick up items with different values
- Visit the shop to sell your loot for gold
- Descend stairs to new levels for more treasure

### Setup
1. Python 3.9+
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Run
```bash
python -m game.main
```

### Controls
- Move: WASD or Arrow Keys
- Interact (Sell at Shop / Use Stairs): E
- Toggle Inventory Overlay: I
- Quit: ESC or window close

### Notes
- Items have different names, rarities, and sell values
- Selling at the shop converts inventory into gold
- Each new level randomizes a fresh dungeon layout and loot