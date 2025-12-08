import pygame
import random
import math
import os
import sys
import cv2
import numpy as np

PLAYER_SPEED = 6
ANIMAL_COLLIDE_RADIUS = 40
ESSENTIAL_COLLIDE_RADIUS = 40
DROPLET_COLLIDE_RADIUS = 20
FALL_SPEED_CHOICES = [2, 3, 4, 5, 6, 7, 8]


def load_image(name):
    path = os.path.join(os.path.dirname(__file__), name)
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        print("IMAGE NOT FOUND:", name)
        sys.exit()


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def fit(img, maxw, maxh):
    w, h = img.get_size()
    sc = min(maxw / w, maxh / h, 1)
    return pygame.transform.smoothscale(img, (int(w * sc), int(h * sc)))


# ---------------- PLAYER ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self, img_r, img_l, x, y):
        super().__init__()
        self.img_right = img_r
        self.img_left = img_l
        self.image = self.img_right
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.center)

    @property
    def center(self):
        return (self.rect.centerx, self.rect.centery)


# ---------------- FALLING OBJECT ----------------
class FallingObject(pygame.sprite.Sprite):
    def __init__(self, img, kind, area):
        super().__init__()
        self.image = img
        self.kind = kind
        self.area = area
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        ax, ay, aw, ah = self.area
        self.rect.x = random.randint(ax + 50, ax + aw - 50)
        self.rect.y = random.randint(ay - ah // 2, ay - 20)
        self.speed = random.choice(FALL_SPEED_CHOICES)

    def update(self):
        self.rect.y += self.speed
        _, ay, _, ah = self.area
        if self.rect.top > ay + ah:
            self.reset_position()


class Level1:
    def __init__(self, x, y, w, h):
        """Embed game into a region (x,y,w,h)"""
        self.x, self.y, self.w, self.h = x, y, w, h
        self.surface = pygame.Surface((w, h))

        # Load assets
        self.bg = pygame.transform.smoothscale(load_image("forest.png"), (w, h))
        self.man_r = fit(load_image("man_right(1).png"), 100, 120)
        self.man_l = fit(load_image("man_left(1).png"), 100, 120)
        self.dino_img = fit(load_image("dino.png"), 80, 80)
        self.egg_img = fit(load_image("egg.png"), 60, 60)

        # Player
        self.player = Player(self.man_r, self.man_l, w // 2, h - 120)
        self.player_group = pygame.sprite.GroupSingle(self.player)

        # Game area rect
        self.area = pygame.Rect(0, 0, w, h)

        # Falling Objects
        self.animals = pygame.sprite.Group(
            FallingObject(self.dino_img, "dino", self.area) for _ in range(10)
        )
        self.eggs = pygame.sprite.Group(
            FallingObject(self.egg_img, "egg", self.area) for _ in range(10)
        )
        self.droplet = pygame.sprite.GroupSingle(
            FallingObject(self.egg_img, "egg_life", self.area)
        )

        # Score
        self.egg_caught = 0
        self.dino_hits = 0
        self.score = 0

        # Game Result Flags
        self.game_over = False
        self.win = False

        self.font = pygame.font.SysFont("Arial", 24)

    # ----------- Movement Input Triggered by Main.py -----------
    def receive_wand_input(self, direction):
        if self.game_over:
            return

        if direction == "LEFT":
            self.player.image = self.player.img_left
            self.player.pos.x -= PLAYER_SPEED

        elif direction == "RIGHT":
            self.player.image = self.player.img_right
            self.player.pos.x += PLAYER_SPEED

        # Clamp within game area
        self.player.pos.x = max(50, min(self.w - 50, self.player.pos.x))
        self.player.rect.centerx = int(self.player.pos.x)

    # ----------- UPDATE GAME STATE -----------
    def update(self):
        if self.game_over:
            return

        self.animals.update()
        self.eggs.update()
        self.droplet.update()

        # Collisions
        for a in self.animals:
            if dist(a.rect.center, self.player.center) < ANIMAL_COLLIDE_RADIUS:
                a.reset_position()
                self.dino_hits += 1
                self.score -= 10

                if self.dino_hits >= 3:
                    self.win = False
                    self.game_over = True

        for e in self.eggs:
            if dist(e.rect.center, self.player.center) < ESSENTIAL_COLLIDE_RADIUS:
                e.reset_position()
                self.egg_caught += 1
                self.score += 10

                if self.egg_caught >= 5:
                    self.win = True
                    self.game_over = True

    def draw(self, screen):
        self.update()
        self.surface.blit(self.bg, (0, 0))
        self.animals.draw(self.surface)
        self.eggs.draw(self.surface)
        self.droplet.draw(self.surface)
        self.player_group.draw(self.surface)

        # HUD
        hud = self.font.render(
            f"Eggs: {self.egg_caught}/5    Dino: {self.dino_hits}/3    Score: {self.score}",
            True, (0, 0, 0)
        )
        self.surface.blit(hud, (10, 10))

        # ----------- END SCREEN -----------  
        if self.game_over:
            self.surface.fill((255, 255, 255))

            big_font = pygame.font.SysFont("Arial", 70)
            med_font = pygame.font.SysFont("Arial", 36)

            if self.win:
                msg = "YOU WIN!"
                color = (0, 180, 0)
            else:
                msg = "GAME OVER"
                color = (200, 0, 0)

            msg_surf = big_font.render(msg, True, color)
            score_surf = med_font.render(f"Score: {self.score}", True, (0, 0, 0))
            prompt = med_font.render("Press SPACE to continue", True, (70, 70, 70))

            self.surface.blit(msg_surf, (self.w//2 - msg_surf.get_width()//2, self.h//2 - 120))
            self.surface.blit(score_surf, (self.w//2 - score_surf.get_width()//2, self.h//2 - 40))
            self.surface.blit(prompt, (self.w//2 - prompt.get_width()//2, self.h//2 + 40))

        screen.blit(self.surface, (self.x, self.y))

    def is_finished(self):
        """Main.py will use this"""
        return self.game_over
