import pygame
player1_score = 0
player2_score = 0
surface = pygame.Surface(20,10)
player2_win_text ="Player 2 wins!"
player1_win_text ="Player 1 wins!"
# pygame.init()
pygame.display.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Pong Game")
white = ((255,255,255))
red = ((255,0,0))
black = ((0,0,0))
paddle_width = 20
paddle_height = 100
paddle1_x = 10
paddle1_y = screen_height//2 - paddle_height // 2
pygame.font.init()
score_font = pygame.font.Font(None,32)
paddle2_x = screen_width - paddle_width - 10
paddle2_y = screen_height//2 - paddle_height // 2
running = True
background = pygame.image.load("CT07_14_15_16/Grass Court.jpg")
ball = pygame.image.load("/workspaces/Lance-pythonthinker2/CT07_14_15_16/Tennis Ball.png")
paddle = pygame.image.load("CT07_14_15_16/Tennis Racket.png")
ball_radius = 10
ball_x = screen_width//2
ball_y = screen_height//2

ball_dx = 1
ball_dy = 1
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle1_y >0:
        paddle1_y-=1
    if keys[pygame.K_s] and paddle1_y < screen_height - paddle_height:
        paddle1_y+=1
    if keys[pygame.K_UP] and paddle2_y >0:
        paddle2_y-=1
    if keys[pygame.K_DOWN] and paddle2_y < screen_height - paddle_height:
        paddle2_y+=1
    ball_x += ball_dx
    ball_y += ball_dy
    if ball_y <= 0 or ball_y > screen_height:
        ball_dy *= -1
    if ball_x <= 0 :
        player2_score +=1
        ball_x = screen_width//2
        ball_y = screen_height//2
    if ball_x > screen_width:
        player1_score +=1
        ball_x = screen_width//2
        ball_y = screen_height//2
    paddle1_box = pygame.Rect(paddle1_x,paddle1_y,paddle_width,paddle_height)
    paddle2_box = pygame.Rect(paddle2_x,paddle2_y,paddle_width,paddle_height)
    if ball_x <= (paddle1_box.right + ball_radius) and (paddle1_box.top <= ball_y <= paddle1_box.bottom):
        ball_dx *= -1
    if ball_x >=(paddle2_box.left - ball_radius) and (paddle2_box.top <= ball_y <= paddle2_box.bottom):
        ball_dx *= -1
    screen.blit(background,(0,0))
    # pygame.draw.rect(screen,white,(paddle1_x,paddle1_y,paddle_width,paddle_height))
    # pygame.draw.rect(screen,white,(paddle2_x,paddle2_y,paddle_width,paddle_height))
    pygame.draw.circle(screen,white,(ball_x,ball_y),ball_radius)
    screen.blit(ball,(ball_x-ball_radius,ball_y-ball_radius))
    screen.blit(paddle,(paddle1_x,paddle1_y))
    screen.blit(pygame.transform.rotate(paddle,180),(paddle2_x,paddle2_y))
    player1_score_text = score_font.render("player 1: " + str(player1_score), True,black)
    screen.blit(player1_score_text,(10,10))
    player2_score_text = score_font.render("player 2: " + str(player2_score), True,black)
    screen.blit(player2_score_text,(screen_width-10-player2_score_text.get_width(),10))
    if player1_score==3:
        screen.blit(score_font.render(screen_width/2),(screen_width//2,screen_height//2))
    if player2_score==3:
        screen.blit(player2_win_text,(screen_width//2,screen_height//2))
    pygame.display.flip()
pygame.quit()