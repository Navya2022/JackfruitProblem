import pygame
import cv2
import numpy as np
import sys

from object_detection import detect_wand
import level1
import level3
import level2
import training
import signup
import intro

pygame.init()

SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Wand Controller")

FPS = 60
FONT = pygame.font.SysFont("Arial", 26)

# ---- CAMERA WINDOW SIZE ----
CAM_W, CAM_H = 420, 320
cam_x, cam_y = 20, SCREEN_H - CAM_H - 20

# ---- GAME WINDOW POSITION ----
GAME_W, GAME_H = 820, 620
GAME_X, GAME_Y = SCREEN_W - GAME_W - 20, 20

# Raw camera dimensions
frame_w = 640
frame_h = 480

# Neutral zone
NEUTRAL_W = 80
NEUTRAL_H = 80

neutral_left   = (frame_w // 2) - (NEUTRAL_W // 2)
neutral_right  = (frame_w // 2) + (NEUTRAL_W // 2)
neutral_top    = (frame_h // 2) - (NEUTRAL_H // 2)
neutral_bottom = (frame_h // 2) + (NEUTRAL_H // 2)

wand_x, wand_y = None, None


def draw_camera(frame):
    cam_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    surf = pygame.surfarray.make_surface(np.rot90(cam_rgb))

    screen.blit(pygame.transform.scale(surf, (CAM_W, CAM_H)), (cam_x, cam_y))

    pygame.draw.rect(screen, (255, 255, 255), (cam_x-2, cam_y-2, CAM_W+4, CAM_H+4), 2)

    pygame.draw.rect(
        screen, (0, 200, 255),
        (
            cam_x + (neutral_left * CAM_W // frame_w),
            cam_y + (neutral_top * CAM_H // frame_h),
            NEUTRAL_W * CAM_W // frame_w,
            NEUTRAL_H * CAM_H // frame_h
        ),
        3
    )

    if wand_x is not None:
        draw_x = cam_x + int(wand_x * CAM_W / frame_w)
        draw_y = cam_y + int(wand_y * CAM_H / frame_h)
        pygame.draw.circle(screen, (255, 255, 0), (draw_x, draw_y), 10)


def detect_dir_level1(x, y):
    if x is None:
        return None
    if x < neutral_left:
        return "LEFT"
    if x > neutral_right:
        return "RIGHT"
    return None


def detect_dir_level3(x, y):
    if x is None:
        return None
    if x < neutral_left:
        return "LEFT"
    if x > neutral_right:
        return "RIGHT"
    if y < neutral_top:
        return "UP"
    if y > neutral_bottom:
        return "DOWN"
    return None

def run_level1():
    global wand_x, wand_y
    clock = pygame.time.Clock()
    game = level1.Level1(GAME_X, GAME_Y, GAME_W, GAME_H)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        x, y, frame = detect_wand()
        wand_x, wand_y = x, y

        direction = detect_dir_level1(x, y)
        if direction:
            game.receive_wand_input(direction)

        screen.fill((30, 30, 30))
        if frame is not None:
            draw_camera(frame)

        game.draw(screen)
        pygame.display.update()

        if game.game_over or game.win:
            pygame.time.delay(1500)
            return



def run_level3():
    global wand_x, wand_y
    clock = pygame.time.Clock()
    print("here")
    game = level3.ShiftingMaze( GAME_X, GAME_Y, GAME_W, GAME_H)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        x, y, frame = detect_wand()
        wand_x, wand_y = x, y

        direction = detect_dir_level3(x, y)
        if direction:
            game.move_player(direction)

        screen.fill((30, 30, 30))
        if frame is not None:
            draw_camera(frame)

        game.draw(screen)
        pygame.display.update()

        if game.win:
            return


def run():
    
    training.start_training()
    run_level1()
    level2.main() 
    run_level3()
if __name__ == "__main__":
    intro.intro_transition(title="",
    subtitle="",
    bg_image_path="backin.png")
    signup.main()