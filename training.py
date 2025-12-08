import pygame
import cv2
import numpy as np
import sys
from collections import deque
from object_detection import detect_wand  

pygame.init()

WIN_W, WIN_H = 1280, 720
win = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Wand Training")

FONT = pygame.font.SysFont("Arial", 32)

trained = {
    "RIGHT": False,
    "LEFT": False,
    "UP": False,
    "DOWN": False,
    "JUMP": False,
    "KILL": False
}

def all_training_done():
    return all(trained.values())

center_x, center_y = WIN_W // 2, WIN_H // 2
NEUTRAL_RADIUS = 60      
MOVE_THRESHOLD = 120    

wand_positions = deque(maxlen=5)  # store last 5 positions


jump_circle = (WIN_W // 3, WIN_H // 3, 50)
kill_circle = (2 * WIN_W // 3, WIN_H // 3, 50)


def point_in_circle(px, py, cx, cy, r):
    return (px - cx)**2 + (py - cy)**2 <= r*r

def check_jump_kill(x, y):
    if x is None or y is None:
        return
    if point_in_circle(x, y, jump_circle[0], jump_circle[1], jump_circle[2]):
        trained["JUMP"] = True
    if point_in_circle(x, y, kill_circle[0], kill_circle[1], kill_circle[2]):
        trained["KILL"] = True

def check_directions():
    if len(wand_positions) < wand_positions.maxlen:
        return  # not enough data yet
    avg_x = sum(p[0] for p in wand_positions) / len(wand_positions)
    avg_y = sum(p[1] for p in wand_positions) / len(wand_positions)

    dx = avg_x - center_x
    dy = avg_y - center_y

    if abs(dx) < NEUTRAL_RADIUS and abs(dy) < NEUTRAL_RADIUS:
        return 


    if dx > MOVE_THRESHOLD:
        trained["RIGHT"] = True
    elif dx < -MOVE_THRESHOLD:
        trained["LEFT"] = True

    if dy > MOVE_THRESHOLD:
        trained["DOWN"] = True
    elif dy < -MOVE_THRESHOLD:
        trained["UP"] = True


def draw_neutral_zone():
    pygame.draw.circle(win, (0, 200, 255), (center_x, center_y), NEUTRAL_RADIUS, 3)
    win.blit(FONT.render("NEUTRAL", True, (255,255,255)), (center_x - 50, center_y - NEUTRAL_RADIUS - 30))

def draw_circles():
    # Jump
    jc_color = (0, 255, 0) if trained["JUMP"] else (150, 150, 150)
    pygame.draw.circle(win, jc_color, (jump_circle[0], jump_circle[1]), jump_circle[2])
    win.blit(FONT.render("JUMP", True, (255,255,255)), (jump_circle[0]-35, jump_circle[1]-70))
    # Kill
    kc_color = (255, 0, 0) if trained["KILL"] else (150, 150, 150)
    pygame.draw.circle(win, kc_color, (kill_circle[0], kill_circle[1]), kill_circle[2])
    win.blit(FONT.render("KILL", True, (255,255,255)), (kill_circle[0]-30, kill_circle[1]-70))

def draw_status():
    y_offset = 10
    for key, val in trained.items():
        color = (0, 255, 0) if val else (255, 50, 50)
        txt = FONT.render(f"{key}: {'✓' if val else '...'}", True, color)
        win.blit(txt, (10, y_offset))
        y_offset += 35

def draw_wand(x, y):
    if x is not None and y is not None:
        pygame.draw.circle(win, (255, 255, 0), (int(x), int(y)), 15)


def start_training():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        x, y, cam_frame = detect_wand()

        if x is not None and y is not None:
            wand_positions.append((x, y))
        check_directions()
        check_jump_kill(x, y)
        if cam_frame is not None:
            cam_rgb = cv2.cvtColor(cam_frame, cv2.COLOR_BGR2RGB)
            cam_surf = pygame.surfarray.make_surface(np.rot90(cam_rgb))
            win.blit(pygame.transform.scale(cam_surf, (WIN_W, WIN_H)), (0, 0))

        draw_neutral_zone()

        draw_wand(x, y)
 
        draw_circles()
  
        draw_status()

        pygame.display.update()

        if all_training_done():
            print("Training Completed!")
            return trained

if __name__ == "__main__":
    result = start_training()
    print(result)
