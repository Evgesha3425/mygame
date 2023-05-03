import pygame
import random
import test_menu

from database import get_best

pygame.init()


# screen
W = 800
H = 600
screen = pygame.display.set_mode((W, H))


def start_the_game():
    # fps
    FPS = 60
    clock = pygame.time.Clock()

    # font
    font_path = 'fonts/Ubuntu-Light.ttf'
    font_large = pygame.font.Font(font_path, 48)
    font_small = pygame.font.Font(font_path, 24)

    # spawn delay
    INIT_DELAY = 2000
    spawn_delay = INIT_DELAY
    DECREASE_BASE = 1.01
    last_spawn_time = pygame.time.get_ticks()

    # game fields
    game_over = False
    retry_text = font_small.render('PRESS ANY KEY', True, (255, 255, 255))
    retry_rect = retry_text.get_rect()
    retry_rect.midtop = (W // 2, H // 2)

    score = 0

    # images

    bg_image = pygame.image.load('images/background/bg_mini.png')

    ground_image = pygame.image.load('images/background/ground_mini.png')
    ground_image = pygame.transform.scale(ground_image, (804, 60))
    GROUND_H = ground_image.get_height()

    enemy_image = pygame.image.load('images/monst.png')
    enemy_image = pygame.transform.scale(enemy_image, (80, 80))

    enemy_dead_image = pygame.image.load('images/monst.png')
    enemy_dead_image = pygame.transform.scale(enemy_dead_image, (80, 80))

    player_image = pygame.image.load('images/player_mini.png')
    player_image = pygame.transform.scale(player_image, (60, 80))

    menu_bg = pygame.image.load('images/background/bg_menu.jpg')


# objects
    class Entity:
        def __init__(self, image):
            self.image = image
            self.rect = self.image.get_rect()
            self.change_y = 0
            self.change_x = 0
            self.speed = 5
            self.is_out = False
            self.is_dead = False
            self.jump_speed = -12
            self.gravity = 0.5
            self.is_grounded = False

        def handle_input(self):
            pass

        def kill(self, dead_image):
            self.image = dead_image
            self.is_dead = True
            self.change_x = -self.change_x
            self.change_y = self.jump_speed

        def update(self):
            # movement
            self.rect.x += self.change_x
            self.rect.y += self.change_y
            self.change_y += self.gravity

            if self.is_dead:
                # is out check
                if self.rect.top > H - GROUND_H:
                    self.is_out = True
            else:
                # x movement
                self.handle_input()

                if self.rect.bottom > H - GROUND_H:
                    self.is_grounded = True
                    self.change_y = 0
                    self.rect.bottom = H - GROUND_H

        def draw(self, surface):
            surface.blit(self.image, self.rect)


    class Goomba(Entity):
        def __init__(self):
            super().__init__(enemy_image)
            self.spawn()

        def spawn(self):
            direction = random.randint(0, 1)
            if direction == 0:
                self.change_x = -self.speed
                self.rect.bottomleft = (W, 0)
            else:
                self.change_x = self.speed
                self.rect.bottomright = (0, 0)

        def update(self):
            super().update()
            if self.change_x > 0 and self.rect.left > W or self.change_x < 0 and self.rect.right < 0:
                self.is_out = True


    class Player(Entity):
        def __init__(self):
            super().__init__(player_image)
            self.respawn()

        def handle_input(self):
            self.change_x = 0

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.change_x = -self.speed
            elif keys[pygame.K_d]:
                self.change_x = self.speed

            if self.is_grounded and keys[pygame.K_SPACE]:
                self.is_grounded = False
                self.jump()

        def respawn(self):
            self.is_out = False
            self.is_dead = False
            self.rect.midbottom = (W // 2, H)

        def jump(self):
            self.change_y = self.jump_speed

    class Platform(pygame.sprite.Sprite):
        def __init__(self, width, height):
            # Конструктор платформ
            super().__init__()
            # Также указываем фото платформы
            self.image = pygame.image.load('images/background/platform_mini.png').convert_alpha()

            # Установите ссылку на изображение прямоугольника
            self.rect = self.image.get_rect()


    # Класс для расстановки платформ на сцене
    class Level(object):
        def __init__(self, player):
            # Создаем группу спрайтов (поместим платформы различные сюда)
            self.platform_list = pygame.sprite.Group()
            # Ссылка на основного игрока
            self.player = player

        # Чтобы все рисовалось, то нужно обновлять экран
        # При вызове этого метода обновление будет происходить
        def update(self):
            self.platform_list.update()

        # Метод для рисования объектов на сцене
        def draw(self, screen):
            # Рисуем задний фон
            screen.blit(bg_image, (0, 0))

            # Рисуем все платформы из группы спрайтов
            self.platform_list.draw(screen)

    class Level_01(Level):
        def __init__(self, player):
            # Вызываем родительский конструктор
            Level.__init__(self, player)

            # Массив с данными про платформы. Данные в таком формате:
            # ширина, высота, x и y позиция
            level = [
                [600, 93, -20, 570],
                [600, 93, 190, 570],
                [600, 93, 400, 570],
                [600, 93, 610, 570],
                [210, 32, 500, 500],
                [210, 32, 200, 400],
                [210, 32, 600, 300],
            ]

            # Перебираем массив и добавляем каждую платформу в группу спрайтов - platform_list
            for platform in level:
                block = Platform(platform[0], platform[1])
                block.rect.x = platform[2]
                block.rect.y = platform[3]
                block.player = self.player
                self.platform_list.add(block)


    player = Player()

    goombas = []

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if player.is_out:
                    score = 0
                    finish_delay = INIT_DELAY
                    last_spawn_time = pygame.time.get_ticks()
                    player.respawn()
                    goombas.clear()


        clock.tick(FPS)

        # screen.fill((92, 148, 252))
        screen.blit(bg_image, (0, 0))
        screen.blit(ground_image, (0, H - GROUND_H))

        score_surface = font_large.render(str(score), True, (255, 255, 255))
        score_rect = score_surface.get_rect()

        if player.is_out:
            score_rect.midbottom = (W // 2, H // 2)

            screen.blit(retry_text, retry_rect)
        else:
            now = pygame.time.get_ticks()
            elapsed = now - last_spawn_time

            if elapsed > spawn_delay:
                last_spawn_time = pygame.time.get_ticks()
                goombas.append(Goomba())

            player.update()
            player.draw(screen)

            for goomba in list(goombas):
                if goomba.is_out:
                    goombas.remove(goomba)
                else:
                    goomba.update()
                    goomba.draw(screen)

                    if not player.is_dead and not goomba.is_dead and player.rect.colliderect(goomba.rect):
                        if player.rect.bottom - player.change_y < goomba.rect.top:
                            goomba.kill(enemy_dead_image)
                            player.jump()
                            score += 1
                            spawn_delay = INIT_DELAY / (DECREASE_BASE ** score)
                        else:
                            player.kill(player_image)

            # drawing score
            score_rect.midtop = (W // 2, 5)

        screen.blit(score_surface, score_rect)

        pygame.display.flip()
    quit()


menu = pygame_menu.Menu('Welcome', 400, 300,
                       theme=pygame_menu.themes.THEME_BLUE)
menu.add.text_input('Имя :', default='Игрок 1')
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)
menu.add.button('Records', get_best)

menu.mainloop(screen)
