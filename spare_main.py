import pygame
import random
import pygame_menu
import pygame_textinput
from database import get_best

pygame.init()

# Ширина и высота экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
name_game = pygame.display.set_caption('Slowking')

# счетчик кадров в секунду
FPS = 60
# Создаем сам экран
clock = pygame.time.Clock()

# шрифты
font_path = 'fonts/Ubuntu-Light.ttf'
font_large = pygame.font.Font(font_path, 48)
font_small = pygame.font.Font(font_path, 24)

# рестарт игры
retry_text = font_small.render('PRESS ANY KEY', True, (255, 255, 255))
retry_rect = retry_text.get_rect()
retry_rect.midtop = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

lose_label = font_large.render("Вы проиграли!", True, ('black'))
restart = font_small.render("Играть заново", True, ('black'))
restart_rect = restart.get_rect()
textinput = pygame_textinput.TextInputVisualizer()

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
    # счетчик
    score = 0

    # начальная задержка создания монстров
    INIT_DELAY = 2000
    # частота создания монстров
    spawn_delay = INIT_DELAY
    # коэффициент увеличения сложности
    DECREASE_BASE = 1.01
    # хранение последнего времени создания монстра
    last_spawn_time = pygame.time.get_ticks()

    # класс существ
    class Entity:
        # конструктор класса
        def __init__(self, image):
            # изображение существа
            self.image = image
            # прямоугольник вокруг существа
            self.rect = self.image.get_rect()
            # скорость по х и у
            self.change_y = 0
            self.change_x = 0
            # скорость для перемещения
            self.speed = 5
            # в пределах карты мы или нет
            self.is_out = False
            # живы или нет
            self.is_dead = False
            # скорость прыжка
            self.jump_speed = -12
            # гравитация
            self.gravity = 0.5
            # находимся ли на земле
            self.is_grounded = False

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

        # def flip(self):
        #     # переворачиваем изображение / по оси Х True / по оси Y False
        #     self.image = pygame.transform.flip(self.image, True, False)

    # class Platform(pygame.sprite.Sprite):
    #     def __init__(self, width, height):
    #         # Конструктор платформ
    #         super().__init__()
    #         # Также указываем фото платформы
    #         self.image = pygame.image.load('images/background/platform_mini.png').convert_alpha()
    #
    #         # Установите ссылку на изображение прямоугольника
    #         self.rect = self.image.get_rect()
    #
    #
    # # Класс для расстановки платформ на сцене
    # class Level(object):
    #     def __init__(self, player):
    #         # Создаем группу спрайтов (поместим платформы различные сюда)
    #         self.platform_list = pygame.sprite.Group()
    #         # Ссылка на основного игрока
    #         self.player = player
    #
    #     # Чтобы все рисовалось, то нужно обновлять экран
    #     # При вызове этого метода обновление будет происходить
    #     def update(self):
    #         self.platform_list.update()
    #
    #     # Метод для рисования объектов на сцене
    #     def draw(self, screen):
    #         # Рисуем задний фон
    #         screen.blit(bg, (0, 0))
    #
    #         # Рисуем все платформы из группы спрайтов
    #         self.platform_list.draw(screen)
    #
    # class Level_01(Level):
    #     def __init__(self, player):
    #         # Вызываем родительский конструктор
    #         Level.__init__(self, player)
    #
    #         # Массив с данными про платформы. Данные в таком формате:
    #         # ширина, высота, x и y позиция
    #         level = [
    #             [600, 93, -20, 570],
    #             [600, 93, 190, 570],
    #             [600, 93, 400, 570],
    #             [600, 93, 610, 570],
    #             [210, 32, 500, 500],
    #             [210, 32, 200, 400],
    #             [210, 32, 600, 300],
    #         ]
    #
    #         # Перебираем массив и добавляем каждую платформу в группу спрайтов - platform_list
    #         for platform in level:
    #             block = Platform(platform[0], platform[1])
    #             block.rect.x = platform[2]
    #             block.rect.y = platform[3]
    #             block.player = self.player
    #             self.platform_list.add(block)

    # создаем игрока
    player = Player()

    # список Хонтеров, находящихся на экране
    haunters = []

    # основной цикл
    running = True
    while running:
        # фон
        screen.blit(bg_image, (0, 0))
        screen.blit(ground_image, (0, SCREEN_HEIGHT - GROUND_H))

        # все события которые происходят
        for e in pygame.event.get():
            # проверка на событие выхода из игры
            if e.type == pygame.QUIT:
                running = False
                pygame.quit()

            # проверка на нажатие других клавиш
            elif e.type == pygame.KEYDOWN:
                if player.is_out:
                    score = 0
                    finish_delay = INIT_DELAY
                    last_spawn_time = pygame.time.get_ticks()
                    player.respawn()
                    haunters.clear()


        # поверхность счетчика
        score_surface = font_large.render(str(score), True, ('blue'))
        score_rect = score_surface.get_rect()

        # при проигрыше
        if player.is_out:
            # # расположение очков после смерти
            # score_rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            # # поверхность с перезапуском
            # screen.blit(retry_text, retry_rect)

            screen.blit(bg_image, (0, 0))
            screen.blit(lose_label, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 - 250))

            screen.blit(restart, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))

            mouse = pygame.mouse.get_pos()
            if restart_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
                start_the_game()



            events = pygame.event.get()
            # Feed it with events every frame
            textinput.update(events)
            # Blit its surface onto the screen
            screen.blit(textinput.surface, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))

        # если еще живы
        else:
            # текущее игровое время
            now = pygame.time.get_ticks()
            # время с момента последнего создания монстра
            elapsed = now - last_spawn_time

            # проверяем вышла ли задержка и можно ли создавать монстра
            if elapsed > spawn_delay:
                # зафиксировали последнее время создания монстра
                last_spawn_time = pygame.time.get_ticks()
                # добавляем нового монстра в список монстров на экране
                haunters.append(Haunter())

            # обновляем игрока для отображения
            player.update()
            player.draw(screen)

            # перебираем всех монстров из копии списка монстров
            for h in list(haunters):
                # удаляем монстра если он за пределами экрана
                if h.is_out:
                    haunters.remove(h)
                # обновляем если он живой
                else:
                    h.update()
                    h.draw(screen)

                # если игрок и монстр живы и соприкасаются
                if not player.is_dead and not h.is_dead and player.rect.colliderect(h.rect):
                    # если игрок упал сверху
                    if player.rect.bottom - player.change_y < h.rect.top:
                        h.kill(enemy_dead_image)
                        player.jump()
                        score += 1
                        spawn_delay = INIT_DELAY / (DECREASE_BASE ** score)
                    else:
                        player.kill(player_image)

            # расположение очков во время игры
            score_rect.midtop = (SCREEN_WIDTH // 2, 5)

        screen.blit(score_surface, score_rect)
        pygame.display.update()
        # ограничение по кадрам в секунду
        clock.tick(FPS)


def start_menu():
    menu = pygame_menu.Menu('Slowking', 400, 300,
                           theme=pygame_menu.themes.THEME_BLUE)

    menu.add.button('Играть', start_the_game)
    menu.add.button('Рекорды', get_best)
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

start_menu()