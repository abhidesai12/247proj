import pygame
import random


class Enemy:
    def __init__(
        self,
        path,
        width=20,
        height=20,
        vel=5,
        color=(255, 165, 0),
        field_x=0,
        field_y=0,
    ):
        self.path = path
        self.width = width
        self.height = height
        self.vel = vel
        self.color = color
        self.field_x = field_x
        self.field_y = field_y
        self.current_point = 0
        self.x, self.y = self.path[self.current_point]

        # Assign a sprite on init
        sprite_path = random.choice(["./levels/level3/enemy1.png", "./levels/level3/enemy2.png"])
        self.sprite = pygame.image.load(sprite_path)
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))

    def draw(self, screen):
        # Draw the border
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (
                self.x - 1 + self.field_x,
                self.y - 1 + self.field_y,
                self.width + 2,
                self.height + 2,
            ),
        )

        # Draw the sprite
        return screen.blit(self.sprite, (self.x + self.field_x, self.y + self.field_y))

    def move(self):
        if self.current_point < len(self.path) - 1:
            target_x, target_y = self.path[self.current_point + 1]
        else:
            target_x, target_y = self.path[0]

        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx**2 + dy**2) ** 0.5

        if dist < self.vel:
            self.x, self.y = target_x, target_y
            self.current_point = (self.current_point + 1) % len(self.path)
        else:
            self.x += self.vel * dx / dist
            self.y += self.vel * dy / dist
