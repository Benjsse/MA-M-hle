import sys, pygame, asyncio
pygame.init()

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
# alle Positionen auf dem Muehlespielbrett
positions = outerrec + middlerec + innerrec

# alle belegten Positionen 
occupied = {}

Mill1 = [(200,200),(200,400),(200,600)]
Mill2 = [(200,600),(400,600),(600,600)]
Mill3 = [(600,600),(600,400),(600,200)]
Mill4 = [(600,200),(400,200),(200,200)]
Mill5 = firstline
Mill6 = secondline
Mill7 = thirdline
Mill8 = fourthline
Mill9 = [(250,250),(250,400),(250,550)]
Mill10 = [(250,550),(400,550),(550,550)]
Mill11 = [(550,550),(550,400),(550,250)]
Mill12 = [(550,250),(400,250),(250,250)]
Mill13 = [(300,300),(300,400),(300,500)]
Mill14 = [(300,500),(400,500),(500,500)]
Mill15 = [(500,500),(500,400),(500,300)]
Mill16 = [(500,300),(400,300),(300,300)]
# alle Mühlen

Mills = [Mill1, Mill2, Mill3, Mill4, Mill5, Mill6, Mill7, Mill8, Mill9, Mill10, Mill11, Mill12, Mill13, Mill14, Mill15, Mill16]

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Mühlespiel")
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

def get_neighbors(pos):
    
    neighbors = set()

    def add_from_list(lst, allow_wrap):
        if pos not in lst:
            return
        idx = lst.index(pos)

        # vorheriger
        if idx > 0:
            neighbors.add(lst[idx - 1])
        elif allow_wrap:
            neighbors.add(lst[-1])

        # nächster
        if idx < len(lst) - 1:
            neighbors.add(lst[idx + 1])
        elif allow_wrap:
            neighbors.add(lst[0])

    # Ringe (mit Wrap)
    add_from_list(outerrec, True)
    add_from_list(middlerec, True)
    add_from_list(innerrec, True)

    # Verbindungs­linien (ohne Wrap)
    add_from_list(firstline,  False)
    add_from_list(secondline, False)
    add_from_list(thirdline,  False)
    add_from_list(fourthline, False)

    return list(neighbors)
# Wessen Zug ist es?
move_count_without_mill = 0
positions_history = []
white_placed = 0
red_placed = 0

def check_game_status():
    global move_count_without_mill, positions_history, white_placed, red_placed

    # Status Ausgabe für ehlersuche
    print("Aktueller Status:")
    print("White Placed:", white_placed)
    print("Red Placed:", red_placed)
    print("Occupied:", occupied)
    print("Move Count Without Mill:", move_count_without_mill)

    # Zähle die Steine der Spieler
    white_stones = [pos for pos in occupied if occupied[pos] == 'white']
    red_stones = [pos for pos in occupied if occupied[pos] == 'red']

    # Überprüfen, ob ein Spieler weniger als 3 Steine hat (nur wenn beide Spieler mindestens 9 Steine platziert haben)
    
    if len(white_stones) < 3 and placing_phase == False:
        end_game("Rot gewinnt!", "Weiss hat weniger als 3 Steine.")
        return
    if len(red_stones) < 3 and placing_phase == False:
        end_game("Weiss gewinnt!", "Rot hat weniger als 3 Steine.")
        return

        # Überprüfen, ob ein Spieler keine gültigen Züge mehr machen kann
        white_moves = ( (len(white_stones) == 3 and any(p not in occupied for p in positions)) or any(
            pos for pos in white_stones if any(neighbor not in occupied for neighbor in get_neighbors(pos))
        ) )
        red_moves = ( (len(red_stones) == 3 and any(p not in occupied for p in positions)) or any(
            pos for pos in red_stones if any(neighbor not in occupied for neighbor in get_neighbors(pos))
        ) )
        if not white_moves and not red_moves:
            print("Unentschieden! Beide Spieler können keine Züge mehr machen.")
            return
        if not white_moves:
            print("Red gewinnt! White kann keine Züge mehr machen.")
            return
        if not red_moves:
            print("White gewinnt! Red kann keine Züge mehr machen.")
            return

    # Prüfen, ob nach 20 Zügen keine Mühle gebildet wurde
    if move_count_without_mill >= 50:
        print("Unentschieden! Nach 20 Zügen wurde keine Mühle gebildet.")
        return
    # Prüfen, ob die gleiche Stellung dreimal erreicht wurde
    positions_snapshot = tuple(sorted(occupied.items()))  # Aktuelle Stellung der Steine
    positions_history.append(positions_snapshot)
    if positions_history.count(positions_snapshot) >= 3:
        print("Unentschieden! Die gleiche Stellung wurde dreimal erreicht.")
        return

game_over = False
game_over_text = ["", ""]  # [headline, reason]

def end_game(headline, reason):
    global game_over, game_over_text
    game_over = True
    game_over_text = [headline, reason]
    print(headline, reason)

def draw_top_text(lines):
    overlay_height = 120
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
    global occupied, move_count_without_mill, positions_history, white_placed, red_placed
    global current_turn, stones_placed, placing_phase, selected_stone, removal_mode, removal_selection
    global game_over, game_over_text

    occupied.clear()
    move_count_without_mill = 0
    positions_history = []
    white_placed = 0
    red_placed = 0

    current_turn = 'white'
    stones_placed = 0
    placing_phase = True
    selected_stone = None

    removal_mode = False
    removal_selection = None

    game_over = False
    game_over_text = ["", ""]

current_turn = 'white'
stones_placed = 0
placing_phase = True
selected_stone = None # für die Zugphase des Spiels

removal_mode = False
removal_selection = None

# game loop
async def main():
    while True:
        global current_turn, stones_placed, placing_phase, selected_stone, removal_mode, removal_selection, white_placed, red_placed, move_count_without_mill
        global occupied, positions_history
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
             # Neustart mit R
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()

            # wenn das Spiel vorbei ist, Eingaben (ausser R/QUIT) ignorieren
            if game_over:
                continue
            if removal_mode:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    pos = get_nearest_position(mouse_pos)
                    if pos is None:
                        continue
                    # Überprüfen, ob der Stein entfernt werden kann
                    if pos in occupied and occupied[pos] != current_turn:
                        # Prüfen, ob der Stein Teil einer Mühle ist
                        is_in_mill = False
                        for mill in Mills:
                            if pos in mill and all(p in occupied and occupied[p] == occupied[pos] for p in mill):
                                is_in_mill = True
                                break
                        # Nur freie Steine können entfernt werden, es sei denn, alle Steine des Gegners sind in Mühlen
                        opponent_stones = [p for p in occupied if occupied[p] != current_turn]
                        opponent_mill_stones = [
                            p for p in opponent_stones
                            if any(p in mill and all(q in occupied and occupied[q] == occupied[p] for q in mill) for mill in Mills)
                        ]
                        if is_in_mill and len(opponent_stones) != len(opponent_mill_stones):
                            print("Ungültige Auswahl. Steine aus einer Mühle können nicht entfernt werden.")
                            continue
                        # Entfernen des Steins
                        removal_selection = pos
                        print("Gegnerischer Stein ausgewählt:", removal_selection)
                        del occupied[pos]
                        removal_mode = False
                        check_game_status()
                        current_turn = 'red' if current_turn == 'white' else 'white'
                    else:
                        print("Ungültige Auswahl. Wähle einen gegnerischen Stein.")
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                pos = get_nearest_position(mouse_pos)
                if pos is None:
                    continue
                if placing_phase:
                    if pos not in occupied:
                        occupied[pos] = current_turn
                        stones_placed += 1
                        if current_turn == 'white':
                            white_placed += 1  # Zähler für weisse Steine erhöhen
                        else:
                            red_placed += 1  # Zähler für rote Steine erhöhen
                        for mill in Mills:
                            if pos in mill and all(p in occupied and occupied[p] == current_turn for p in mill):
                                removal_mode = True
                                print("Mühle gebildet! Entferne einen Stein des Gegners.")
                                move_count_without_mill = 0  # Zähler zurücksetzen, wenn eine Mühle gebildet wird
                                break
                        if not removal_mode:
                            move_count_without_mill += 1  # Zähler erhöhen, wenn keine Mühle gebildet wird
                            current_turn = 'red' if current_turn == 'white' else 'white'
                        if stones_placed >= 18:
                            placing_phase = False
                        check_game_status()
                else:
                    if selected_stone is None:
                        # Spieler wählt einen Stein aus
                        if pos in occupied and occupied[pos] == current_turn:
                            selected_stone = pos
                    else:   
                        # Nur reagieren, wenn pos eine gültige Position ist
                        player_stones = [p for p in occupied if occupied[p] == current_turn]
                        can_fly = len(player_stones) == 3
                        if pos not in occupied and (can_fly or pos in get_neighbors(selected_stone)):
                        # Stein bewegen
                            occupied[pos] = current_turn
                            del occupied[selected_stone]
                            selected_stone = None
                            for mill in Mills:
                                if pos in mill and all(p in occupied and occupied[p] == current_turn for p in mill):
                                    removal_mode = True
                                    print("Mühle gebildet! Entferne einen Stein des Gegners.")
                                    move_count_without_mill = 0  # Zähler zurücksetzen, wenn eine Mühle gebildet wird
                                    break
                            if not removal_mode:
                                move_count_without_mill += 1  # Zähler erhöhen, wenn keine Mühle gebildet wird
                                current_turn = 'red' if current_turn == 'white' else 'white'
                            check_game_status()
                        elif pos == selected_stone:
                            selected_stone = None
                        else:
                            continue

        screen.fill(black)
        board()
        for pos, color in occupied.items():
            if color == 'white':
                white_stone(pos)
            else:
                red_stone(pos)

        if selected_stone:
            # Hervorheben des ausgewählten Steins
            pygame.draw.circle(screen, (0,255,0), selected_stone, 10, 2)
        if game_over:
            draw_top_text([
                (game_over_text[0], True),
                (game_over_text[1], False),
                ("Drücke R für Neustart", False),
            ])
        else:
            draw_top_text([
                (f"Am Zug: {'Weiss' if current_turn=='white' else 'Rot'}", False),
                (f"Platzierphase: {'Ja' if placing_phase else 'Nein'}", False),
                ("Drücke R für Neustart", False),
            ])
        pygame.display.flip()
        pygame.time.delay(100)  # Kurze Verzögerung, um die CPU-Auslastung zu reduzieren
        await asyncio.sleep(0)
asyncio.run(main())