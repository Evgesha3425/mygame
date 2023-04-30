# Документация https://www.pygame.org/docs/
# Шрифты https://fonts.google.com/
# Иконки https://www.iconfinder.com/

import pygame

# Добавляем часы, чтобы обновлять экран не так часто
clock = pygame.time.Clock()
# Инициализируем игру
pygame.init()
# Размеры для экрана игры (передается кортеж)
screen = pygame.display.set_mode((1200, 480), )
# Добавялем название для приложения
pygame.display.set_caption("Slowking")
# Подгружаем изображение и устанавливаем его как иконку для проекта https://www.iconfinder.com/
icon = pygame.image.load('images/icon.png').convert_alpha()
pygame.display.set_icon(icon)

bg = pygame.image.load('images/background/bg_1.png').convert_alpha()

# Создание движения игрока влево
walk_left = [
    pygame.image.load('images/player_left/player_left_1.png').convert_alpha(),
    pygame.image.load('images/player_left/player_left_2.png').convert_alpha(),
    pygame.image.load('images/player_left/player_left_3.png').convert_alpha(),
    pygame.image.load('images/player_left/player_left_4.png').convert_alpha()
]

# Создание движения игрока вправо
walk_right = [
    pygame.image.load('images/player_right/player_right_1.png').convert_alpha(),
    pygame.image.load('images/player_right/player_right_2.png').convert_alpha(),
    pygame.image.load('images/player_right/player_right_3.png').convert_alpha(),
    pygame.image.load('images/player_right/player_right_4.png').convert_alpha()
]

monster = pygame.image.load('images/monster.png').convert_alpha()
monster_list_in_game = []

player_anim_count = 0
bg_x = 0

# Скорость для передвижения игрока
player_speed = 35
# Координата размещения игрока
player_x = 150
player_y = 250

is_jump = False
jump_count = 7

# bg_sound = pygame.mixer.Sound('sounds/bg.mp3')
# bg_sound.play()

# Подключаем таймер для появления монстров с задержкой
monster_timer = pygame.USEREVENT + 1
pygame.time.set_timer(monster_timer, 5000)

label = pygame.font.Font('fonts/PTSans-Regular.ttf', 40)
# текст, не скруглять, цвет
lose_label = label.render("Вы проиграли!", False, (193, 196, 199))
restart_label = label.render("Играть заново", False, (115, 132, 148))
# невидимая рамка
restart_label_rect = restart_label.get_rect(topleft=(180, 200))
start_label = label.render("Играть!", False, (115, 132, 148))
start_label_rect = start_label.get_rect(topleft=(180, 200))


# Выстрелы
shots_left = 5 # осталось выстрелов
shot = pygame.image.load('images/bullet.png').convert_alpha()
shots = []

# gameplay для того чтобы проверять, запущена ли игра. Если нет - проигрыш
gameplay = True

# Добавляем цикл, чтобы программа сразу же не закрывалась
running = True
while running:
    if gameplay:
        # Вставка фона
        screen.blit(bg, (bg_x, 0))
        screen.blit(bg, (bg_x + 1200, 0))

        # Квадрат вокруг нашего игрока для соприкосновения
        player_rect = walk_left[0].get_rect(topleft=(player_x, player_y))
        # monster_rect = monster.get_rect(topleft=(monster_x, 250))

        # Автоматическая вставка монстров за счет выведения их из списка
        if monster_list_in_game:
            # Перебирая список через enumerate мы не только перебираем список, но и получаем его индекс
            for (i, el) in enumerate(monster_list_in_game):
                screen.blit(monster, el)
                el.x -= 10

                # Удаление монстра вне поле игры
                if el.x < -10:
                    monster_list_in_game.pop(i)

                # Условие соприкосновения
                if player_rect.colliderect(el):
                    print("You lose")
                    gameplay = False

        # Движение персонажа
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            screen.blit(walk_left[player_anim_count], (player_x, player_y))
        else:
            screen.blit(walk_right[player_anim_count], (player_x, player_y))

        if player_anim_count == 2:
            player_anim_count = 0
        else:
            player_anim_count += 1

        # Отслеживание нажатия клавиш
        if keys[pygame.K_LEFT] and player_x > 100:
            player_x -= player_speed
        elif keys[pygame.K_RIGHT] and player_x < 750:
            player_x += player_speed

        # Отслеживание прыжка
        if not is_jump:
            if keys[pygame.K_UP]:
                is_jump = True
        else:
            if jump_count >= -7:
                if jump_count > 0:
                    player_y -= (jump_count ** 2)
                else:
                    player_y += (jump_count ** 2)
                jump_count -= 1
            else:
                is_jump = False
                jump_count = 7

        # Движение фона
        bg_x -= 2
        if bg_x == -1200:
            bg_x = 0

        # Движение после выстрела
        if shots:
            for (i, el) in enumerate(shots):
                screen.blit(shot, (el.x, el.y))
                el.x += 4

                # Удаление после выхода за пределы игрового экрана
                if el.x > 950:
                    shots.pop()

                if monster_list_in_game:
                    for (index, monst) in enumerate(monster_list_in_game):
                        # При взаимодействии патрона и монстра они удалятся
                        if el.colliderect(monst):
                            monster_list_in_game.pop(index)
                            shots.pop(i)

    else:
        screen.fill((87, 88, 89))
        screen.blit(lose_label, (180, 100))
        screen.blit(restart_label, restart_label_rect)

        mouse = pygame.mouse.get_pos()
        # Проверка соприкосновения квадрата restart с мышкой
        if restart_label_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            gameplay = True
            player_x = 150
            monster_list_in_game.clear()
            shots.clear()
            shots_left = 5

    pygame.display.update()  #Постоянно обновляем экран нашего приложения

    for event in pygame.event.get():  #pygame.event.get() - список со всеми возможными событиями
        # Добавляем условие корректного закрытия игры
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        # При срабатывании таймера добавляется новый монстр в список
        if event.type == monster_timer:
            monster_list_in_game.append(monster.get_rect(topleft=(950, 100)))
        # Выстрел по нажатию. Благодаря KEYUP срабатывание будет происходить после поднятия с клавиши
        if gameplay and event.type == pygame.KEYUP and event.key == pygame.K_SPACE and shots_left > 0:
            shots.append(shot.get_rect(topleft=(player_x + 30, player_y + 10)))
            shots_left -= 1

    clock.tick(15)
#
