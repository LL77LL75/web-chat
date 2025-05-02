import pygame
# pygame.init()
pygame.display.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Pong Game")
white = ((255,255,255))
red = ((255,0,0))
moon_glow = ((235,245,255))
paddle_width = 20
paddle_height = 100
paddle1_x = 10
paddle1_y = screen_height//2 - paddle_height // 2
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.draw.rect(screen,moon_glow, (0, 0, screen_width, screen_height))
    pygame.display.flip()
pygame.quit()