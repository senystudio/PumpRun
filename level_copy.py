import pygame
import sys
import random
import math
from pygame.locals import *
import time
import pygame.mixer
import csv

pygame.mixer.init()

# Загрузка фоновой музыки
pygame.mixer.music.load(
    'project/Chuck_Berry_-_You_Never_Can_Tell.mp3')  # Замените 'background_music.mp3' на путь к вашему аудиофайлу
pygame.mixer.music.set_volume(0.5)  # Установите уровень громкости (от 0.0 до 1.0)
pygame.mixer.music.play(-1)

killed_enemies_count = 0
ost_hp = 0


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    global ost_hp

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.animation_count = 0
        self.image = player_image[self.animation_count]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.speed = 5
        self.direction = 1
        self.hp = 100  # Начальное здоровье

    def update(self):
        keys = pygame.key.get_pressed()
        collision_wall = pygame.sprite.groupcollide(player_group, wall_group, False, False)

        if keys[pygame.K_a]:
            if not collision_wall:
                for sprite in all_sprites:
                    sprite.rect.x += self.speed
                self.rect.x -= self.speed
                self.direction = -1
                self.animation_count = (self.animation_count + 1) % len(player_image)
                self.image = pygame.transform.flip(player_image[self.animation_count], self.direction == -1, False)
                return
            else:
                self.rect.x += 50
                return

        if keys[pygame.K_d]:
            if not collision_wall:
                for sprite in all_sprites:
                    sprite.rect.x -= self.speed
                self.rect.x += self.speed
                self.direction = 1
                self.animation_count = (self.animation_count + 1) % len(player_image)
                self.image = pygame.transform.flip(player_image[self.animation_count], self.direction == -1, False)
                return
            else:
                self.rect.x -= 50
                return

        if keys[pygame.K_w]:
            if not collision_wall:
                for sprite in all_sprites:
                    sprite.rect.y += self.speed
                self.rect.y -= self.speed
                self.animation_count = (self.animation_count + 1) % len(player_image)
                self.image = pygame.transform.flip(player_image[self.animation_count], self.direction == -1, False)
                return
            else:
                self.rect.y += 50
                return

        if keys[pygame.K_s]:
            if not collision_wall:
                for sprite in all_sprites:
                    sprite.rect.y -= self.speed
                self.rect.y += self.speed
                self.animation_count = (self.animation_count + 1) % len(player_image)
                self.image = pygame.transform.flip(player_image[self.animation_count], self.direction == -1, False)
                return
            else:
                self.rect.y -= 50
                return

        enemy_collisions = pygame.sprite.spritecollide(self, enemi_group, False)
        trophy_collisions = pygame.sprite.spritecollide(self, trophy_group, False)

        if trophy_collisions:
            display_buttons()

        for enemy in enemy_collisions:
            self.hp -= 1
            ost_hp = self.hp
        # Проверка на отрицательное здоровье (если нужно)
        if self.hp < 0:
            self.hp = 0


class Weapon(pygame.sprite.Sprite):
    def __init__(self, player_rect, mouse_position):
        super().__init__()
        self.original_image = pygame.transform.scale(load_image("bullet.png"),
                                                     (60, 30))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = player_rect.center
        self.direction = math.atan2(mouse_position[1] - player_rect.centery,
                                    mouse_position[0] - player_rect.centerx)
        self.speed = 25

    def update(self):
        self.rect.x += self.speed * math.cos(self.direction)
        self.rect.y += self.speed * math.sin(self.direction)

        if self.rect.x > width or self.rect.x < 0 or self.rect.y > height or self.rect.y < 0:
            self.kill()

        # Rotate the image based on the direction
        self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.direction))
        wall_hit_list = pygame.sprite.spritecollide(self, wall_group, False)
        for wall in wall_hit_list:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(enemi_group, all_sprites)
        self.animation_count = 0
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.speed = 5
        self.reset_offset = 0
        self.offset_x = random.randrange(-300, 300)
        self.offset_y = random.randrange(-300, 300)
        self.hp = 100
        self.shoot_cooldown = 60
        self.shoot_timer = 0

    def update(self):
        # Calculate the target position as the center of the screen
        target_x, target_y = width // 2, height // 2
        distance_to_player = math.hypot(target_x - self.rect.x, target_y - self.rect.y)

        # Check if the player is within a certain radius before starting movement
        if distance_to_player < 300:
            # Логика движения врага
            if self.reset_offset == 0:
                self.offset_x = random.randrange(-300, 300)
                self.offset_y = random.randrange(-300, 300)
                self.reset_offset = random.randrange(80, 150)
            else:
                self.reset_offset -= 1

                # Check for collision with walls
                if not pygame.sprite.spritecollideany(self, wall_group, collided=pygame.sprite.collide_rect):
                    if target_x > self.rect.x:
                        self.rect.x += 1
                    else:
                        self.rect.x -= 1

                    if target_y > self.rect.y:
                        self.rect.y += 1
                    else:
                        self.rect.y -= 1

        # Обновление анимации врага
        self.animation_count = (self.animation_count + 1) % len(enemi_image)
        self.image = enemi_image[self.animation_count]


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, delay=0.5):
        super().__init__()

        self.images = [pygame.transform.scale(load_image('krest.png'), (80, 80))]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.delay = delay
        self.start_time = time.time()

    def update(self):
        current_time = time.time()

        if current_time - self.start_time >= self.delay:
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]


player_spr = None
enemy_spr = None
display_scroll = [0, 0]


class Field:
    def __init__(self, file_path):
        self.field_data = self.load_level(file_path)
        self.sprite_size = 50

    def load_level(self, file_path):
        with open(file_path, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '-'), level_map))

    def generate_level(self):
        global player_spr, enemy_spr
        for y, row in enumerate(self.field_data):
            for x, cell in enumerate(row):
                if self.field_data[y][x] == '.':
                    Tile('empty', x, y)
                elif self.field_data[y][x] == 'h':
                    Tile('winner_h', x, y)
                elif self.field_data[y][x] == 'b':
                    Tile('winner_b', x, y)
                elif self.field_data[y][x] == '#':
                    Tile('wall', x, y)
                    wall_group.add(Tile('wall', x, y))
                elif self.field_data[y][x] == '-':
                    Tile('back', x, y)
                elif self.field_data[y][x] == '+':
                    Tile('island_fence', x, y)
                elif self.field_data[y][x] == '^':
                    Tile('island_square_fence', x, y)
                elif self.field_data[y][x] == 'a':
                    Tile('island_floor_stone', x, y)
                elif self.field_data[y][x] == '@':
                    Tile('empty', x, y)
                    player_spr = Player(x * self.sprite_size, y * self.sprite_size)  # Создание "Игрока"
                    player_group.add(player_spr)
                elif self.field_data[y][x] == '*':
                    Tile('over', x, y)
                elif self.field_data[y][x] == '6':
                    Tile('hot', x, y)
                elif self.field_data[y][x] == 'C':
                    Tile('island_floor_stone', x, y)
                    Tile('prize', x, y)
                    trophy_group.add(Tile('prize', x, y))
                elif self.field_data[y][x] == 't':
                    Tile('over', x, y)
                    Tile('plant', x, y)
                elif self.field_data[y][x] == 'F':
                    Tile('over', x, y)
                    Tile('decor', x, y)
                elif self.field_data[y][x] == 'P':
                    Tile('over', x, y)
                    Tile('tree', x, y)
                elif self.field_data[y][x] == '/':
                    Tile('over', x, y)
                    Tile('road', x, y)
                elif self.field_data[y][x] == '1':
                    Tile('empty', x, y)
                    enemy_image = pygame.transform.scale(load_image("yeti (47).png"), (70, 70))

                    # Создание объекта Enemy с загруженным изображением
                    enemy_spr = Enemy(x * self.sprite_size, y * self.sprite_size, enemy_image)
                    enemi_group.add(enemy_spr)


def load_image(filename):
    filename = 'project/' + filename
    return pygame.image.load(filename).convert_alpha()


def terminate():
    pygame.quit()
    sys.exit()


def error_screen():
    text = ['Произошла ошибка',
            'Нажмите любую клавишу',
            'для выхода из игры']

    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    fon1 = pygame.transform.scale(load_image('Background02.png'), (width, height))
    screen.blit(fon1, (0, 0))

    fon2 = pygame.transform.scale(load_image('Muntain.png'), (width, height))
    screen.blit(fon2, (0, 0))

    fon3 = pygame.transform.scale(load_image('Cloud.png'), (width, height))
    screen.blit(fon3, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


# filename = str(input('название файла: '))
filename = 'pole.txt'
pygame.init()
size = width, height = 1500, 800

screen = pygame.display.set_mode(size)
FPS = 120
clock = pygame.time.Clock()

start_screen()

tile_images = {'wall': pygame.transform.scale(load_image('bricks.jpg'), (50, 50)),
               'empty': pygame.transform.scale(load_image('floor.png'), (50, 50)),
               'winner_h': pygame.transform.scale(load_image('white_block.png'), (50, 50)),
               'winner_b': pygame.transform.scale(load_image('black_block.png'), (50, 50)),
               'back': pygame.transform.scale(load_image('fon_colour.png'), (50, 50)),
               'over': pygame.transform.scale(load_image('sand.png'), (50, 50)),
               'hot': pygame.transform.scale(load_image('lava.png'), (50, 50)),
               'island_fence': pygame.transform.scale(load_image('fence_3.png'), (50, 50)),
               'island_square_fence': pygame.transform.scale(load_image('square_fence.png'), (50, 50)),
               'island_floor_stone': pygame.transform.scale(load_image('floor_stone.png'), (50, 50)),
               'prize': pygame.transform.scale(load_image('trophy-gold.png'), (50, 50)),
               'road': pygame.transform.scale(load_image('carpet.jpg'), (50, 40)),
               'plant': pygame.transform.scale(load_image('tree.png'), (45, 45)),
               'decor': pygame.transform.scale(load_image('flower.png'), (45, 45)),
               'island_flood': pygame.transform.scale(load_image('flower.png'), (45, 45)),
               'tree': pygame.transform.scale(load_image('pink_tree.png'), (45, 45))}
player_image = [pygame.transform.scale(load_image(f"walk{i}.png"), (60, 60)) for i in range(1, 11)]
enemi_image = [pygame.transform.scale(load_image(f"yeti ({i}).png"), (50, 50)) for i in range(1, 48)]

tile_width = tile_height = 50

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
field_group = pygame.sprite.Group()
enemi_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
trophy_group = pygame.sprite.Group()
# player_spr = Player(width // 2, height // 2)
# player_group.add(player_spr)

fields = Field(filename)
fields.generate_level()

for sprite in tiles_group:
    field_group.add(sprite)


def update_hp_text(player_hp):
    font = pygame.font.Font('project/one piece font.ttf', 36)
    if player_hp <= 80 and player_hp >= 40:
        text_color = (255, 205, 255)
    elif player_hp <= 40:
        text_color = (255, 0, 0)
    else:
        text_color = (255, 255, 255)

    player_hp = '%.1f' % player_hp
    text = font.render(f'HP: {player_hp}', True, text_color)
    screen.blit(text, (10, 10))
    screen.blit(text, (10, 10))


restart_limit = 1

font = pygame.font.SysFont('project/one piece font.ttf', 40)
objects = []


class Button():
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress

        self.fillColors = {
            'normal': '#fff490',
            'hover': '#666666',
            'pressed': '#333333',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))

        self.alreadyPressed = False

        objects.append(self)

    def process(self):

        mousePos = pygame.mouse.get_pos()

        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])

                if self.onePress:
                    self.onclickFunction()

                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True

            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)


amount = 0

font_killed_enemies = pygame.font.Font('project/one piece font.ttf', 36)


def update_killed_enemies_text(count):
    global amount
    text_killed_enemies = font_killed_enemies.render(f'Killed Enemies: {count}', True, (255, 255, 255))
    screen.blit(text_killed_enemies, (10, 50))
    amount = count


is_window_open = True
game_over = False
start_time = time.time()
current_time = 0


def display_buttons():
    global is_window_open, game_over, current_time
    pygame.init()
    screen = pygame.display.set_mode((1500, 800))
    pygame.display.set_caption('Game Window')

    font = pygame.font.Font('project/one piece font.ttf', 36)  # Добавлен шрифт

    save_button = Button(300, 600, 400, 100, 'Save', saving_in_bd)
    quit_button = Button(850, 600, 400, 100, 'Quit', terminate)

    while is_window_open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_window_open = False
                terminate()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Process buttons' events
                for button in [save_button, quit_button]:
                    button.process()
        current_time = int(time.time() - start_time)  # в секундах

        end_fon1 = pygame.transform.scale(load_image('end_mountain (1).png'), (width, height))
        screen.blit(end_fon1, (0, 0))

        end_fon2 = pygame.transform.scale(load_image('end_mountain (2).png'), (width, height))
        screen.blit(end_fon2, (0, 0))

        end_fon3 = pygame.transform.scale(load_image('end_mountain (3).png'), (width, height))
        screen.blit(end_fon3, (0, 0))

        end_fon4 = pygame.transform.scale(load_image('end_mountain (4).png'), (width, height))
        screen.blit(end_fon4, (0, 0))

        end_fon5 = pygame.transform.scale(load_image('end_mountain (5).png'), (width, height))
        screen.blit(end_fon5, (0, 0))

        # Вывод количества набранных очков и времени прохождения
        score_text = font.render(f"Score: {amount}", True, ('#fff490'))
        time_text = font.render(f"Time: {current_time} seconds", True, ('#fff490'))
        health_text = font.render(f"HP: {ost_hp}", True, ('#fff490'))
        screen.blit(score_text, (20, 20))
        screen.blit(time_text, (20, 60))
        screen.blit(health_text, (20, 100))

        save_button.process()
        quit_button.process()
        pygame.display.flip()


# Сенина база данных: в ней хранятся количество убитых врагов и время, за которое была пройдена игра
# функция вычисление кличества убитых 428 строчка/amount
# время: current_time


def saving_in_bd():
    with open('records.csv', 'a') as file:
        file.write(f'{amount};{current_time}\n')


def get_all_records():
    with open('records.csv') as file:
        records = []
        for i in csv.reader(file, delimiter=';'):
            records.append(i)
        return records


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()


        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button click
            mouse_position = pygame.mouse.get_pos()
            # Shoot bullets towards the mouse click position
            weapon = Weapon(player_spr.rect, mouse_position)
            weapon_group.add(weapon)

            pos = pygame.mouse.get_pos()

            for object in objects:
                object.process()

    player_group.update()
    weapon_group.update()
    enemi_group.update()
    explosion_group.update()

    screen.fill((0, 0, 0))

    player_center = player_spr.rect.center
    screen_center = (width // 2, height // 2)
    screen_x, screen_y = screen_center[0] - player_center[0], screen_center[1] - player_center[1]
    for sprite in all_sprites:
        sprite.rect.x += screen_x
        sprite.rect.y += screen_y

    collisions = pygame.sprite.groupcollide(weapon_group, enemi_group, True, False)
    for bullet, hit_enemies in collisions.items():
        for enemy in hit_enemies:
            enemy.hp -= 20  # Decrease enemy's health on bullet hit
            if enemy.hp <= 0:
                # Create an explosion sprite at the enemy's position when killed
                explosion = Explosion(enemy.rect.x, enemy.rect.y)
                explosion_group.add(explosion)
                enemy.kill()
                killed_enemies_count += 1  # Increment the killed enemies count

    all_sprites.update()
    all_sprites.draw(screen)
    player_group.draw(screen)
    enemi_group.draw(screen)
    weapon_group.draw(screen)
    explosion_group.draw(screen)

    update_hp_text(player_spr.hp)
    if player_spr.hp == 0:
        display_buttons()  # Call the function to display buttons in a new window

    # update_restart_text(restart_count)
    update_killed_enemies_text(killed_enemies_count)

    pygame.display.flip()
    clock.tick(30)
