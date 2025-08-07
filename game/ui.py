import pygame
from typing import List, Tuple

from .constants import (
    TILE_SIZE,
    COLOR_TEXT,
    COLOR_HUD_BG,
    COLOR_HUD_BG_ALPHA,
    COLOR_SHOP,
)
from .entities import Inventory


def draw_text(surface: pygame.Surface, text: str, pos: Tuple[int, int], font: pygame.font.Font, color=COLOR_TEXT) -> None:
    img = font.render(text, True, color)
    surface.blit(img, pos)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, gold: int, level: int) -> None:
    draw_text(surface, f"Gold: {gold}", (10, 8), font)
    draw_text(surface, f"Level: {level}", (10, 32), font)


def draw_inventory_overlay(surface: pygame.Surface, font: pygame.font.Font, inventory: Inventory) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, COLOR_HUD_BG_ALPHA))
    surface.blit(overlay, (0, 0))

    draw_text(surface, "Inventory (I to close)", (40, 40), font)
    y = 80
    if not inventory.items:
        draw_text(surface, "(empty)", (40, y), font)
        return

    for name, count, single_value in sorted(inventory.counts_by_name()):
        draw_text(surface, f"{name} x{count} — {single_value} each", (40, y), font)
        y += 28


def draw_shop_prompt(surface: pygame.Surface, font: pygame.font.Font, at_shop: bool, can_sell: bool) -> None:
    if not at_shop:
        return
    text = "Press E to sell all" if can_sell else "Inventory empty"
    prompt = pygame.Surface((320, 40))
    prompt.fill(COLOR_SHOP)
    surface.blit(prompt, (surface.get_width() - 340, 8))
    draw_text(surface, text, (surface.get_width() - 320, 16), font)