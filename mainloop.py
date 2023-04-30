import pygame
pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((1200, 480), )

walk_left = [
    pygame.image.load('images/player_left/player_left_1.png').convert_alpha(),
    pygame.image.load('images/player_left/player_left_2.png').convert_alpha(),
    pygame.image.load('images/player_left/player_left_3.png').convert_alpha(),
    pygame.image.load('images/player_left/player_left_4.png').convert_alpha()
]

walk_right = [
    pygame.image.load('images/player_right/player_right_1.png').convert_alpha(),
    pygame.image.load('images/player_right/player_right_2.png').convert_alpha(),
    pygame.image.load('images/player_right/player_right_3.png').convert_alpha(),
    pygame.image.load('images/player_right/player_right_4.png').convert_alpha()
]

text = pygame.font.Font('fonts/PTSans-Regular.ttf', 40)

black_surface = pygame.Surface((200, 50))

start_label = text.render("Играть!", False, (115, 132, 148))
start_label_rect = start_label.get_rect(topleft=(537, 167))

bg = pygame.image.load('images/background/bg_1.png')

running = True
gameplay = True
while running:
    if gameplay:
        screen.blit(bg, (0,0))
        screen.blit(black_surface, (500, 170))
        screen.blit(start_label, start_label_rect)

        mouse = pygame.mouse.get_pos()
        if start_label_rect.collidepoint(mouse):
            gameplay = True

        # Движение фона
        bg_x -= 2
        if bg_x == -1200:
            bg_x = 0

        pygame.display.update()  # Постоянно обновляем экран нашего приложения

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

    clock.tick(15)