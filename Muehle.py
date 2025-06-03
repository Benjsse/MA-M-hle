import sys, pygame
pygame.init()

size = width, height = 800, 800
black = 0, 0, 0
white = 255, 255, 255
grey = 128, 128, 128

outerrec = [(200,200),(200,400),(200,600),(400,600),(600,600),(600,400),(600,200),(400,200)]
middlerec = [(250,250),(250,400),(250,550),(400,550),(550,550),(550,400),(550,250),(400,250)]
innerrec = [(300,300),(300,400),(300,500),(400,500),(500,500),(500,400),(500,300),(400,300)]

screen = pygame.display.set_mode(size)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    pygame.draw.lines(screen, grey, True, outerrec, width=5)
    pygame.draw.lines(screen, grey, True, middlerec, width=5)
    pygame.draw.lines(screen, grey, True, innerrec, width=5)
    pygame.draw.lines(screen, grey, False, [(200,400),(300,400)], width=5)
    pygame.draw.lines(screen, grey, False, [(600,400),(500,400)], width=5)
    pygame.draw.lines(screen, grey, False, [(400,500),(400,600)], width=5)
    pygame.draw.lines(screen, grey, False, [(400,200),(400,300)], width=5)

    pygame.display.flip()
