import sys
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mühlespiel – Hauptmenü")

# Farben
BLACK = (10, 10, 14)
WHITE = (240, 240, 240)
GREY  = (120, 120, 130)
BLUE  = (0, 120, 255)
BLUE_DARK = (0, 70, 180)

# Typo
FONT_TITLE = pygame.font.SysFont(None, 64)
FONT_ITEM  = pygame.font.SysFont(None, 40)
FONT_HINT  = pygame.font.SysFont(None, 24)

MENU_ITEMS = [
    ("PvP ", "pvp"),
    ("Leicht", "leicht"),
    ("Mittel", "mittel"),
    ("Schwer", "schwer"),
]

def draw_centered_text(text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    screen.blit(surf, rect)
    return rect


def run_menu():
    clock = pygame.time.Clock()
    selected_idx = 0
    title_y = 180
    first_item_y = 300
    item_gap = 64

    while True:
        hover_idx = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_idx = (selected_idx - 1) % len(MENU_ITEMS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_idx = (selected_idx + 1) % len(MENU_ITEMS)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return MENU_ITEMS[selected_idx][1]
                elif event.key == pygame.K_ESCAPE:
                    return None

        screen.fill(BLACK)
        draw_centered_text("Mühlespiel",       FONT_TITLE, WHITE, title_y)
        draw_centered_text("Wähle einen Modus", FONT_HINT, GREY,   title_y + 48)
    
        mouse_pos = pygame.mouse.get_pos()
        for i, (label, key) in enumerate(MENU_ITEMS):
            y = first_item_y + i * item_gap
            is_selected = (i == selected_idx)
            rect = draw_centered_text(label, FONT_ITEM, (BLUE if is_selected else WHITE), y)
            if rect.collidepoint(mouse_pos):
                hover_idx = i
                underline_start = (rect.left, rect.bottom + 4)
                underline_end   = (rect.right, rect.bottom + 4)
                pygame.draw.line(screen, BLUE_DARK, underline_start, underline_end, 3)

        if hover_idx is not None:
            selected_idx = hover_idx
            if pygame.mouse.get_pressed(3)[0]:
                pygame.time.delay(120)
                return MENU_ITEMS[selected_idx][1]

        draw_centered_text("↑/↓ auswählen • Enter bestätigen • ESC beenden", FONT_HINT, GREY, HEIGHT - 60)
        pygame.display.flip()
        clock.tick(60)

def launch_from_menu():
    choice = run_menu()
    if choice is None:
        pygame.quit(); sys.exit(0)

    if choice == "leicht":
        # PvP kommt später – wir starten noch nicht.
        pygame.quit(); sys.exit(0)
    if choice == "pvp":
        # PvP kommt später – wir starten noch nicht.
        import main
    if choice == "mittel":
        pygame.quit(); sys.exit(0)
    if choice == "schwer":
        pygame.quit(); sys.exit(0)
    if choice == "unmoeglich":
        pygame.quit(); sys.exit(0)

if __name__ == "__main__":
    launch_from_menu()
