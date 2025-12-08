import pygame
import sys
import time
import login
import firebase

def outro_screen( bg_image_path):
    score = firebase.getLevel(login.user)
    pygame.init()

    SCREEN_W, SCREEN_H = 1000, 520
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Game Over")

    # Load background if provided
    bg = None
    if bg_image_path:
        try:
            bg = pygame.image.load(bg_image_path)
            bg = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
        except:
            print("⚠️ Could not load background image. Showing plain background.")

    # Fonts
    font_title = pygame.font.SysFont("Arial", 80, bold=True)
    font_score = pygame.font.SysFont("Arial", 50)

    # Text surfaces
    title_text = font_title.render("GAME OVER", True, (255, 255, 255))
    score_text = font_score.render(f"Your Score: {score}", True, (255, 255, 0))

    start_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Draw background or black screen
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # Draw text
        screen.blit(title_text, (SCREEN_W//2 - title_text.get_width()//2, 200))
        screen.blit(score_text, (SCREEN_W//2 - score_text.get_width()//2, 350))

        pygame.display.update()

        # Auto-close after 6 seconds
        if time.time() - start_time >= 6:
            pygame.quit()
            return  # return to whatever called it
