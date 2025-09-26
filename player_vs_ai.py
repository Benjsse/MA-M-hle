import sys, pygame, asyncio, os
import time
from ai_heuristic import (
    positions, Mills, get_neighbors, choose_ai_move, choose_removal
)

pygame.init()

DIFFICULTY_OVERRIDE = None

size = width, height = 800, 800
black = 0, 0, 0
white = 255, 255, 255
grey = 128, 128, 128
red = 255, 0, 0

outerrec = [(200,200),(200,400),(200,600),(400,600),(600,600),(600,400),(600,200),(400,200)]
middlerec = [(250,250),(250,400),(250,550),(400,550),(550,550),(550,400),(550,250),(400,250)]
innerrec = [(300,300),(300,400),(300,500),(400,500),(500,500),(500,400),(500,300),(400,300)]
firstline = [(200,400),(250,400),(300,400)]
secondline= [(600,400),(550,400),(500,400)]
thirdline = [(400,500),(400,550),(400,600)]
fourthline = [(400,200),(400,250),(400,300)]

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Mühlespiel – Spieler (Weiss) vs KI (Rot)")
font_big = pygame.font.SysFont(None, 60)
font_small = pygame.font.SysFont(None, 28)

def board():
    pygame.draw.lines(screen, grey, True, outerrec, width=4)
    pygame.draw.lines(screen, grey, True, middlerec, width=4)
    pygame.draw.lines(screen, grey, True, innerrec, width=4)
    pygame.draw.lines(screen, grey, False, [(200,400),(300,400)], width=4)
    pygame.draw.lines(screen, grey, False, [(600,400),(500,400)], width=4)
    pygame.draw.lines(screen, grey, False, [(400,500),(400,600)], width=4)
    pygame.draw.lines(screen, grey, False, [(400,200),(400,300)], width=4)

def red_stone(position):
    pygame.draw.circle(screen, red, position, 10, 0)

def white_stone(position):
    pygame.draw.circle(screen, white, position, 10, 0)

def get_nearest_position(mouse_pos, threshold=10):
    for pos in positions:
        dx = mouse_pos[0] - pos[0]
        dy = mouse_pos[1] - pos[1]
        if dx*dx + dy*dy <= threshold*threshold:
            return pos
    return None

# Spielzustand
state = {
    "occupied": {},          # {(x,y): "white"/"red"}
    "placing_phase": True,
    "white_placed": 0,
    "red_placed": 0,
}

# Hilfsvariablen
move_count_without_mill = 0
positions_history = []
current_turn = 'white'
stones_placed = 0
selected_stone = None

removal_mode = False
removal_selection = None

game_over = False
game_over_text = ["", ""]  # [headline, reason]

def end_game(headline, reason):
    global game_over, game_over_text
    game_over = True
    game_over_text = [headline, reason]
    print(headline, reason)

def draw_top_text(lines):
    overlay_height = 140
    overlay = pygame.Surface((width, overlay_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))  # halbtransparent
    screen.blit(overlay, (0, 0))

    y = 20
    for text, big in lines:
        surf = (font_big if big else font_small).render(text, True, white)
        rect = surf.get_rect(center=(width//2, y))
        screen.blit(surf, rect)
        y += 45 if big else 28

def reset_game():
    global move_count_without_mill, positions_history, current_turn, stones_placed, selected_stone
    global removal_mode, removal_selection, game_over, game_over_text, state
    state = {
        "occupied": {},
        "placing_phase": True,
        "white_placed": 0,
        "red_placed": 0,
    }
    move_count_without_mill = 0
    positions_history = []
    current_turn = 'white'
    stones_placed = 0
    selected_stone = None
    removal_mode = False
    removal_selection = None
    game_over = False
    game_over_text = ["", ""]

def snapshot_and_draw_rules():
    # 50-Züge-Regel und Stellungswiederholung
    global positions_history
    positions_snapshot = tuple(sorted(state["occupied"].items()))
    positions_history.append(positions_snapshot)
    if positions_history.count(positions_snapshot) >= 3:
        end_game("Unentschieden!", "Die gleiche Stellung wurde dreimal erreicht.")
        return True
    if move_count_without_mill >= 50:
        end_game("Unentschieden!", "Nach 50 Zügen wurde keine Mühle gebildet.")
        return True
    return False

def check_loss_no_moves(player):
    # Keine Züge (in Zugphase & nicht fliegen) -> Gegner gewinnt
    from ai_heuristic import generate_moves, can_fly, opponent
    if not state["placing_phase"]:
        moves = generate_moves(state, player)
        if len(moves) == 0 and not can_fly(state, player):
            win_text = "Weiss gewinnt!" if player == "red" else "Rot gewinnt!"
            end_game(win_text, "Gegner hat keine gültigen Züge mehr.")
            return True
    return False

def apply_and_handle_mill(player, mv):
    global move_count_without_mill
    from ai_heuristic import apply_move, forms_mill

    s2, formed = apply_move(state, mv, player)
    # state übernehmen
    state.update(s2)

    if formed:
        move_count_without_mill = 0
        return True
    else:
        move_count_without_mill += 1
        return False

def handle_ai_turn(depth):
    global current_turn
    from ai_heuristic import opponent
    if game_over:
        return
    # KI (rot)
    mv = choose_ai_move(state, "red", depth)
    if mv is None:
        end_game("Weiss gewinnt!", "Rot hat keinen Zug.")
        return
    formed = apply_and_handle_mill("red", mv)
    if formed:
        # KI entfernt automatisch einen weissen Stein
        rem = choose_removal(state, "red")
        if rem is not None and rem in state["occupied"]:
            del state["occupied"][rem]
    # Übergang in Zugphase?
    if state["white_placed"] + state["red_placed"] >= 18:
        state["placing_phase"] = False
    # Siegbedingungen (Steinzahl)
    white_count = sum(1 for p,c in state["occupied"].items() if c == "white")
    red_count   = sum(1 for p,c in state["occupied"].items() if c == "red")
    if not state["placing_phase"]:
        if white_count < 3:
            end_game("Rot gewinnt!", "Weiss hat weniger als 3 Steine.")
            return
        if red_count < 3:
            end_game("Weiss gewinnt!", "Rot hat weniger als 3 Steine.")
            return
    if check_loss_no_moves("white"):
        return
    if not game_over:
        current_turn = "white"

def difficulty_to_depth():
    # Mapping: leicht -> 1, mittel -> 3, schwer -> 4
    if DIFFICULTY_OVERRIDE is not None:
        return int(DIFFICULTY_OVERRIDE)
    import os
    diff = os.getenv("DIFFICULTY", "leicht").strip().lower()
    if diff.startswith("mit"): return 3
    elif diff.startswith("sch"): return 5
    return 1

async def main(depth=None):
    global current_turn, stones_placed, selected_stone, removal_mode, removal_selection, move_count_without_mill, DIFFICULTY_OVERRIDE

    if depth is not None:
        DIFFICULTY_OVERRIDE = depth

    depth = difficulty_to_depth()

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()

            if game_over:
                continue

            # Spieler entfernt roten Stein nach Mühle
            if removal_mode:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    pos = get_nearest_position(mouse_pos)
                    if pos is None:
                        continue
                    if pos in state["occupied"] and state["occupied"][pos] == "red":
                        # prüfen ob aus einer Mühle und ob es Ausweichsteine gibt
                        is_in_mill = False
                        for mill in Mills:
                            if pos in mill and all(p in state["occupied"] and state["occupied"][p] == "red" for p in mill):
                                is_in_mill = True
                                break
                        red_stones = [p for p,c in state["occupied"].items() if c == "red"]
                        red_mill_stones = [
                            p for p in red_stones
                            if any(p in mill and all(q in state['occupied'] and state['occupied'][q] == 'red' for q in mill) for mill in Mills)
                        ]
                        if is_in_mill and len(red_stones) != len(red_mill_stones):
                            # Nicht erlaubt, es gibt rote Steine ausserhalb von Mühlen
                            continue
                        del state["occupied"][pos]
                        removal_mode = False
                        # Nach Entfernen ist Rot am Zug (AI)
                        current_turn = "red"
                        if snapshot_and_draw_rules():  # vllt. Remis
                            continue
                        handle_ai_turn(depth)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and current_turn == "white":
                mouse_pos = pygame.mouse.get_pos()
                pos = get_nearest_position(mouse_pos)
                if pos is None:
                    continue

                if state["placing_phase"]:
                    if pos not in state["occupied"]:
                        # Weiss platziert
                        state["occupied"][pos] = "white"
                        state["white_placed"] += 1
                        stones_placed += 1
                        formed = False
                        for mill in Mills:
                            if pos in mill and all(p in state["occupied"] and state["occupied"][p] == "white" for p in mill):
                                formed = True; break
                        if formed:
                            removal_mode = True
                            move_count_without_mill = 0
                        else:
                            move_count_without_mill += 1
                            current_turn = "red"
                            if snapshot_and_draw_rules():
                                continue
                            # Falls alle 18 Steine platziert wurden, Phase umschalten
                            if state["white_placed"] + state["red_placed"] >= 18:
                                state["placing_phase"] = False
                            handle_ai_turn(depth)
                        if state["white_placed"] + state["red_placed"] >= 18:
                            state["placing_phase"] = False
                else:
                    # Zugphase, Auswahl und Bewegung wie in main.py
                    global_selected_before = selected_stone
                    if selected_stone is None:
                        if pos in state["occupied"] and state["occupied"][pos] == "white":
                            selected_stone = pos
                    else:
                        # darf ich dorthin? (fliegen bei 3 Steinen)
                        white_positions = [p for p,c in state["occupied"].items() if c == "white"]
                        can_fly = (len(white_positions) == 3)
                        if pos not in state["occupied"] and (can_fly or pos in get_neighbors(selected_stone)):
                            # bewegen
                            del state["occupied"][selected_stone]
                            state["occupied"][pos] = "white"
                            selected_stone = None
                            formed = False
                            for mill in Mills:
                                if pos in mill and all(p in state["occupied"] and state["occupied"][p] == "white" for p in mill):
                                    formed = True; break
                            if formed:
                                removal_mode = True
                                move_count_without_mill = 0
                            else:
                                move_count_without_mill += 1
                                current_turn = "red"
                                if snapshot_and_draw_rules():
                                    continue
                                handle_ai_turn(depth)
                            # Siegbedingungen nach menschlichem Zug prüfen
                            if not state["placing_phase"]:
                                white_count = len([1 for p,c in state["occupied"].items() if c == "white"])
                                red_count = len([1 for p,c in state["occupied"].items() if c == "red"])
                                if white_count < 3:
                                    end_game("Rot gewinnt!", "Weiss hat weniger als 3 Steine.")
                                elif red_count < 3:
                                    end_game("Weiss gewinnt!", "Rot hat weniger als 3 Steine.")
                        elif pos == selected_stone:
                            selected_stone = None

        # Zeichnen
        screen.fill(black)
        board()
        for p, col in state["occupied"].items():
            if col == "white":
                white_stone(p)
            else:
                red_stone(p)

        if selected_stone:
            pygame.draw.circle(screen, (0,255,0), selected_stone, 10, 2)

        # Top Bar mit Status & Schwierigkeit
        diff_str = os.getenv("DIFFICULTY", "leicht").capitalize()
        if game_over:
            draw_top_text([
                (game_over_text[0], True),
                (game_over_text[1], False),
                (f"Schwierigkeit: {diff_str}  •  Drücke R für Neustart", False),
            ])
        else:
            draw_top_text([
                (f"Am Zug: {'Weiss' if current_turn=='white' else 'Rot (KI)'}", False),
                (f"Platzierphase: {'Ja' if state['placing_phase'] else 'Nein'}", False),
                (f"Schwierigkeit: {diff_str}  •  Drücke R für Neustart", False),
            ])

        pygame.display.flip()
        pygame.time.delay(100)
        clock.tick(60)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
