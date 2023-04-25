# Документация
# Шрифты https://fonts.google.com/


import pygame

# Добавляем часы, чтобы обновлять экран не так часто
clock = pygame.time.Clock()
# Инициализируем игру
pygame.init()
# Размеры для экрана игры (передается кортеж). Параметр flags=pygame.NOFRAME уберет рамку вокруг игры
screen = pygame.display.set_mode((900, 360), )
# Добавялем название для приложения
pygame.display.set_caption("Beetle")
# Подгружаем изображение и устанавливаем его как иконку для проекта https://www.iconfinder.com/
icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)

# Создаем текстовую запись https://fonts.google.com/
# myfont = pygame.font.Font('fonts/PTSans-Regular.ttf', 40)
# text_surface = myfont.render('Beetle game', True, 'Red')

bg = pygame.image.load('images/bg.jpg')

# Создание движения игрока влево
walk_left = [
    pygame.image.load('images/player_left/player_left_1.png'),
    pygame.image.load('images/player_left/player_left_2.png'),
    pygame.image.load('images/player_left/player_left_3.png')
]

player_anim_count = 0
bg_x = 0

bg_sound = pygame.mixer.Sound('sounds/bg.mp3')
bg_sound.play()

running = True
# Добавляем цикл, чтобы программа сразу же не закрывалась
while running:

    # screen.fill((114, 157, 224))
    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x - 900, 0))

    # Чтобы добавить новый объект используем blit
    # screen.blit(square, (0, 0))
    # screen.blit(text_surface, (300, 100))
    screen.blit(walk_left[player_anim_count], (250, 187))

    if player_anim_count == 2:
        player_anim_count = 0
    else:
        player_anim_count += 1

    # Движение фона
    bg_x += 2
    if bg_x == +900:
        bg_x = 0

    # Добавим объект в одну строчку
    # pygame.draw.circle(screen, 'Red', (10, 7), 5)

    pygame.display.update()  #Постоянно обновляем экран нашего приложения

    for event in pygame.event.get():  #pygame.event.get() - список со всеми возможными событиями
        # Добавляем условие корректного закрытия игры
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        # Проверяем событие на нажатие клавиши
        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_a:
        #         screen.fill((70, 44, 133))

    clock.tick(10)

