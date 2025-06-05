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
                # überprüfen des nächsten Nachbarn
            if idx < len(lst) - 1:
                neighbors.append(lst[idx+1])
    return neighbors #liste wird zurückgegeben, die alle Nachbarn der Position enthält
# Wessen Zug ist es?
current_turn = 'white'
stones_placed = 0
placing_phase = True
selected_stone = None #für die Zugphase des Spiels

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            pos = get_nearest_position(mouse_pos)
            if pos is None:
                continue
            if placing_phase:
                if pos not in occupied:
                    occupied[pos] = current_turn
                    stones_placed += 1
                    current_turn = 'red' if current_turn == 'white' else 'white'
                    if stones_placed >=18:
                        placing_phase = False
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
                        current_turn = 'red' if current_turn == 'white' else 'white'
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
