import sys, pygame
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

def get_neighbors(pos): # Funktion, um die Nachbarn einer Position zu finden
    neighbors = []
    lists = [outerrec, middlerec, innerrec, firstline, secondline, thirdline, fourthline]
    for lst in lists:
        if pos in lst:
            idx = lst.index(pos)
            #überprüfen des vorherigen Nachbarn 
            if idx > 0:
                neighbors.append(lst[idx-1])
            else:
                neighbors.append(lst[-1])
                # überprüfen des nächsten Nachbarn
            if idx < len(lst) - 1:
                neighbors.append(lst[idx+1])
            else:
                neighbors.append(lst[0])
    return neighbors #liste wird zurückgegeben, die alle Nachbarn der Position enthält
# Wessen Zug ist es?
move_count_without_mill = 0
positions_history = []
white_placed = 0
red_placed = 0

def check_game_status():
    global move_count_without_mill, positions_history, white_placed, red_placed

    # Status Ausgabe für Fehlersuche
    print("Aktueller Status:")
    print("White Placed:", white_placed)
    print("Red Placed:", red_placed)
    print("Occupied:", occupied)
    print("Move Count Without Mill:", move_count_without_mill)

    # Zähle die Steine der Spieler
    white_stones = [pos for pos in occupied if occupied[pos] == 'white']
    red_stones = [pos for pos in occupied if occupied[pos] == 'red']

    # Überprüfen, ob ein Spieler weniger als 3 Steine hat (nur wenn beide Spieler mindestens 9 Steine platziert haben)
    if white_placed >= 9 and red_placed >= 9:
        if len(white_stones) < 3:
            print("Red gewinnt! White hat weniger als 3 Steine.")
            sys.exit()
        if len(red_stones) < 3:
            print("White gewinnt! Red hat weniger als 3 Steine.")
            sys.exit()
        # Überprüfen, ob ein Spieler keine gültigen Züge mehr machen kann
        white_moves = any(
            pos for pos in white_stones if any(neighbor not in occupied for neighbor in get_neighbors(pos))
        )
        red_moves = any(
            pos for pos in red_stones if any(neighbor not in occupied for neighbor in get_neighbors(pos))
        )
        if not white_moves and not red_moves:
            print("Unentschieden! Beide Spieler können keine Züge mehr machen.")
            sys.exit()
        if not white_moves:
            print("Red gewinnt! White kann keine Züge mehr machen.")
            sys.exit()
        if not red_moves:
            print("White gewinnt! Red kann keine Züge mehr machen.")
            sys.exit()

    # Prüfen, ob nach 20 Zügen keine Mühle gebildet wurde
    if move_count_without_mill >= 20:
        print("Unentschieden! Nach 20 Zügen wurde keine Mühle gebildet.")
        sys.exit()

    # Prüfen, ob die gleiche Stellung dreimal erreicht wurde
    positions_snapshot = tuple(sorted(occupied.items()))  # Aktuelle Stellung der Steine
    positions_history.append(positions_snapshot)
    if positions_history.count(positions_snapshot) >= 3:
        print("Unentschieden! Die gleiche Stellung wurde dreimal erreicht.")
        sys.exit()


current_turn = 'white'
stones_placed = 0
placing_phase = True
selected_stone = None # für die Zugphase des Spiels

removal_mode = False
removal_selection = None

# Entfernen von Steinen
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
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
                        white_placed += 1  # Zähler für weiße Steine erhöhen
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
                    if pos not in occupied and pos in get_neighbors(selected_stone):
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
    pygame.display.flip()