import pygame
# pygame.init()
pygame.display.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Pong Game")
white = ((255,255,255))
red = ((255,0,0))
gray = ((50,50,50))
paddle_width = 20
paddle_height = 100
paddle1_x = 10
paddle1_y = screen_height//2 - paddle_height // 2

paddle2_x = screen_width - paddle_width - 10
paddle2_y = screen_height//2 - paddle_height // 2
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1_y >0:
            paddle1_y-=1
        if keys[pygame.K_s] and paddle1_y < screen_height - paddle_height:
            paddle1_y+=1
    screen.fill(gray)
    pygame.draw.rect(screen,white,(paddle1_x,paddle1_y,paddle_width,paddle_height))
    pygame.draw.rect(screen,white,(paddle2_x,paddle2_y,paddle_width,paddle_height))
    pygame.display.flip()
pygame.quit()