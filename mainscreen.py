# mainscreen.py  (web-tauglich, ohne subprocess; robustes Fallback für depth)
import sys
import os
import pygame
import asyncio
import inspect

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mühlespiel – Hauptmenü (Web-fähig)")

# Farben
BLACK = (10, 10, 14)
WHITE = (240, 240, 240)
GREY  = (120, 120, 130)
BLUE  = (0, 120, 255)

FONT_TITLE = pygame.font.SysFont(None, 64)
FONT_ITEM  = pygame.font.SysFont(None, 40)
FONT_HINT  = pygame.font.SysFont(None, 24)

MENU_ITEMS = [
    ("Spieler vs Spieler (PvP)", "pvp"),
    ("Gegen KI – leicht",        ("ai", 1)),
    ("Gegen KI – mittel",        ("ai", 3)),
    ("Gegen KI – schwer",        ("ai", 6)),
]

DIFF_MAP = {1: "leicht", 3: "mittel", 6: "schwer"}

def draw_centered_text(text, font, y, color=WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    screen.blit(surf, rect)

def menu_loop():
    selected_idx = 0
    blink = 0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    pygame.quit(); sys.exit(0)
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_idx = (selected_idx - 1) % len(MENU_ITEMS)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_idx = (selected_idx + 1) % len(MENU_ITEMS)
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return MENU_ITEMS[selected_idx][1]

        screen.fill(BLACK)
        draw_centered_text("Mühlespiel", FONT_TITLE, 120)
        draw_centered_text("Wähle einen Modus", FONT_ITEM, 180, GREY)

        base_y = 280
        for i, (label, _val) in enumerate(MENU_ITEMS):
            color = BLUE if i == selected_idx and (blink // 20) % 2 == 0 else WHITE
            draw_centered_text(label, FONT_ITEM, base_y + i * 60, color)

        draw_centered_text("↑/↓ Navigieren • Enter Start • Esc Beenden", FONT_HINT, HEIGHT - 40, GREY)
        pygame.display.flip()
        blink += 1
        clock.tick(60)

async def run_pvp():
    import main as pvp_module
    # pvp_module.main ist async -> direkt awaiten
    await pvp_module.main()

async def run_ai(depth_choice: int):
    import player_vs_ai as ai_module

    # 1) Wenn player_vs_ai.main(depth=...) unterstützt -> benutze es
    try:
        sig = inspect.signature(ai_module.main)
        if "depth" in sig.parameters:
            await ai_module.main(depth=depth_choice)
            return
    except (AttributeError, ValueError, TypeError):
        # Falls main nicht inspizierbar ist, gehe zu Fallback 2)
        pass

    # 2) Fallback: Umgebungsvariable setzen, wenn depth-Param fehlt
    os.environ["DIFFICULTY"] = DIFF_MAP.get(depth_choice, "leicht")
    await ai_module.main()  # ohne Argumente

async def main():
    """Web-tauglicher Entry-Point: Kein subprocess, keine os.exec*."""
    while True:
        choice = menu_loop()
        if choice == "pvp":
            await run_pvp()
        elif isinstance(choice, tuple) and choice[0] == "ai":
            await run_ai(choice[1])
        # Nach Spielende zurück ins Menü (Loop läuft weiter)

if __name__ == "__main__":
    asyncio.run(main())

