import pygame

# Инициализируем игру
pygame.init()
# Размеры для экрана игры (передается кортеж). Параметр flags=pygame.NOFRAME уберет рамку вокруг игры
screen = pygame.display.set_mode((600, 300), )
# Добавялем название для приложения
pygame.display.set_caption("Beetle")
# Подгружаем изображение и устанавливаем его как иконку для проекта
icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)

running = True

# Добавляем цикл, чтобы программа сразу же не закрывалась
while running:
    # screen.fill((114, 157, 224))

    pygame.display.update()  #Постоянно обновляем экран нашего приложения


    for event in pygame.event.get():  #pygame.event.get() - список со всеми возможными событиями
        # Добавляем условие корректного закрытия игры
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        # Проверяем событие на нажатие клавиши
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                screen.fill((70, 44, 133))

