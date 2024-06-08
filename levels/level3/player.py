import pygame

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

        # Assign sprites on init
        self.walk1_img = pygame.image.load("./images/walk1.png")
        self.walk2_img = pygame.image.load("./images/walk2.png")
        self.sprite = self.walk1_img
        self.last_update = 0
        self.current_frame = 0
        self.facing_left = False

    def move(self, keys):
        moving = False
        if keys[pygame.K_a] and self.x > self.field_x + self.width:
            self.x -= self.vel
            self.facing_left = True
            moving = True
        elif keys[pygame.K_d] and self.x < self.field_x + self.field_width - self.width:
            self.x += self.vel
            self.facing_left = False
            moving = True
        elif keys[pygame.K_s] and self.y < self.field_y + self.field_height - self.height:
            self.y += self.vel
            moving = True
        elif keys[pygame.K_w] and self.y > self.field_y + self.height:
            self.y -= self.vel
            moving = True

        # Animate the player
        if moving:
            now = pygame.time.get_ticks()
            if now - self.last_update > 200:  # Change frame every 200 ms
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % 2
                if self.current_frame == 0:
                    self.sprite = self.walk1_img
                else:
                    self.sprite = self.walk2_img

            if self.facing_left:  # Moving left
                self.sprite = pygame.transform.flip(self.sprite, True, False)

    def draw(self, screen):
        # Draw the sprite
        return screen.blit(self.sprite, (self.x, self.y))

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
