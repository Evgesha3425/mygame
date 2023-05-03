import pygame
import random

# инициализируем пайгейм
pygame.init()

# Ширина и высота экрана
W = 800
H = 600

# Создаем сам экран
screen = pygame.display.set_mode((W, H), )

# счетчик кадров в секунду
FPS = 60
# часы
clock = pygame.time.Clock()

# шрифты
font_large = pygame.font.Font('fonts/Ubuntu-Light.ttf', 48)
font_small = pygame.font.Font('fonts/Ubuntu-Light.ttf', 24)

# проиграли или еще играем
game_over = False

# текстовая поверхность для перезапуска игры
retry_text = font_small.render('PRESS ANY KEY', True, (255, 255, 255))
# прямоугольник вокруг текста
retry_rect = retry_text.get_rect()
# расположение прямоугольника
retry_rect.midtop = (W // 2, H // 2)

# загружаем картинки
bg_image = pygame.image.load('images/background/bg.png').convert_alpha()

ground_image = pygame.image.load('images/background/ground.png').convert_alpha()
GROUND_H = ground_image.get_height()

monster_image = pygame.image.load('images/monst.png').convert_alpha()
monster_dead_image = pygame.image.load('images/monster.png').convert_alpha()

player_image = pygame.image.load('images/player.png').convert_alpha()
player_dead_image = pygame.image.load('images/monster.png').convert_alpha()


# класс существ
class Entity:
    # конструктор класса
    def __init__(self, image):
        # изображение существа
        self.image = image
        # прямоугольник вокруг существа
        self.rect = self.image.get_rect()
        # скорость по х и у
        self.x_speed = 0
        self.y_speed = 0
        # скорость для перемещения
        self.speed = 5
        # в пределах карты мы или нет
        self.is_out = False
        # живы или нет
        self.is_dead = False
        # скорость прыжка
        self.jump_speed = -5
        # гравитация
        self.gravity = 0.5
        # находимся ли на земле
        self.is_grounded = False

    # отслеживание управления
    def handle_input(self):
        pass

    # уничтожение сущности
    def kill(self, dead_image):
        # меняем картинку
        self.image = dead_image
        # меняем что сущность мертва
        self.is_dead = True
        # инвертируем скорость при смерти
        self.x_speed = -self.x_speed
        # после смерти подкидывается сущность
        self.y_speed = self.jump_speed

    # для обновления отрисовки движения
    def update(self):
        # перемещение за счет изменения скорости
        self.rect.x += self.x_speed
        # передвижение за счет изменения скорости вместе с гравитацией
        self.rect.y += self.y_speed
        # изменяем скорость прибавляя гравитацию
        self.y_speed += self.gravity

        # если мы уже мертвы
        if self.is_dead:
            # верхняя граница больше (высота экрана - высота земли)
            if self.rect.top > H - GROUND_H:
                self.is_out = True
        # если живы, то ходим по земле
        else:
            self.handle_input()
            # проверяем чтобы не выпали за пределы игры
            # нижняя граница больше (высота экрана - высота земли)
            if self.rect.bottom > H - GROUND_H:
                self.is_grounded = True
                self.y_speed = 0
                self.rect.bottom = H - GROUND_H

    # для отрисовки сущности
    def draw(self, surface):
        surface.blit(self.image, self.rect)


# создаем класс игрока
class Player(Entity):
    # конструктор класса
    def __init__(self):
        # наследуемся от родительство класса
        super().__init__(player_image)
        self.respawn()

    # переопределим управление для игрока
    def handle_input(self):
        # обнуляем скорость по х
        self.x_speed = 0

        # проверка нажатия на клавиши
        keys = pygame.key.get_pressed()
        # двигаем игрока влево
        if keys[pygame.K_LEFT]:
            self.x_speed = -self.speed
        # двигаем игрока вправо
        elif keys[pygame.K_RIGHT]:
            self.x_speed = self.speed

        # проверяем можем ли прыгнуть (стоим на земле)
        if self.is_grounded and keys[pygame.K_UP]:
            self.is_grounded = False
            self.jump()

    # для рестарта игры
    def respawn(self):
        # что игрок еще в пределах экрана
        self.is_out = False
        # что игрок еще жив
        self.is_dead = False
        # возвращаем игрока в центр экрана
        self.rect.midbottom = (W // 2, H - GROUND_H)

    # функция для прыжка
    def jump(self):
        # меняем скорость по y
        self.y_speed = self.jump_speed


# создаем класс монстра
class Monster(Entity):
    # конструктор класса
    def __init__(self):
        super().__init__(monster_image)
        # создание монстров
        self.spawn()

    # выпуск врагов
    def spawn(self):
        # выбор направления, откуда появляются монстры
        direction = random.randint(0, 1)

        if direction == 0:
            # двигаемся из левой части экрана вправо
            self.x_speed = self.speed
            self.rect.bottomright = (0, 300)
        else:
            # двигаемся из правой части экрана влево
            self.x_speed = -self.speed
            self.rect.bottomleft = (W, 300)

    def update(self):
        super().update()
        # если монстр уходит за пределы влево или вправо
        if self.x_speed > 0 and self.rect.left > W or self.x_speed < 0 and self.rect.right < 0:
            self.is_out = True


# создаем игрока
player = Player()
# внутриигровые очки
score = 0

# список всех монстров на экране
monsters = []
# начальная задержка создания монстров
INIT_DELAY = 2000
# частота создания монстров
spawn_delay = INIT_DELAY
# коэффициент увеличения сложности
DECREASE_BASE = 1.01
# хранение последнего времени создания монстра
last_spawn_time = pygame.time.get_ticks()


# основной цикл
running = True
while running:
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
                spawn_delay = INIT_DELAY
                last_spawn_time = pygame.time.get_ticks()
                player.respawn()
                monsters.clear()

        # ограничение по кадрам в секунду
        clock.tick(FPS)

        # заливка экрана
        screen.fill((92, 148, 252))
        # screen.blit(bg_image, (0, 0))

        # вставляем землю
        screen.blit(ground_image, (0, H - GROUND_H))

        # поверхность для отрисовки очков
        score_text = font_large.render(str(score), True, (0, 0, 0))
        score_rect = score_text.get_rect()

        # при проигрыше
        if player.is_out:
            # расположение очков после смерти
            score_rect.midbottom = (W // 2, H // 2)
            # поверхность с перезапуском
            screen.blit(retry_text, retry_rect)
        # если еще живы
        else:
            # обновляем игрока для отображения
            player.update()
            player.draw(screen)

            # текущее игровое время
            now = pygame.time.get_ticks()
            # время с момента последнего создания монстра
            elapsed = now - last_spawn_time
            # проверяем вышла ли задержка и можно ли создавать монстра
            if elapsed > spawn_delay:
                # зафиксировали последнее время создания монстра
                last_spawn_time = now
                # добавляем нового монстра в список монстров на экране
                monsters.append(Monster())

                # перебираем всех монстров из копии списка монстров
                for monster in list(monsters):
                    # удаляем монстра если он за пределами экрана
                    if monster.is_out:
                        monsters.remove(monster)
                    # обновляем если он живой
                    else:
                        monster.update()
                        monster.draw(screen)

                    # если игрок и монстр живы и соприкасаются
                    if not player.is_dead and not monster.is_dead and player.rect.colliderect(monster):
                        # если игрок упал сверху
                        if player.rect.bottom - player.y_speed < monster.rect.top:
                            monster.kill(monster_dead_image)
                            player.jump()
                            score += 1
                            spawn_delay = INIT_DELAY / (DECREASE_BASE ** score)
                        # если игрок коснулся монстра в другом варианте
                        else:
                            player.kill(player_image)
            # расположение очков во время игры
            score_rect.midtop = (W // 2, 5)

        screen.blit(score_text, score_rect)

        # обновление дисплея
        pygame.display.update()

quit()
