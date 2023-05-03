# Документация https://www.pygame.org/docs/
# Шрифты https://fonts.google.com/
# Иконки https://www.iconfinder.com/

# импорт библиотеки
import pygame

# инициализируем пайгейм
pygame.init()

# ширина и высота экрана
SIZE_WIDTH, SIZE_HEIGHT = 1180, 860
# создание самого экрана
screen = pygame.display.set_mode((SIZE_WIDTH, SIZE_HEIGHT), )

# название игры
pygame.display.set_caption("Slowking")

# счетчик кадров в секунду
FPS = 30
# часы
clock = pygame.time.Clock()

# шрифты
# font_large = pygame.font.Font('fonts/Ubuntu-Light.ttf', 48)
# font_small = pygame.font.Font('fonts/Ubuntu-Light.ttf', 24)

bg = pygame.image.load('images/background/bg.png').convert_alpha()
ground = pygame.image.load('images/background/ground.png').convert_alpha()

# Выстрелы
shots_left = 5 # осталось выстрелов
shot = pygame.image.load('images/shot.png').convert_alpha()
shots = []

monster = pygame.image.load('images/monster.png').convert_alpha()
monster_list_in_game = []



# расположение текста
# retry_text = font_small.render('Press any key', True, (255, 255, 255))
# retry_rect = retry_text.get_rect()
# retry_rect.midtop = (SIZE_WIDTH // 2, SIZE_HEIGHT // 2)

# класс для создания главного игрока
class Player(pygame.sprite.Sprite):
    # стандартное направление игрока вправо
    right = True

    # конструктор класса
    def __init__(self):
        # наследование родительских методов
        super().__init__()

        # подключение изображения игрока
        self.image = pygame.image.load('images/player_right/player_right_1.png').convert_alpha()
        # прямоугольник вокруг изображения
        self.rect = self.image.get_rect()

        # направление движения при нажатии на клавиши
        self.change_x = 0
        self.change_y = 0

    # функция передвижения игрока
    def update(self):
        # подключаем гравитацию
        self.calc_grav()

        # движение вправо/влево
        self.rect.x += self.change_x

        # проверка столкновения с предметами
        contact_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        # перебираем возможные объекты для столкновения по горизонтали
        for contact in contact_list:
            # при движении вправо, остановимся в левой координате прямоугольника
            if self.change_x > 0:
                self.rect.right = contact.rect.left
            # при движении влево, остановимся в правой координате прямоугольника
            elif self.change_x < 0:
                self.rect.left = contact.rect.right

        # движение вверх/вниз
        self.rect.y += self.change_y

        # проверка столкновения с предметами
        contact_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        # перебираем возможные объекты для столкновения по вертикали
        for contact in contact_list:
            # при падении вниз, остановимся в верхней координате прямоугольника
            if self.change_y > 0:
                self.rect.bottom = contact.rect.top
            # при прыжке вверх, остановимся в нижней координате прямоугольника
            elif self.change_x < 0:
                self.rect.top = contact.rect.bottom

            # останавливаем вертикальное движение
            self.change_y = 0

    # подключаем гравитацию
    def calc_grav(self):
        # если в воздухе
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.9

        # если на земле
        if self.rect.y >= SIZE_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SIZE_HEIGHT - self.rect.height

    # прыжок
    def jump(self):
        # опускаемся и проверяем столкновение, затем поднимаемся обратно
        self.rect.y += 10
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 10

        # если соприкосновения нет
        if len(platform_hit_list) > 0 or self.rect.bottom >= SIZE_HEIGHT:
            self.change_y = -16

    # движение вправо
    def go_right(self):
        # устанавливаем скорость движения вправо
        self.change_x = 9
        if (not self.right):
            self.flip()
            self.right = True

    # движение влево
    def go_left(self):
        # устанавливаем скорость движения влево
        self.change_x = -9
        # если смотрел вправо, зеркально развернем
        if (self.right):
            self.flip()
            self.right = False

    # при бездействии на клавиатуре игрок стоит на месте
    def stop(self):
        self.change_x = 0

    # зеркальное отражение игрока
    def flip(self):
        # переворачиваем изображение / по оси Х True / по оси Y False
        self.image = pygame.transform.flip(self.image, True, False)


# класс платформ
class Platform(pygame.sprite.Sprite):
    # конструктор класса
    def __init__(self, width, height):
        # наследование родительских методов
        super().__init__()

        # подключение изображения платформы
        self.image = pygame.image.load('images/background/platform.png').convert_alpha()
        # прямоугольник вокруг изображения
        self.rect = self.image.get_rect()


class Ground(pygame.sprite.Sprite):
    # конструктор класса
    def __init__(self, width, height):
        super().__init__()

        # подключение изображения платформы
        self.image = pygame.image.load('images/background/ground.png').convert_alpha()
        # прямоугольник вокруг изображения
        self.rect = self.image.get_rect()


# базовый класс для каждого уровня
class Level:
    # конструктор класса
    def __init__(self, player):
        # создаем группу спрайтов платформ
        self.platform_list = pygame.sprite.Group()
        # ссылка на игрока
        self.player = player

    # функция обновления спрайтов группы платформ
    def update(self):
        self.platform_list.update()

    # функция рисования платформ на экране
    def draw(self, screen):
        # фон игры
        screen.blit(bg, (0, 0))

        # земля
        screen.blit(ground, (0, 0))

        # рисуем все платформы из группы спрайтов
        self.platform_list.draw(screen)

        # рисуем все платформы из группы спрайтов
        self.platform_list.draw(screen)


# Класс, что описывает где будут находится все платформы
# на определенном уровне игры
class Level_01(Level):
    def __init__(self, player):
        # Вызываем родительский конструктор
        Level.__init__(self, player)

        # Массив с данными про платформы. Данные в таком формате:
        # ширина, высота, x и y позиция
        level = [[210, 32, 500, 500],
                 [210, 32, 200, 400],
                 [210, 32, 600, 300]
                 ]

        # Перебираем массив и добавляем каждую платформу в группу спрайтов - platform_list
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        Ground(0, 500)


def play():
    # создаем слоупока
    player = Player()

    # Создаем все уровни
    level_list = []
    level_list.append(Level_01(player))

    # Устанавливаем текущий уровень
    current_level_no = 0
    current_level = level_list[current_level_no]

    # создаем группу для объединия наших спрайтов
    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    # начальные координаты
    player.rect.x = 300
    player.rect.y = SIZE_HEIGHT - player.rect.height
    # добавление игрока в группу спрайтов
    active_sprite_list.add(player)

    # бесконечный цикл чтобы не закрывалось окно до тех пор, пока это не выполнят принудительно
    running = True
    while running:
        # обновление дисплея
        pygame.display.update()

        # перебор всех событий, происходящих в пайгейм
        for event in pygame.event.get():
            # проверка события на закрытие
            if event.type == pygame.QUIT:
                running = False

            # отслеживание события нажатия на клавиши при нажатии на кнопку
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()

            # отслеживание события нажатия на клавиши при отпуске кнопки
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        if monster_list_in_game:
            for (i, el) in enumerate(monster_list_in_game):
                screen.blit(monster, el)
                el.x -= 50

                # Удаление монстра вне поле игры
                if el.x < -10:
                    monster_list_in_game.pop(i)
                    score += 1

                # Условие соприкосновения
                if player_rect.colliderect(el):
                    print("You lose")
                    gameplay = False

        # обновляем спрайт игрока
        active_sprite_list.update()
        # Обновляем объекты на экране
        current_level.update()

        # ограничение движения справа
        if player.rect.right > SIZE_WIDTH:
            player.rect.right = SIZE_WIDTH
        # ограничение движения слева
        if player.rect.left < 0:
            player.rect.left = 0

        current_level.draw(screen)
        # рисуем спрайт нашего игрока
        active_sprite_list.draw(screen)

        # установка ограничения по кадрам в секунду
        clock.tick(FPS)

    quit()

play()