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

# Wessen Zug ist es?
current_turn = 'white'

# Counter wieviele Steine platziert wurden
stones_placed = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            pos = get_nearest_position(mouse_pos)
            if pos and pos not in occupied:
                occupied[pos] = current_turn  # platzieren des Steins
                stones_placed += 1            # stein wurde platziert
                # anderer spieler ist nun am Zug
                current_turn = 'red' if current_turn == 'white' else 'white'

    screen.fill(black)
    board()
    for pos, color in occupied.items():
        if color == 'white':
            white_stone(pos)
        else:
            red_stone(pos)
    pygame.display.flip()
