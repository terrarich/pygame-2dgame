import sys
import os
import pygame

# Allow running as a script: add project root to sys.path
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from game.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    TILE_SIZE,
    TILE_WALL,
    TILE_FLOOR,
    TILE_SHOP,
    TILE_STAIRS,
    COLOR_BG,
    COLOR_WALL,
    COLOR_FLOOR,
    COLOR_PLAYER,
    COLOR_TEXT,
    COLOR_SHOP,
    COLOR_STAIRS,
)
from game.entities import Player
from game.dungeon import Dungeon
from game.ui import draw_hud, draw_inventory_overlay, draw_shop_prompt


def draw_map(surface: pygame.Surface, dungeon: Dungeon) -> None:
    for y in range(dungeon.height):
        for x in range(dungeon.width):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile = dungeon.tiles[y][x]
            if tile == TILE_WALL:
                color = COLOR_WALL
            elif tile == TILE_FLOOR:
                color = COLOR_FLOOR
            elif tile == TILE_SHOP:
                color = COLOR_SHOP
            elif tile == TILE_STAIRS:
                color = COLOR_STAIRS
            else:
                color = COLOR_FLOOR
            surface.fill(color, rect)


def draw_items(surface: pygame.Surface, dungeon: Dungeon) -> None:
    for (x, y), item in dungeon.items_by_pos.items():
        rect = pygame.Rect(x * TILE_SIZE + 8, y * TILE_SIZE + 8, TILE_SIZE - 16, TILE_SIZE - 16)
        surface.fill(item.color, rect)


def draw_player(surface: pygame.Surface, player: Player) -> None:
    x_px, y_px = player.pos_px()
    rect = pygame.Rect(x_px + 4, y_px + 4, TILE_SIZE - 8, TILE_SIZE - 8)
    surface.fill(COLOR_PLAYER, rect)


def game_loop() -> None:
    pygame.init()
    pygame.display.set_caption("Treasure Dungeons")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)

    level = 1
    dungeon = Dungeon(level=level)
    player = Player(x=dungeon.player_start[0], y=dungeon.player_start[1])

    inventory_open = False

    def restart_level(next_level: int) -> None:
        nonlocal dungeon, player, inventory_open, level
        level = next_level
        dungeon = Dungeon(level=level)
        # keep gold, clear inventory
        player.x, player.y = dungeon.player_start
        player.inventory.items.clear()

    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_i:
                    inventory_open = not inventory_open

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        if dx != 0 or dy != 0:
            nx, ny = player.x + dx, player.y + dy
            if dungeon.tile_is_walkable(nx, ny):
                player.x, player.y = nx, ny
                picked = dungeon.try_pick_item(player.x, player.y)
                if picked is not None:
                    player.inventory.add(picked)

        # Interactions
        at_shop = dungeon.tiles[player.y][player.x] == TILE_SHOP
        at_stairs = dungeon.tiles[player.y][player.x] == TILE_STAIRS
        sell_pressed = keys[pygame.K_e]
        if at_shop and sell_pressed:
            if player.inventory.items:
                player.gold += player.inventory.total_value()
                player.inventory.clear()
        if at_stairs and sell_pressed:
            restart_level(level + 1)

        # Render
        screen.fill(COLOR_BG)
        draw_map(screen, dungeon)
        draw_items(screen, dungeon)
        draw_player(screen, player)
        draw_hud(screen, font, player.gold, level)
        draw_shop_prompt(screen, font, at_shop, bool(player.inventory.items))
        if inventory_open:
            draw_inventory_overlay(screen, font, player.inventory)

        pygame.display.flip()


def main() -> None:
    game_loop()


if __name__ == "__main__":
    main()