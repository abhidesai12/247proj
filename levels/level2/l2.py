# l2.py

from math import pi as PI
from os import path as ospath
from random import choice as rand_choice
from random import randint as rnd_int
from random import randrange as rnd_range
from random import uniform as rnd_uniform
from sys import exit as terminate
from time import sleep as slumber

import pygame as pyg

pyg.font.init()
pyg.init()
Vector2 = pyg.math.Vector2

# Color Constants
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_DARK_GREY = (40, 40, 40)
COLOR_LIGHT_GREY = (100, 100, 100)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)

# Game Settings
GAME_TITLE = "Cardinal Conquest"
SCREEN_WIDTH = 800
SCREEN_HEIGHT = SCREEN_WIDTH // 4 * 3
SCREEN_DIMENSIONS = (SCREEN_WIDTH, SCREEN_HEIGHT)
FRAMES_PER_SEC = 60
TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Player Properties
PLAYER_HEALTH = 150
PLAYER_VELOCITY = 150
PLAYER_IMAGE = "main_player.png"
PLAYER_ROTATION_VELOCITY = PI
PLAYER_HIT_RECTANGLE = pyg.Rect(0, 0, 32, 32)
ENEMIES_DEFEATED = 0

# Weapon Properties
PROJECTILE_OFFSET = Vector2(20, 10)
PROJECTILE_IMAGE = "bullet.png"
PROJECTILE_VELOCITY = 300
PROJECTILE_RANGE = 1000
PROJECTILE_FREQUENCY = 200
PROJECTILE_KNOCKBACK = 20
WEAPON_SPREAD = 5
PROJECTILE_IMPACT = 20

# Enemy Properties
ENEMY_IMAGE1 = "mob1.png"
ENEMY_IMAGE2 = "mob2.png"
ENEMY_IMAGE3 = "mob3.png"
ENEMY_HEALTH1 = 100
ENEMY_HEALTH2 = 50
ENEMY_HEALTH3 = 200
ENEMY_DETECTION_RANGE = 400
ENEMY_VELOCITIES = [50, 75, 25]
ENEMY_SCALE = 2.25
ENEMY_HIT_RECTANGLE = pyg.Rect(0, 0, 30, 30)
ENEMY_IMPACT = 10
ENEMY_KNOCKBACK = 20
ENEMY_AVOIDANCE_RADIUS = 50

# Font
UI_FONT = pyg.font.SysFont(None, 25)
UI_FONT_LARGE = pyg.font.SysFont(None, 60)

# Images
FLOOR_IMAGE = pyg.image.load("levels/level2/img/floor.png")
FLOOR_IMAGE2 = pyg.image.load("levels/level2/img/floor.png")
BACKGROUND_IMAGE = pyg.image.load("levels/level2/img/back.jpg")

from g import game_state


def interpolate_color(window, hue=(0, 0, 0)):
    overlay = pyg.Surface(window.get_size())
    overlay.fill(hue)
    for transparency in range(0, 255, 5):
        overlay.set_alpha(transparency)
        window.blit(overlay, (0, 0))
        pyg.display.update()
        pyg.time.delay(10)


def fade_in(window, hue=(0, 0, 0)):
    interpolate_color(window, hue)


def fade_out(window, hue=(0, 0, 0)):
    interpolate_color(window, hue)


class GameInstance:
    def __init__(self):
        self.screen = pyg.display.set_mode(SCREEN_DIMENSIONS)
        pyg.display.set_caption(GAME_TITLE)
        self.clock = pyg.time.Clock()
        pyg.key.set_repeat(30, 30)
        self.preload_assets()
        self.mob_spawn_interval = 3000
        self.prev_mob_spawn_time = pyg.time.get_ticks()
        self.level_start_time = pyg.time.get_ticks()

    def preload_assets(self):
        game_dir = ospath.dirname(__file__)
        img_dir = ospath.join(game_dir, "img")
        sound_dir = ospath.join(ospath.dirname(game_dir), "sound")
        self.level_map = LevelMap(ospath.join(game_dir, "map_small.txt"))
        self.player_walk1_img = pyg.image.load(ospath.join(img_dir, "walk1.png")).convert_alpha()
        self.player_walk2_img = pyg.image.load(ospath.join(img_dir, "walk2.png")).convert_alpha()
        self.projectile_img = pyg.image.load(ospath.join(img_dir, PROJECTILE_IMAGE)).convert_alpha()
        self.Enemy_img = pyg.image.load(ospath.join(img_dir, ENEMY_IMAGE1)).convert_alpha()
        self.enemy2_img = pyg.image.load(ospath.join(img_dir, ENEMY_IMAGE2)).convert_alpha()
        self.enemy3_img = pyg.image.load(ospath.join(img_dir, ENEMY_IMAGE3)).convert_alpha()
        self.health_img = pyg.image.load(ospath.join(img_dir, "heart.png")).convert_alpha()
        self.health_img = pyg.transform.scale(self.health_img, (30, 30))
        self.paused_overlay = pyg.Surface(self.screen.get_size()).convert_alpha()
        self.paused_overlay.fill((0, 0, 0, 180))
        self.impact_sound = pyg.mixer.Sound("sound/hit.mp3")
        self.gameover_sound = pyg.mixer.Sound("sound/end.mp3")
        self.kill_sound = pyg.mixer.Sound("sound/destroy.wav")

    def initialize(self):
        self.all_entities = pyg.sprite.Group()
        self.obstacles = pyg.sprite.Group()
        self.enemies = pyg.sprite.Group()
        self.projectiles = pyg.sprite.Group()
        self.player = Player(self, 3, 3)
        self.player.enemies_defeated = 0
        self.player_lives = 3
        for y, row in enumerate(self.level_map.map_data):
            for x, cell in enumerate(row):
                self.map_y = y
                self.map_x = x
                if cell == "1":
                    Obstacle(self, x, y)
                if cell == "2":
                    Obstacle2(self, x, y)
                if cell == "M":
                    Enemy(self, x, y)
                if cell == "H":
                    Enemy2(self, x, y)
                if cell == "T":
                    Enemy3(self, x, y)
        self.camera = LevelCamera(self.level_map.width, self.level_map.height)
        self.paused = False

    def execute(self):
        self.running = True
        while self.running:
            self.dt = self.clock.tick(FRAMES_PER_SEC) / 1000
            self.handle_events()
            if not self.paused:
                self.update()
            self.render()

    def terminate(self):
        pyg.quit()
        terminate()

    def update(self):
        self.all_entities.update()
        self.camera.update(self.player)
        collisions = pyg.sprite.spritecollide(self.player, self.enemies, False, collide_hit_rect)
        if collisions:
            self.player_lives -= 1
            self.impact_sound.play()
            if self.player_lives <= 0:
                self.display_gameover()
                game_state["current_level"] = "level_2"
                self.running = False
                return
            self.player.pos = Vector2(3, 3) * TILE_SIZE
            self.player.health = PLAYER_HEALTH
        impacts = pyg.sprite.groupcollide(self.enemies, self.projectiles, False, True)
        for enemy in impacts:
            enemy.health = 0
            enemy.vel = Vector2(0, 0)
            self.kill_sound.play()
            self.player.enemies_defeated += 1
        current_time = pyg.time.get_ticks()
        if current_time - self.level_start_time > 300000:
            self.mob_spawn_interval = 200
        elif current_time - self.prev_mob_spawn_time > self.mob_spawn_interval:
            self.spawn_enemy()
            self.prev_mob_spawn_time = current_time
            self.mob_spawn_interval = max(2000, self.mob_spawn_interval - 50)
        if self.player.enemies_defeated >= 25:
            game_state["current_level"] = "level_3"
            self.running = False

    def render(self):
        self.screen.blit(BACKGROUND_IMAGE, (0, 0))
        for entity in self.all_entities:
            if isinstance(entity, Enemy):
                render_health_bar(entity)
            self.screen.blit(entity.image, self.camera.apply(entity))
        enemy_count_text = UI_FONT.render("Librarians killed: " + str(self.player.enemies_defeated), True, COLOR_RED)
        self.screen.blit(enemy_count_text, (10, 30))
        for i in range(self.player_lives):
            self.screen.blit(self.health_img, (10 + i * 40, 50))
        if self.paused:
            self.screen.blit(self.paused_overlay, (0, 0))
            pause_text = UI_FONT_LARGE.render("PAUSED!", True, COLOR_GREEN)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 20))
        pyg.display.flip()

    def handle_events(self):
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                self.terminate()
            if event.type == pyg.KEYDOWN:
                if event.key == pyg.K_ESCAPE:
                    self.terminate()
                if event.key == pyg.K_p:
                    self.paused = not self.paused

    def display_gameover(self):
        fade_in(self.screen)
        game_over_font = pyg.font.Font(None, 74)
        game_over_text = game_over_font.render("You Died", True, (255, 0, 0))
        score_text = game_over_font.render(f"Score: {self.player.enemies_defeated}", True, COLOR_WHITE)
        replay_text = game_over_font.render("Replay Game", True, COLOR_WHITE)
        replay_rect = replay_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        while True:
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    pyg.quit()
                    terminate()
                elif event.type == pyg.MOUSEBUTTONDOWN:
                    if replay_rect.collidepoint(event.pos):
                        return
            self.screen.fill(COLOR_BLACK)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() - 75 // 2))
            self.screen.blit(replay_text, replay_rect.topleft)
            pyg.display.flip()

    def display_start_screen(self):
        pass

    def display_end_screen(self):
        pass

    def spawn_enemy(self):
        enemy_type = rand_choice(["M", "H", "T"])
        if enemy_type == "M":
            Enemy(self, rnd_int(0, self.map_x), rnd_int(0, self.map_y))
        elif enemy_type == "H":
            Enemy2(self, rnd_int(0, self.map_x), rnd_int(0, self.map_y))
        elif enemy_type == "T":
            Enemy3(self, rnd_int(0, self.map_x), rnd_int(0, self.map_y))


def run_level2():
    game = GameInstance()
    game.display_start_screen()
    while True:
        game.initialize()
        game.execute()
        if game_state["current_level"] == "level_3":
            break
        game.display_end_screen()


def sprite_collision(sprite, group, direction):
    if direction == "x":
        collisions = pyg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if collisions:
            if collisions[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = collisions[0].rect.left - sprite.hit_rect.width / 2
            if collisions[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = collisions[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if direction == "y":
        collisions = pyg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if collisions:
            if collisions[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = collisions[0].rect.top - sprite.hit_rect.height / 2
            if collisions[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = collisions[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pyg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_entities
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walk1_img = game.player_walk1_img
        self.walk2_img = game.player_walk2_img
        self.image = self.walk1_img
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)
        self.hit_rect = PLAYER_HIT_RECTANGLE.copy()
        self.hit_rect.center = self.rect.center
        self.vel = Vector2(0, 0)
        self.pos = Vector2(x, y) * TILE_SIZE
        self.last_shot_time = 0
        self.health = PLAYER_HEALTH
        self.enemies_defeated = 0
        self.shoot_cooldown = 500
        self.last_update_time = 0
        self.current_frame = 0

    def get_keys(self):
        self.vel = Vector2(0, 0)
        keys = pyg.key.get_pressed()
        if keys[pyg.K_a]:
            self.vel.x = -PLAYER_VELOCITY
        if keys[pyg.K_d]:
            self.vel.x = PLAYER_VELOCITY
        if keys[pyg.K_w]:
            self.vel.y = -PLAYER_VELOCITY
        if keys[pyg.K_s]:
            self.vel.y = PLAYER_VELOCITY
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def get_mouse(self):
        mouse_state = pyg.mouse.get_pressed()
        if mouse_state[0]:
            current_time = pyg.time.get_ticks()
            if current_time - self.last_shot_time > self.shoot_cooldown:
                self.last_shot_time = current_time
                mouse_pos = pyg.mouse.get_pos()
                mouse_pos = Vector2(mouse_pos) + self.game.camera.camera.topleft
                direction = (mouse_pos - self.pos).normalize()
                Projectile(self.game, self.pos, direction)

    def update(self):
        self.get_keys()
        self.get_mouse()
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        sprite_collision(self, self.game.obstacles, "x")
        self.hit_rect.centery = self.pos.y
        sprite_collision(self, self.game.obstacles, "y")
        self.rect.center = self.hit_rect.center
        now = pyg.time.get_ticks()
        if now - self.last_update_time > 200:
            self.last_update_time = now
            self.current_frame = (self.current_frame + 1) % 2
            if self.current_frame == 0:
                self.image = self.walk1_img
            else:
                self.image = self.walk2_img
            if self.vel.x < 0:
                self.image = pyg.transform.flip(self.image, True, False)
            elif self.vel.x > 0:
                self.image = self.image
            self.rect = self.image.get_rect()
            self.rect.center = self.hit_rect.center


def avoid_enemies(sprite):
    for enemy in sprite.game.enemies:
        if enemy != sprite:
            dist = sprite.pos - enemy.pos
            if 0 < dist.length() < ENEMY_AVOIDANCE_RADIUS:
                sprite.acc += dist.normalize()


def render_health_bar(sprite):
    if sprite.health > 0.6 * sprite.max_health:
        hue = COLOR_GREEN
    elif sprite.health > 0.3 * sprite.max_health:
        hue = COLOR_YELLOW
    else:
        hue = COLOR_RED
    width = int(sprite.rect.width * sprite.health / sprite.max_health)
    sprite.health_bar = pyg.Rect(0, 0, width, 7)
    if sprite.health < sprite.max_health:
        pyg.draw.rect(sprite.image, hue, sprite.health_bar)


class Enemy(pyg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_entities, game.enemies
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.Enemy_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)

    def get_mouse(self):
        mouse_state = pyg.mouse.get_pressed()
        if mouse_state[0]:
            current_time = pyg.time.get_ticks()
            if current_time - self.last_shot_time > self.shoot_cooldown:
                self.last_shot_time = current_time
                mouse_pos = pyg.mouse.get_pos()
                mouse_pos = Vector2(mouse_pos) + self.game.camera.camera.topleft
                direction = (mouse_pos - self.pos).normalize()
                Projectile(self.game, self.pos, direction)

    def update(self):
        self.get_keys()
        self.get_mouse()
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        sprite_collision(self, self.game.obstacles, "x")
        self.hit_rect.centery = self.pos.y
        sprite_collision(self, self.game.obstacles, "y")
        self.rect.center = self.hit_rect.center
        now = pyg.time.get_ticks()
        if now - self.last_update_time > 200:
            self.last_update_time = now
            self.current_frame = (self.current_frame + 1) % 2
            if self.current_frame == 0:
                self.image = self.walk1_img
            else:
                self.image = self.walk2_img
            if self.vel.x < 0:
                self.image = pyg.transform.flip(self.image, True, False)
            elif self.vel.x > 0:
                self.image = self.image
            self.rect = self.image.get_rect()
            self.rect.center = self.hit_rect.center


def avoid_enemies(sprite):
    for enemy in sprite.game.enemies:
        if enemy != sprite:
            dist = sprite.pos - enemy.pos
            if 0 < dist.length() < ENEMY_AVOIDANCE_RADIUS:
                sprite.acc += dist.normalize()


def render_health_bar(sprite):
    if sprite.health > 0.6 * sprite.max_health:
        hue = COLOR_GREEN
    elif sprite.health > 0.3 * sprite.max_health:
        hue = COLOR_YELLOW
    else:
        hue = COLOR_RED
    width = int(sprite.rect.width * sprite.health / sprite.max_health)
    sprite.health_bar = pyg.Rect(0, 0, width, 7)
    if sprite.health < sprite.max_health:
        pyg.draw.rect(sprite.image, hue, sprite.health_bar)


class Enemy(pyg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_entities, game.enemies
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.Enemy_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)
        self.hit_rect = ENEMY_HIT_RECTANGLE.copy()
        self.hit_rect.center = self.rect.center
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.pos = Vector2(x, y) * TILE_SIZE
        self.rect.center = self.pos
        self.rot = 0
        self.max_health = ENEMY_HEALTH1
        self.health = self.max_health
        self.speed = rand_choice(ENEMY_VELOCITIES)
        self.target = game.player

    def update(self):
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < ENEMY_DETECTION_RANGE**2:
            self.rot = target_dist.angle_to(Vector2(1, 0))
            self.image = pyg.transform.rotate(self.game.Enemy_img, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = Vector2(1, 0).rotate(-self.rot)
            avoid_enemies(self)
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt**2
            self.rect.center = self.pos
        render_health_bar(self)
        if self.health <= 0:
            self.kill()


class Enemy2(pyg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_entities, game.enemies
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.enemy2_img
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)
        self.hit_rect = ENEMY_HIT_RECTANGLE.copy()
        self.hit_rect.center = self.rect.center
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.pos = Vector2(x, y) * TILE_SIZE
        self.rect.center = self.pos
        self.rot = 0
        self.max_health = ENEMY_HEALTH2
        self.health = self.max_health
        self.speed = rand_choice(ENEMY_VELOCITIES)

    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(Vector2(1, 0))
        self.image = pyg.transform.rotate(self.game.enemy2_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = Vector2(1, 0).rotate(-self.rot)
        avoid_enemies(self)
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt**2
        self.rect.center = self.pos
        render_health_bar(self)
        if self.health <= 0:
            self.kill()


class Enemy3(pyg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_entities, game.enemies
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.enemy3_img
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)
        self.hit_rect = ENEMY_HIT_RECTANGLE.copy()
        self.hit_rect.center = self.rect.center
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.pos = Vector2(x, y) * TILE_SIZE
        self.rect.center = self.pos
        self.rot = 0
        self.max_health = ENEMY_HEALTH3
        self.health = self.max_health
        self.speed = rand_choice(ENEMY_VELOCITIES)

    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(Vector2(1, 0))
        self.image = pyg.transform.rotate(self.game.enemy3_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = Vector2(1, 0).rotate(-self.rot)
        avoid_enemies(self)
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt**2
        self.rect.center = self.pos
        render_health_bar(self)
        if self.health <= 0:
            self.kill()


class Projectile(pyg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self.groups = game.all_entities, game.projectiles
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.projectile_img
        self.rect = self.image.get_rect()
        self.pos = Vector2(pos)
        self.rect.center = self.pos
        self.vel = direction.normalize() * PROJECTILE_VELOCITY
        self.spawn_time = pyg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pyg.time.get_ticks() - self.spawn_time > PROJECTILE_RANGE:
            self.kill()


class Obstacle(pyg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_entities, game.obstacles
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pyg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.blit(FLOOR_IMAGE, (0, 0))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE


class Obstacle2(pyg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_entities, game.obstacles
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pyg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.blit(FLOOR_IMAGE2, (0, 0))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE


def collide_hit_rect(sprite_a, sprite_b):
    return sprite_a.hit_rect.colliderect(sprite_b.rect)


class LevelMap:
    def __init__(self, file_path):
        self.map_data = []
        with open(file_path, "rt") as map_file:
            for row in map_file:
                self.map_data.append(row.strip())
        self.tile_width = len(self.map_data[0])
        self.tile_height = len(self.map_data)
        self.width = self.tile_width * TILE_SIZE
        self.height = self.tile_height * TILE_SIZE


class LevelCamera:
    def __init__(self, map_width, map_height):
        self.camera = pyg.Rect(0, 0, map_width, map_height)
        self.map_width = map_width
        self.map_height = map_height

    def apply(self, target):
        return target.rect.move(self.camera.topleft)

    def update(self, target):
        left = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        top = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        left = min(0, left)
        top = min(0, top)
        left = max(-(self.map_width - SCREEN_WIDTH), left)
        top = max(-(self.map_height - SCREEN_HEIGHT), top)
        self.camera = pyg.Rect(left, top, self.map_width, self.map_height)


def render_player_health(surface, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_WIDTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_WIDTH
    outline_rect = pyg.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    fill_rect = pyg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        color = COLOR_GREEN
    elif pct > 0.3:
        color = COLOR_YELLOW
    else:
        color = COLOR_RED
    pyg.draw.rect(surface, color, fill_rect)
    pyg.draw.rect(surface, COLOR_WHITE, outline_rect, 2)
