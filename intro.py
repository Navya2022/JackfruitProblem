import pygame
import sys
import time

def intro_transition(title="WELCOME", subtitle="Get Ready!", bg_image_path=None):
    pygame.init()

    SCREEN_W, SCREEN_H = 1280, 720
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Intro Transition")

    # Load background if provided
    bg = None
    if bg_image_path:
        try:
            bg = pygame.image.load(bg_image_path)
            bg = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
        except:
            print("⚠️ Background image not found. Using black screen.")

    # Fonts
    font_title = pygame.font.SysFont("Arial", 90, bold=True)
    font_sub = pygame.font.SysFont("Arial", 50)

    # Render text
    title_surface = font_title.render(title, True, (255, 255, 255))
    sub_surface = font_sub.render(subtitle, True, (255, 255, 0))

    start_time = time.time()

    # Fade-in alpha
    alpha = 0

    # Create surfaces for smooth fade
    fade_surface = pygame.Surface((SCREEN_W, SCREEN_H))
    fade_surface.fill((0, 0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Draw background or black
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # Draw text
        screen.blit(title_surface, (SCREEN_W//2 - title_surface.get_width()//2, 200))
        screen.blit(sub_surface, (SCREEN_W//2 - sub_surface.get_width()//2, 350))

        # Fade in effect (alpha goes 255 → 0)
        if alpha > 0:
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
            alpha -= 3  # speed of fade (lower = slower)

        pygame.display.update()

        # End after 4 seconds
        if time.time() - start_time >= 4:
            break


    return  # return control to main.py
