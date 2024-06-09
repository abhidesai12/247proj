import pygame
import sys
from pygame import mixer
import random


pygame.mixer.init()
impact_audio = pygame.mixer.Sound("./sound/hit.mp3")

window_dimensions = (800, 600)
game_window = pygame.display.set_mode(window_dimensions)

game_progress = {"current_level": "level_3"}


def gradually_appear(display, fill_color=(0, 0, 0)):
    emerging_layer = pygame.Surface(display.get_size())
    emerging_layer.fill(fill_color)
    for opacity in range(0, 255, 5):
        emerging_layer.set_alpha(opacity)
        display.blit(emerging_layer, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)


def gradually_disappear(display, fill_color=(0, 0, 0)):
    emerging_layer = pygame.Surface(display.get_size())
    emerging_layer.fill(fill_color)
    for opacity in range(255, -1, -5):
        emerging_layer.set_alpha(opacity)
        display.blit(emerging_layer, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)


def display_victory(display_surface):
    gradually_appear(display_surface)
    victory_font = pygame.font.Font(None, 74)
    victory_text = victory_font.render("Congrats you won!", True, (0, 255, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_area.collidepoint(event.pos):
                    return

        display_surface.fill((0, 0, 0))
        display_surface.blit(victory_text, (display_surface.get_width() // 2 - victory_text.get_width() // 2, display_surface.get_height() // 2 - victory_text.get_height() // 2))
        pygame.display.flip()


def run_level3():
    display_width = window_dimensions[0]
    display_height = window_dimensions[1]

    arena_x = 150
    arena_y = 80
    arena_w = 500
    arena_h = 500

    display_surface = pygame.display.set_mode((display_width, display_height))

    movement_frame1 = pygame.image.load("./images/walk1.png")
    movement_frame2 = pygame.image.load("./images/walk2.png")

    class Avatar:
        def __init__(self, pos_x, pos_y, bounds_x, bounds_y, bounds_w, bounds_h, avatar_w=50, avatar_h=50, speed=5, avatar_color=(0, 255, 0), death_count=0):
            self.initial_x = pos_x
            self.initial_y = pos_y
            self.pos_x = pos_x
            self.pos_y = pos_y
            self.avatar_w = avatar_w
            self.avatar_h = avatar_h
            self.speed = speed
            self.avatar_color = avatar_color
            self.death_count = death_count
            self.bounds_x = bounds_x
            self.bounds_y = bounds_y
            self.bounds_w = bounds_w
            self.bounds_h = bounds_h

            self.movement_frame1 = pygame.transform.scale(movement_frame1, (self.avatar_w, self.avatar_h))
            self.movement_frame2 = pygame.transform.scale(movement_frame2, (self.avatar_w, self.avatar_h))
            self.current_sprite = self.movement_frame1
            self.is_moving = False
            self.movement_counter = 0
            self.facing_left = False

        def handle_movement(self, key_states):
            self.is_moving = False
            if key_states[pygame.K_a] and self.pos_x > self.bounds_x + self.avatar_w:
                self.pos_x -= self.speed
                self.is_moving = True
                self.facing_left = True
            if key_states[pygame.K_d] and self.pos_x < self.bounds_x + self.bounds_w - self.avatar_w:
                self.pos_x += self.speed
                self.is_moving = True
                self.facing_left = False
            if key_states[pygame.K_s] and self.pos_y < self.bounds_y + self.bounds_h - self.avatar_h:
                self.pos_y += self.speed
                self.is_moving = True
            if key_states[pygame.K_w] and self.pos_y > self.bounds_y + self.avatar_h:
                self.pos_y -= self.speed
                self.is_moving = True

        def update_sprite(self):
            if self.is_moving:
                self.movement_counter = (self.movement_counter + 1) % 20
                if self.movement_counter < 10:
                    self.current_sprite = self.movement_frame1
                else:
                    self.current_sprite = self.movement_frame2

                if self.facing_left:
                    self.current_sprite = pygame.transform.flip(self.current_sprite, True, False)
            else:
                self.current_sprite = self.movement_frame1

        def render(self, display_surface):
            self.update_sprite()
            return display_surface.blit(self.current_sprite, (self.pos_x, self.pos_y))

        def respawn(self):
            self.pos_x = self.initial_x
            self.pos_y = self.initial_y

    def execute_level(speed_factor, arena_bg, bg_color, level_music=None):
        if level_music:
            pygame.mixer.music.load(level_music)
            pygame.mixer.music.play(-1)

        level_running = True

        start_area = Zone(arena_x + 235, arena_y + 5, 60, 10)
        end_area = Zone(arena_x + 235, arena_y + arena_h - 50, 60, 10, zone_color=(60, 163, 5))

        avatar = Avatar(
            start_area.x + start_area.width // 2,
            start_area.y + start_area.height // 2,
            arena_x,
            arena_y,
            arena_w,
            arena_h - 10,
        )

        adversaries = [
            Adversary(
                [(200, 210), (300, 260), (250, 260), (250, 310)],
                speed=2 * speed_factor,
                adversary_color=(255, 0, 0),
                bounds_x=arena_x,
                bounds_y=arena_y,
            ),
            Adversary(
                [(200, 210), (200, 360), (350, 360), (350, 210)],
                speed=4 * speed_factor,
                adversary_color=(0, 255, 0),
                bounds_x=arena_x,
                bounds_y=arena_y,
            ),
            Adversary(
                [(250, 260), (250, 460), (450, 460), (450, 260)],
                speed=6 * speed_factor,
                adversary_color=(0, 0, 255),
                bounds_x=arena_x,
                bounds_y=arena_y,
            ),
            Adversary(
                [(300, 300), (300, 500), (550, 500), (550, 300)],
                speed=7 * speed_factor,
                adversary_color=(255, 255, 0),
                bounds_x=arena_x,
                bounds_y=arena_y,
            ),
            Adversary(
                [(350, 160), (350, 460)],
                speed=1 * speed_factor,
                adversary_color=(255, 0, 255),
                bounds_x=arena_x,
                bounds_y=arena_y,
            ),
            Adversary(
                [(450, 160), (450, 460)],
                speed=1 * speed_factor,
                adversary_color=(0, 255, 255),
                bounds_x=arena_x,
                bounds_y=arena_y,
            ),
            Adversary(
                [(arena_x, arena_y + arena_h // 2 + 10), (arena_x + arena_w, arena_y + arena_h // 2 + 10)],
                speed=3 * speed_factor,
                adversary_color=(128, 0, 128),
                bounds_x=arena_x,
                bounds_y=arena_y,
            ),
            Adversary(
                [(arena_x, arena_y + arena_h // 3 + 10), (arena_x + arena_w, arena_y + arena_h // 3 + 10)],
                speed=5 * speed_factor,
                adversary_color=(0, 128, 128),
                bounds_x=arena_x,
                bounds_y=arena_y,
            ),
        ]

        heart_sprite = pygame.image.load("./images/heart.png")
        heart_sprite = pygame.transform.scale(heart_sprite, (30, 30))
        life_count = 3

        message_font = pygame.font.Font("freesansbold.ttf", 18)

        def update_game_state():
            nonlocal life_count
            nonlocal level_running
            key_states = pygame.key.get_pressed()
            avatar.handle_movement(key_states)
            for adversary in adversaries:
                adversary.move()

            if avatar.render(display_surface).collidelist([adversary.render(display_surface) for adversary in adversaries]) != -1:
                impact_audio.play()
                avatar.respawn()
                avatar.death_count += 1
                life_count -= 1
                if life_count <= 0:
                    game_over_screen()
                    game_progress["current_level"] = "level_3"
                    level_running = False
                    return

            if avatar.render(display_surface).collidelist([end_area.render(display_surface)]) != -1:
                level_running = False
                return

        def render_game():
            display_surface.fill(bg_color)
            display_surface.blit(arena_bg, (arena_x, arena_y))
            start_area.render(display_surface)
            end_area.render(display_surface)
            avatar.render(display_surface)
            for adversary in adversaries:
                adversary.render(display_surface)

            death_message = message_font.render("WELCOME UPSTAIRS! YOU'VE DIED " + str(avatar.death_count) + " TIMES." if bg_color == (0, 0, 0) else "YOU'VE DIED " + str(avatar.death_count) + " TIMES. HAHA", True, (255, 255, 255) if bg_color == (0, 0, 0) else (0, 0, 0))
            display_surface.blit(death_message, (225, 50))

            for i in range(life_count):
                display_surface.blit(heart_sprite, (10 + i * 40, 10))

            pygame.display.update()

        def game_over_screen():
            gradually_appear(display_surface)
            game_over_font = pygame.font.Font(None, 74)
            game_over_text = game_over_font.render("You Died", True, (255, 0, 0))
            score_message = game_over_font.render(f"Score: " + str(avatar.death_count), True, (255, 255, 255))
            replay_message = game_over_font.render("Replay Game", True, (255, 255, 255))
            replay_area = replay_message.get_rect(center=(display_width // 2, display_height // 2 + 100))

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if replay_area.collidepoint(event.pos):
                            game_progress["current_level"] = "level_3"
                            run_level3()
                            return

                display_surface.fill((0, 0, 0))
                display_surface.blit(
                    game_over_text,
                    (
                        display_width // 2 - game_over_text.get_width() // 2,
                        display_height // 2 - game_over_text.get_height() - 75 // 2,
                    ),
                )
                display_surface.blit(
                    score_message,
                    (display_width // 2 - score_message.get_width() // 2, display_height // 2),
                )
                display_surface.blit(replay_message, replay_area.topleft)
                pygame.display.flip()

        while level_running:
            pygame.time.delay(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    level_running = False

            update_game_state()
            render_game()

        if level_music:
            pygame.mixer.music.stop()
        return life_count > 0

    arena_bg = pygame.image.load("./images/bg2.png")
    arena_bg = pygame.transform.scale(arena_bg, (arena_w, arena_h))

    updated_arena_bg = pygame.image.load("./images/bg2.png")
    updated_arena_bg = pygame.transform.scale(updated_arena_bg, (arena_w, arena_h))

    if not execute_level(1, arena_bg, (255, 255, 255)):
        return

    gradually_disappear(display_surface)
    gradually_appear(display_surface)

    if not execute_level(2, updated_arena_bg, (0, 0, 0), "sound/dunk.mp3"):
        return

    pygame.mixer.music.load("sound/background.mp3")
    pygame.mixer.music.play(-1)

    game_progress["current_level"] = "final_level"


class Adversary:
    def __init__(
        self,
        path_points,
        adversary_w=35,
        adversary_h=70,
        speed=9,
        adversary_color=(255, 165, 0),
        bounds_x=0,
        bounds_y=0,
    ):
        self.path_points = path_points
        self.adversary_w = adversary_w
        self.adversary_h = adversary_h
        self.speed = speed
        self.adversary_color = adversary_color
        self.bounds_x = bounds_x
        self.bounds_y = bounds_y
        self.current_point_index = 0
        self.pos_x, self.pos_y = self.path_points[self.current_point_index]

        adversary_sprite_path = random.choice(["./images/enemy1-lg.png", "./images/enemy2-lg.png"])
        self.sprite = pygame.image.load(adversary_sprite_path).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.adversary_w, self.adversary_h))

    def render(self, display_surface):
        return display_surface.blit(self.sprite, (self.pos_x, self.pos_y))

    def move(self):
        if self.current_point_index < len(self.path_points) - 1:
            target_x, target_y = self.path_points[self.current_point_index + 1]
        else:
            target_x, target_y = self.path_points[0]
        dx = target_x - self.pos_x
        dy = target_y - self.pos_y
        distance = (dx**2 + dy**2) ** 0.5

        if distance < self.speed:
            self.pos_x, self.pos_y = target_x, target_y
            self.current_point_index = (self.current_point_index + 1) % len(self.path_points)
        else:
            self.pos_x += self.speed * dx / distance
            self.pos_y += self.speed * dy / distance


class Zone:
    def __init__(self, zone_x, zone_y, zone_w, zone_h, zone_color=(0, 0, 0)):
        self.x = zone_x
        self.y = zone_y
        self.width = zone_w
        self.height = zone_h
        self.color = zone_color

    def render(self, display_surface):
        return pygame.draw.rect(display_surface, self.color, (self.x, self.y, self.width, self.height))
