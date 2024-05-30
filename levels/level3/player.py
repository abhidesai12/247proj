import pygame
import math


class Player:
    def __init__(
        self,
        x,
        y,
        field_x,
        field_y,
        field_width,
        field_height,
        width=50,
        height=50,
        vel=5,
        color=(0, 255, 0),
        deaths=0,
    ):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = vel
        self.color = color
        self.deaths = deaths
        self.field_x = field_x
        self.field_y = field_y
        self.field_width = field_width
        self.field_height = field_height

        # Assign a sprite on init
        self.sprite = pygame.image.load("./levels/level3/player.png")
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.field_x + self.width:
            self.x -= self.vel
        if keys[pygame.K_RIGHT] and self.x < self.field_x + self.field_width - self.width:
            self.x += self.vel
        if keys[pygame.K_DOWN] and self.y < self.field_y + self.field_height - self.height:
            self.y += self.vel
        if keys[pygame.K_UP] and self.y > self.field_y + self.height:
            self.y -= self.vel

    def draw(self, screen):
        # Draw the sprite
        return screen.blit(self.sprite, (self.x, self.y))

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
