import pygame as pg
import math
from random import uniform, choice
from .settings import *
from .tmap import collide_hit_rect

vec = pg.math.Vector2


def sprite_collision(sprite, group, dir):
    if dir == "x":
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == "y":
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walk1_img = game.walk1_img
        self.walk2_img = game.walk2_img
        self.image = self.walk1_img
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = vec(x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.last_shot = 0
        self.hp = PLAYER_HP
        self.librarians_killed = 0
        self.shoot_cooldown = 500
        self.last_update = 0
        self.current_frame = 0

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.85

    def get_mouse(self):
        mouse_pressed = pg.mouse.get_pressed()
        if mouse_pressed[0]:
            now = pg.time.get_ticks()
            if now - self.last_shot > self.shoot_cooldown:
                self.last_shot = now
                mouse_pos = pg.mouse.get_pos()
                mouse_pos = vec(mouse_pos) + self.game.camera.camera.topleft
                direction = vec(mouse_pos[0] - self.pos.x, mouse_pos[1] - self.pos.y).normalize()
                Bullet(self.game, self.pos, direction)

    def update(self):
        self.get_keys()
        self.get_mouse()
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        sprite_collision(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        sprite_collision(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center

        now = pg.time.get_ticks()
        if now - self.last_update > 200:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % 2
            if self.current_frame == 0:
                self.image = self.walk1_img
            else:
                self.image = self.walk2_img

            if self.vel.x < 0:
                self.image = pg.transform.flip(self.image, True, False)
            elif self.vel.x > 0:
                self.image = self.image
            self.rect = self.image.get_rect()
            self.rect.center = self.hit_rect.center


def avoid_mobs(sprite):
    for mob in sprite.game.mobs:
        if mob != sprite:
            distance = sprite.pos - mob.pos
            if 0 < distance.length() < AVOID_RADIUS:
                sprite.acc += distance.normalize()


def draw_hp(sprite):
    if sprite.hp > 0.60 * sprite.mob_hp:
        color = GREEN
    elif sprite.hp > 0.30 * sprite.mob_hp:
        color = YELLOW
    else:
        color = RED
    width = int(sprite.rect.width * sprite.hp / sprite.mob_hp)
    sprite.hp_bar = pg.Rect(0, 0, width, 7)
    if sprite.hp < sprite.mob_hp:
        pg.draw.rect(sprite.image, color, sprite.hp_bar)


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = vec(x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rect.center = self.pos
        self.rot = 0
        self.mob_hp = MOB_HP
        self.hp = self.mob_hp
        self.speed = choice(MOB_SPEEDS)
        self.target = game.player

    def update(self):
        """Updates the position etc for the loop."""
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < MOB_DETECT**2:
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.game.mob_img, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            avoid_mobs(self)
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt**2
            self.rect.center = self.pos
        draw_hp(self)
        if self.hp <= 0:
            self.kill()
            # self.game.player.librarians_killed += 1


class Mob2(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob2_img
        self.rect = self.image.get_rect()
        self.rect.center = vec(x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rect.center = self.pos
        self.rot = 0
        self.mob_hp = MOB_HP2
        self.hp = self.mob_hp
        self.speed = choice(MOB_SPEEDS)

    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob2_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        avoid_mobs(self)
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt**2
        self.rect.center = self.pos
        draw_hp(self)
        if self.hp <= 0:
            self.kill()
            # self.game.player.librarians_killed += 1


class Mob3(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob3_img
        self.rect = self.image.get_rect()
        self.rect.center = vec(x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rect.center = self.pos
        self.rot = 0
        self.mob_hp = MOB_HP3
        self.hp = self.mob_hp
        self.speed = choice(MOB_SPEEDS)

    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob3_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        avoid_mobs(self)
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt**2
        self.rect.center = self.pos
        draw_hp(self)
        if self.hp <= 0:
            self.kill()
            # self.game.player.librarians_killed += 1


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.rect = self.image.get_rect()
        self.pos = vec(pos)  # Ensure pos is a Vector2
        self.rect.center = self.pos
        self.vel = direction.normalize() * BULLET_SPEED  # Normalize direction
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.time.get_ticks() - self.spawn_time > BULLET_TRAVEL:
            self.kill()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.blit(BG, (0, 0))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Wall2(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.blit(BG2, (0, 0))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
