import pygame
import random
import pygame_menu
from database import get_best, add_record

pygame.init()

# Ширина и высота экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

USERNAME = None

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('Slowking')
clock = pygame.time.Clock()  # подключаем часы
FPS = 60  # счетчик кадров в секунду


# шрифты
font_large = pygame.font.Font('fonts/Ubuntu-Light.ttf', 48)
font_small = pygame.font.Font('fonts/Ubuntu-Light.ttf', 24)

lose_label = font_large.render("Вы проиграли!", True, ('black'))
restart = font_small.render("Играть заново :)", True, ('black'))
restart_rect = restart.get_rect(topleft=(320, 300))
records = font_small.render("Таблица рекордов", True, ('black'))
records_rect = records.get_rect(topleft=(305, 350))
# top_five = font_large.render("Топ-5 игроков:", True, ('black'))
save = font_small.render("Сохранить результат", True, ('black'))
save_rect = records.get_rect(topleft=(290, 250))

# загружаем картинки
bg_image = pygame.image.load('images/background/bg_mini.png')

ground_image = pygame.image.load('images/background/ground_mini.png')
ground_image = pygame.transform.scale(ground_image, (804, 60))
GROUND_H = ground_image.get_height()

enemy_image = pygame.image.load('images/monst.png')
enemy_image = pygame.transform.scale(enemy_image, (80, 80))

enemy_dead_image = pygame.image.load('images/monst.png')
enemy_dead_image = pygame.transform.scale(enemy_dead_image, (80, 80))

player_image = pygame.image.load('images/player_mini_2.png')
player_image = pygame.transform.scale(player_image, (100, 80))


# Основная функция игры
def start_the_game():
    SCORE = 0
    INIT_DELAY = 2000  # начальная задержка создания монстров
    spawn_delay = INIT_DELAY  # частота создания монстров
    DECREASE_BASE = 1.01  # коэффициент увеличения сложности
    last_spawn_time = pygame.time.get_ticks()  # хранение последнего времени создания монстра

    # класс существ
    class Entity:
        def __init__(self, image):
            self.image = image  # изображение существа
            self.rect = self.image.get_rect()  # прямоугольник вокруг существа
            self.change_y = 0  # скорость по х
            self.change_x = 0  # скорость по х
            self.speed = 5  # скорость для перемещения
            self.is_out = False  # в пределах карты игрок или нет
            self.is_dead = False  # жив игрок или нет
            self.jump_speed = -12  # скорость прыжка
            self.gravity = 0.5  # гравитация
            self.is_grounded = False  # находимся ли на земле

        # отслеживание управления
        def control(self):
            pass

        # уничтожение сущности
        def kill(self, dead_image):
            # картинка сущности
            self.image = dead_image
            # мертва ли сущность
            self.is_dead = True
            # инвертируем скорость при смерти
            self.change_x = -self.change_x
            # после смерти подкидывается сущность
            self.change_y = self.jump_speed

        # для обновления отрисовки движения
        def update(self):
            # перемещение за счет изменения скорости
            self.rect.x += self.change_x
            # изменяем скорость прибавляя гравитацию
            self.rect.y += self.change_y
            # передвижение за счет изменения скорости вместе с гравитацией
            self.change_y += self.gravity

            # если игрок уже мертв
            if self.is_dead:
                if self.rect.top > SCREEN_HEIGHT - GROUND_H:
                    self.is_out = True
            # если живы, то ходим по земле
            else:
                self.control()
                # проверяем не выпали ли за пределы игры
                if self.rect.bottom > SCREEN_HEIGHT - GROUND_H:
                    self.is_grounded = True
                    self.change_y = 0
                    self.rect.bottom = SCREEN_HEIGHT - GROUND_H

        # для отрисовки сущности
        def draw(self, surface):
            surface.blit(self.image, self.rect)

    # наследуемый класс для инициализации Хонтеров
    class Haunter(Entity):
        # конструктор класса
        def __init__(self):
            super().__init__(enemy_image)
            self.create_haunter()

        # создание хонтеров
        def create_haunter(self):
            # выбор направления, откуда появляются монстры
            direction = random.randint(0, 3)

            if direction == 0:
                self.change_x = self.speed
                self.rect.bottomright = (0, 0)
            elif direction == 1:
                self.change_x = -self.speed
                self.rect.bottomleft = (SCREEN_WIDTH, 0)
            elif direction == 2:
                self.change_x = self.speed
                self.rect.bottomright = (0, 400)
            elif direction == 3:
                self.change_x = -self.speed
                self.rect.bottomleft = (SCREEN_WIDTH, 400)

        def update(self):
            super().update()
            # если Хонтер покидает пределы влево или вправо
            if self.change_x > 0 and self.rect.left > SCREEN_WIDTH or self.change_x < 0 and self.rect.right < 0:
                self.is_out = True

    # класс для инициализации слоупока
    class Player(Entity):
        def __init__(self):
            super().__init__(player_image)
            self.respawn()

        # переопределим управление для игрока
        def control(self):
            # обнуляем скорость по х
            self.change_x = 0

            # проверка нажатия на клавиши
            keys = pygame.key.get_pressed()
            # двигаем игрока влево
            if keys[pygame.K_a]:
                self.change_x = -self.speed
            # двигаем игрока вправо
            elif keys[pygame.K_d]:
                self.change_x = self.speed

            # проверка нахождения на земле для прыжка
            if self.is_grounded and keys[pygame.K_SPACE]:
                self.is_grounded = False
                self.jump()

        # начальное положение в центральной точке
        def respawn(self):
            self.is_out = False
            self.is_dead = False
            self.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT)

        def jump(self):
            self.change_y = self.jump_speed

    player = Player()  # создаем игрока

    haunters = []  # список Хонтеров, находящихся на экране

    # основной цикл
    running = True
    while running:
        paused = False
        # фон
        screen.blit(bg_image, (0, 0))
        screen.blit(ground_image, (0, SCREEN_HEIGHT - GROUND_H))

        # все события которые происходят
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

            # # проверка на нажатие других клавиш
            # elif event.type == pygame.KEYDOWN:
            #     if player.is_out:
            #         SCORE = 0
            #         last_spawn_time = pygame.time.get_ticks()
            #         player.respawn()
            #         haunters.clear()

        score_surface = font_large.render(str(SCORE), True, 'blue')  # поверхность счетчика
        score_rect = score_surface.get_rect()

        # при проигрыше
        if player.is_out:
            screen.blit(bg_image, (0, 0))
            screen.blit(lose_label, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 - 210))

            # расположение очков после смерти
            score_rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70)
            # поверхность с перезапуском
            screen.blit(restart, restart_rect)
            screen.blit(records, records_rect)
            screen.blit(save, save_rect)

            mouse = pygame.mouse.get_pos()
            # перезапуск основной функции
            if restart_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
                start_the_game()

            # if save_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            #     gamer()

            # топ рекордов
            if records_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
                screen.blit(bg_image, (0, 0))
                # screen.blit(top_five, (50, 50))
                show_records()

        # если еще живы
        else:
            now = pygame.time.get_ticks()  # текущее игровое время
            elapsed = now - last_spawn_time  # время с момента последнего создания монстра
            if elapsed > spawn_delay:  # проверяем вышла ли задержка и можно ли создавать монстра
                last_spawn_time = pygame.time.get_ticks()  # зафиксировали последнее время создания монстра
                haunters.append(Haunter())  # добавляем нового монстра в список монстров на экране

            player.update()  # обновляем игрока для отображения
            player.draw(screen)

            for h in list(haunters):  # перебираем всех монстров из копии списка монстров
                if h.is_out:
                    haunters.remove(h)  # удаляем монстра если он за пределами экрана
                else:
                    h.update()  # обновляем если он живой
                    h.draw(screen)

                if not player.is_dead and not h.is_dead and player.rect.colliderect(h.rect):  # живы и соприкасаются
                    if player.rect.bottom - player.change_y < h.rect.top:  # если игрок упал сверху
                        h.kill(enemy_dead_image)
                        player.jump()
                        SCORE += 1
                        spawn_delay = INIT_DELAY / (DECREASE_BASE ** SCORE)
                    else:
                        player.kill(player_image)

            score_rect.midtop = (SCREEN_WIDTH // 2, 5)  # расположение очков во время игры

        screen.blit(score_surface, score_rect)
        pygame.display.update()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            paused_menu()

        clock.tick(FPS)  # ограничение по кадрам в секунду


def start_menu():
    menu = pygame_menu.Menu('Slowking', 400, 300,
                            theme=pygame_menu.themes.THEME_BLUE)

    menu.add.button('Новая игра', start_the_game)
    menu.add.button('Выход', pygame_menu.events.EXIT)

    while True:
        screen.blit(bg_image, (0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        if menu.is_enabled():
            menu.update(events)
            menu.draw(screen)

        pygame.display.update()


def paused_menu():
    menu = pygame_menu.Menu('Slowking', 400, 300,
                            theme=pygame_menu.themes.THEME_BLUE)

    menu.add.button('Начать с начала', start_the_game)
    menu.add.button('В меню', start_menu)

    while True:
        screen.blit(bg_image, (0, 0))

        events = pygame.event.get()

        if menu.is_enabled():
            menu.update(events)
            menu.draw(screen)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            break

        pygame.display.update()


def show_records():
    font_gamer = pygame.font.Font('fonts/Ubuntu-Light.ttf', 24)
    screen.blit(bg_image, (0, 0))
    result = get_best()
    for index, gamer in enumerate(result):
        name, score = gamer
        s = f"{index + 1}. {name} - {score}"
        text_gamer = font_gamer.render(s, True, 'black')
        screen.blit(text_gamer, (320, 250 + 35 * index))


# def gamer():
#     font_gamer = pygame.font.Font('fonts/Ubuntu-Light.ttf', 24)
#     name = 'Введите имя'
#     is_find_name = False
#     while not is_find_name:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 quit()
#
#             elif event.type == pygame.KEYDOWN:
#                 if event.unicode.isalpha():
#                     if name == 'Введите имя':
#                         name = event.unicode
#                     else:
#                         name += event.unicode
#                 elif event.key == pygame.K_BACKSPACE:
#                     name = name[:-1]
#                 elif event.key == pygame.K_RETURN:
#                     if len(name) > 2:
#                         global USERNAME
#                         USERNAME = name
#                         is_find_name = True
#                         break
#
#         screen.fill('black')
#         text_name = font_gamer(name, True, 'black')
#         rect_name = text_name.get_rect()
#         rect_name.center = screen.get_rect().center
#         screen.blit(text_name, rect_name)

# def save_results():
#     font_gamer = pygame.font.Font('fonts/Ubuntu-Light.ttf', 24)
#     name = 'Введите имя'
#     is_find_name = False
#     while not is_find_name:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 quit()
#
#             elif event.type == pygame.KEYDOWN:
#                 if event.unicode.isalpha():
#                     if name == 'Введите имя':
#                         name = event.unicode
#                     else:
#                         name += event.unicode
#                 elif event.key == pygame.K_BACKSPACE:
#                     name = name[:-1]
#                 elif event.key == pygame.K_RETURN:
#                     if len(name) > 2:
#                         global USERNAME
#                         USERNAME = name
#                         is_find_name = True
#                         break
#
#         screen.fill('black')
#         text_name = font_gamer(name, True, 'black')
#         rect_name = text_name.get_rect()
#         rect_name.center = screen.get_rect().center
#         screen.blit(text_name, rect_name)

start_menu()
