from animations import entities_animations, dash_animation, EnemyDeath

from image_loader import load_image

from outsiders_objects import Particle

import pygame

import random


class Hero(pygame.sprite.Sprite):
    def __init__(self, screen, sprite, all_sprites, tile_sprites, pos):
        super().__init__(sprite, all_sprites)
        # ---
        self.tile_sprites = tile_sprites
        self.particle_sprite_group = pygame.sprite.Group()
        self.screen = screen
        self.hero_sizes = (14, 18)
        self.is_left = False
        # --- Взаимодействие с врагом
        self.enemy_sprite = None
        self.enemy_lst = []
        self.new_enemy_dict = {}
        # --- Все для слайда
        self.is_slide = False
        self.is_over = False
        self.slide_count = 0
        self.is_flight = True
        # --- Для прыжка и движения по горизонтали
        self.jumps = 2
        self.vel_y = 0
        self.is_jumping = False
        self.gravity = 0.2
        self.dx, self.dy = 0, 0
        # --- Для дэша персонажа
        self.is_dash = False
        self.dash_count = 0
        # --- Для слайда по стене
        self.is_wall_slide = False
        # --- Инициализация картинки, объявления хитбокса и положения относительно экрана
        self.image = pygame.transform.scale(load_image("images/entities/player/idle/0.png", -1),
                                            (self.hero_sizes[0] * 3.5, self.hero_sizes[1] * 3.5))
        # --- Настройка прямоугольгтка игрока
        self.rect = self.image.get_rect()
        self.rect.width //= 1.5
        self.rect.x, self.rect.y = pos
        self.old_rect = (self.rect.width, self.rect.height)
        # ---

    # Физика и анимация слайда
    def do_slide(self):
        '''Функция, отвечающаяя за слайд'''
        if self.is_slide:  # Если переменная is_slide is True, то выполняется слайд
            self.image = dash_animation("images/particles/particle/{}.png", "slide", 3, (12, 12), 3.5)
            self.enemy_collide()
            self.change_rect()
            self.check_collide(coof=3)
            self.rect.x = self.rect.x + self.dx * 3 if not self.is_left else self.rect.x + self.dx * 3
            self.slide_count += 1
        if self.slide_count >= 70:  # Если переменная slide_count >= 70, то слайд заканчивается
            self.kill_and_create_particles_sprites()
            self.is_over = False
            self.slide_count = 0
            self.is_slide = False
            self.rect.size = self.old_rect

    def do_horizontal_and_static_move(self, key):
        '''Функция, отвечающаяя за горизонтальное и статическое положение игрока'''
        if key[pygame.K_d]:
            self.is_left = False
            if not self.is_jumping and not self.is_dash:
                self.image = entities_animations("images/entities/player/run/{}.png",
                                                 "run", 7, (14, 18), 3.5, self.is_left)
            elif self.is_jumping:
                self.image = entities_animations("images/entities/player/jump/{}.png",
                                                 "jump", 1, (14, 18), 3.5, self.is_left)
            self.dx += 2

        elif key[pygame.K_a]:
            self.is_left = True
            if not self.is_jumping and not self.is_dash:
                self.image = entities_animations("images/entities/player/run/{}.png",
                                                 "run", 7, (14, 18), 3.5, self.is_left)
            elif self.is_jumping:
                self.image = entities_animations("images/entities/player/jump/{}.png",
                                                 "jump", 1, (14, 18), 3.5, self.is_left)
            self.dx -= 2
        else:
            if not self.is_jumping and not self.is_dash:
                if not self.is_jumping:
                    self.image = entities_animations("images/entities/player/idle/{}.png", "idle",
                                                     21, (14, 18), 3.5,
                                                     self.is_left)

    def do_dash(self):
        '''Функция, отвечающаяя за дэш'''
        if not self.is_jumping:
            self.image = entities_animations("images/entities/player/slide/{}.png", "slide",
                                             1, (14, 18), 3, self.is_left)

        self.change_rect()
        self.check_collide(coof=2)
        self.rect.x = self.rect.x + self.dx * 2 if not self.is_left else self.rect.x + self.dx * 2
        self.dash_count += 1
        if self.dash_count == 50:
            self.dash_count = 0
            self.is_dash = False
            self.rect.size = self.old_rect

    def kill_and_create_particles_sprites(self):
        '''Функция, отвечающаяя за создание и удаление объектов Particles'''
        for i in self.particle_sprite_group:
            i.kill()
        [Particle(self.particle_sprite_group, (self.rect.x, self.rect.y), False, self.screen,
                  tuple(random.choice(list(range(1, 4)) +
                                      list(range(-3, 0))) for i in range(2))) for i in range(20)]

    def kill_enemies(self):
        for enemy in self.enemy_lst:
            if enemy not in self.new_enemy_dict.keys():
                self.new_enemy_dict[enemy] = EnemyDeath("images/entities/enemy/death/{}.png",
                                                        20, (14, 18), 3.5, enemy, self.is_left)
            self.enemy_lst.remove(enemy)
        for enemy, animation in self.new_enemy_dict.copy().items():
            enemy.image = animation.get_image()
            animation.update_animation()
            if animation.index_of_enemy_pic == animation.count_of_files - 1:
                enemy.kill()
                self.new_enemy_dict.pop(enemy)

    def keys_down_up_move(self, event):
        if event is not None and event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_w or pygame.key.get_pressed()[pygame.K_SPACE]) and self.jumps:
                self.check_collide()
                self.is_jumping = True
                self.gravity = 0.2
                self.vel_y = -7 if self.jumps > 0 else self.vel_y
                self.jumps -= 1

                self.image = entities_animations("images/entities/player/jump/{}.png",
                                                 "jump", 1, (14, 18), 3.5, self.is_left)
                sound_jump = pygame.mixer.Sound('data/sfx/jump.wav')
                sound_jump.set_volume(0.3)
                sound_jump.play()


            elif event.key == pygame.K_LSHIFT:
                self.is_over = True
                for i in self.particle_sprite_group:
                    i.kill()
                self.image = pygame.transform.scale(load_image("images/particles/particle/0.png",
                                                               -1), (25, 25))
                self.is_slide = True
                self.check_collide()
                sound_dash = pygame.mixer.Sound('data/sfx/dash.wav')
                sound_dash.set_volume(0.2)
                sound_dash.play()
            elif event.key == pygame.K_LCTRL:
                self.is_dash = True
                sound_slide = pygame.mixer.Sound('data/sfx/slide.mp3')
                sound_slide.set_volume(0.2)
                sound_slide.play()
            elif event is not None and event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL:
                    self.rect.size = self.old_rect
                    self.is_dash = False
                    self.dash_count = 0
                if event.key == pygame.K_LSHIFT:
                    self.is_slide = False
                    self.rect.size = self.old_rect
                    self.slide_count = 0
                    if self.is_over:
                        self.kill_and_create_particles_sprites()

    def enemy_collide(self):
        for enemy in self.enemy_sprite:
            if enemy.rect.colliderect(self.rect):
                if enemy not in self.enemy_lst:
                    self.enemy_lst.append(enemy)

    def check_collide(self, coof=1):
        for tile in self.tile_sprites:
            if tile.rect.colliderect(self.rect.x, self.rect.y + self.dy, self.rect.width, self.rect.height):
                if self.rect.top > tile.rect.centery:
                    self.rect.top = tile.rect.bottom
                else:
                    self.rect.bottom = tile.rect.top - 1
                    self.dy = 0
                    self.vel_y = 0
                    self.jumps = 2
                    self.is_jumping = False

            if tile.rect.colliderect(self.rect.x + self.dx * coof, self.rect.y, self.rect.width, self.rect.height):
                self.rect.size = self.old_rect
                self.dx = 0
                self.is_dash = False
                self.is_slide = False
                self.jumps = 2
                self.is_jumping = False
                if self.is_left:
                    self.image = pygame.transform.scale(load_image("images/entities/player/wall_slide/1.png", -1, self.is_left),
                                                        (self.hero_sizes[0] * 3.5, self.hero_sizes[1] * 3.5))
                else:
                    self.image = pygame.transform.scale(load_image("images/entities/player/wall_slide/0.png", -1),
                                                        (self.hero_sizes[0] * 3.5, self.hero_sizes[1] * 3.5))

            if tile.rect.colliderect(self.rect):
                if self.rect.right < tile.rect.centerx:
                    self.rect.right = tile.rect.left
                elif self.rect.left > tile.rect.centerx:
                    self.rect.left = tile.rect.right
                if self.rect.top >= tile.rect.centery:
                    self.rect.top = tile.rect.bottom
                else:
                    self.rect.bottom = tile.rect.top
                    self.jumps = 2
                    self.dy = 0
                    self.vel_y = 0
                    self.is_jumping = False

    def change_rect(self, pos=(0, 0), change_height=0):
        pos = pos if pos[0] != 0 and pos[1] != 0 else (self.rect.x, self.rect.y)
        self.rect = self.image.get_rect()
        if change_height:
            self.rect.height = change_height
        self.rect.x, self.rect.y = pos

    def player_rotate(self, event=None):
        '''Функция, отвечающаяя за перемещение игровка по экрану'''
        self.kill_enemies()

        self.dx, self.dy = 0, 0

        self.do_horizontal_and_static_move(pygame.key.get_pressed())

        self.keys_down_up_move(event=event)

        # Физика и анимация движения по горизонтали и статического положения
        self.check_collide()
        self.vel_y += self.gravity
        if self.vel_y > 7:
            self.vel_y = 7
            self.is_jumping = False
        self.dy += self.vel_y

        # Физика дэша
        if self.is_dash and not self.is_jumping:
            self.do_dash()

        # Физика слайда
        self.do_slide()
        if self.is_slide:
            return

        if self.particle_sprite_group:  # Если есть спрайты в спрайт-группе
            self.particle_sprite_group.update()
            self.particle_sprite_group.draw(self.screen)

        self.check_collide()

        self.rect.x += self.dx
        self.rect.y += self.dy

    def update(self, enemy_sprite, event=None):
        self.enemy_sprite = enemy_sprite
        self.player_rotate(event=event)


class Enemies(pygame.sprite.Sprite):
    def __init__(self, screen, enemies_sprite_group, all_sprite_group, tile_sprite_group, pos):
        super().__init__(enemies_sprite_group, all_sprite_group)
        self.tile_sprite_group = tile_sprite_group
        self.screen = screen
        self.dx = random.choice([-1, 1])
        self.is_left = False if self.dx > 0 else True
        self.image = EnemyDeath("images/entities/enemy/idle/{}.png",
                                15, (14, 18), 3.5, self.is_left).get_image()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        # self.rect.width //= 2
        # self.rect.height //= 1.25

        self.count = 0

    def check_collison(self):
        for tile in self.tile_sprite_group:
            if tile.rect.colliderect(self.rect):
                if self.rect.right < tile.rect.centerx:
                    self.rect.right = tile.rect.left
                elif self.rect.left > tile.rect.centerx:
                    self.rect.left = tile.rect.right
                if self.rect.top >= tile.rect.centery:
                    self.rect.top = tile.rect.bottom
                else:
                    self.rect.bottom = tile.rect.top

    def do_enemy_rotate(self):

        self.check_collison()

    def update(self):
        self.do_enemy_rotate()
