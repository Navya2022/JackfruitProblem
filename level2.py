import pygame
import sys
import firebase
import login


pygame.init()


# Window
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HARRY POTTER")


CLOCK = pygame.time.Clock()
FPS = 60
over = False

# Colors
BLUE_DEEP = (5, 10, 40)
BLUE_LIGHT = (40, 120, 200)
GREEN_SEAWEED = (0, 150, 80)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
RED = (220, 50, 50)
GOLD = (255, 210, 0)
GRAY = (160, 160, 160)
PURPLE = (150, 0, 150)
BLACK = (0, 0, 0)


GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_STRENGTH = 20
STONE_SPEED = 10


FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 40)


# player image loading
PLAYER_IMG1= pygame.image.load("avatar1.png").convert_alpha()
PLAYER_IMG = pygame.transform.smoothscale(PLAYER_IMG1, (60, 80))


#friend image loading
FRIEND_IMG1 = pygame.image.load("avatar3.png").convert_alpha()
FRIEND_IMG = pygame.transform.smoothscale(FRIEND_IMG1, (60, 80))

#monster image loading
MONSTER_IMG1 = pygame.image.load("angry.jpeg").convert_alpha()
MONSTER_IMG = pygame.transform.smoothscale(MONSTER_IMG1, (80, 80))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((30, 90, 40))
        self.rect = self.image.get_rect(topleft=(x, y))



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_image = PLAYER_IMG
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))


        self.vel_x = 0 #horizontal speed
        self.vel_y = 0 #vertical speed
        self.on_ground = False #player is in the air
        self.facing = 1  #-1 left


        self.lives = 2
        self.coins = 0
        self.stones = 0
        self.treasures = 0



    def reset_position(self, x, y):
        self.rect.topleft = (x, y)
        self.vel_x = 0
        self.vel_y = 0


    def update(self, platforms):
        # Horizontal movement
        self.rect.x += self.vel_x
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right


        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > 20:
            self.vel_y = 20
        self.rect.y += self.vel_y


        # Vertical collision
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0: # falling down
                    self.rect.bottom = p.rect.top #standing on the block
                    self.vel_y = 0 #standing still
                    self.on_ground = True
                elif self.vel_y < 0: #cant jump ,will hit the bottom of the block
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0


        # Update facing for simple flip
        if self.vel_x > 0:
            self.facing = 1
        elif self.vel_x < 0:
            self.facing = -1


        # Visually flip for facing
        if self.facing == -1:
            self.image = pygame.transform.flip(self.base_image, True, False)
        else:
            self.image = self.base_image


    def move_left(self):
        self.vel_x = -PLAYER_SPEED


    def move_right(self):
        self.vel_x = PLAYER_SPEED


    def stop(self):
        self.vel_x = 0


    def jump(self):
        if self.on_ground: #prevents double jump in middle of the air
            self.vel_y = -JUMP_STRENGTH



class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (10, 10), 9)
        pygame.draw.circle(self.image, WHITE, (7, 7), 3)
        self.rect = self.image.get_rect(center=(x, y))



class StoneItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GRAY, (9, 9), 8)
        self.rect = self.image.get_rect(center=(x, y))



class Treasure(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((35, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GOLD, (0, 10, 35, 20))
        pygame.draw.rect(self.image, (200, 140, 0), (0, 0, 35, 10))
        pygame.draw.line(self.image, BLACK, (0, 10), (35, 10), 2)
        self.rect = self.image.get_rect(midbottom=(x, y))



class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = MONSTER_IMG
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.health = 3
        self.base_x = x
        self.move_range = 60
        self.speed = 1.2


    def update(self):
        # Simple side-to-side movement to make it harder
        self.rect.x += self.speed
        if self.rect.x > self.base_x + self.move_range or self.rect.x < self.base_x - self.move_range:
            self.speed *= -1



class StoneProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GRAY, (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction


    def update(self):
        self.rect.x += STONE_SPEED * self.direction # Remove if off-screen world bounds (0..level_width)
        if self.rect.right < 0 or self.rect.left > 5000:
            self.kill()



class Friend(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = FRIEND_IMG
        self.rect = self.image.get_rect(topleft=(x, y))




def draw_underwater_background(scroll_x):
    # Simple solid blue background
    SCREEN.fill(BLUE_LIGHT)

    # Seaweed
    for i in range(-1000, 4000, 120):
        base_x = i + scroll_x * 0.5
        if -50 < base_x < WIDTH + 50:
            pygame.draw.rect(SCREEN, GREEN_SEAWEED, (base_x, HEIGHT - 80, 20, 80))
            pygame.draw.circle(SCREEN, GREEN_SEAWEED, (int(base_x) + 10, HEIGHT - 80), 15)


    # Bubbles
    for i in range(-1000, 4000, 150):
        bx = (i + scroll_x * 1.2) % (WIDTH + 200) - 100
        by = HEIGHT - (i % HEIGHT)
        pygame.draw.circle(SCREEN, WHITE, (int(bx), int(by)), 6, 1)


    # Fish
    for i in range(-1000, 4000, 200):
        fx = i + scroll_x * 0.8
        fy = 150 + (i % 200)
        if -50 < fx < WIDTH + 50:
            body_color = (255, 100 + (i % 100), 100)
            pygame.draw.ellipse(SCREEN, body_color, (fx, fy, 40, 20))
            pygame.draw.polygon( SCREEN,body_color,[(fx + 40, fy + 10), (fx + 55, fy), (fx + 55, fy + 20)],)
            pygame.draw.circle(SCREEN, WHITE, (int(fx) + 8, int(fy) + 8), 3)
            pygame.draw.circle(SCREEN, BLACK, (int(fx) + 8, int(fy) + 8), 1)

def text(player, time_left, game_over, game_won):
    global over

    # Timer(Clock)
    timer_text = FONT.render(f"Time: {max(0, int(time_left))}s", True, WHITE)
    SCREEN.blit(timer_text, (10, 10))

    # Lives
    lives_text = FONT.render(f"Lives: {player.lives}", True, WHITE)
    SCREEN.blit(lives_text, (10, 40))


    # Coins and stones
    coins_text = FONT.render(f"Coins: {player.coins}", True, GOLD)
    SCREEN.blit(coins_text, (10, 70))


    stones_text = FONT.render(f"Stones: {player.stones}", True, GRAY)
    SCREEN.blit(stones_text, (10, 100))


    treasure_text = FONT.render(f"Treasures: {player.treasures}/3", True, WHITE)
    SCREEN.blit(treasure_text, (10, 130))


    # Controls hint
    controls = FONT.render("ENTER x3 = Kill Monster (3 stones)", True, WHITE)
    SCREEN.blit(controls, (10, HEIGHT - 60))


    if game_over:
        txt = BIG_FONT.render("GAME OVER", True, RED)
        SCREEN.blit(txt, (WIDTH // 2 - txt.get_width() // 2,
                        HEIGHT // 2 - txt.get_height() // 2))
        pygame.display.update()      # <-- IMPORTANT
        pygame.time.wait(3000)
        over = True       # wait but allow OS events
        return


    if game_won:
        txt = BIG_FONT.render("You saved your friend!", True, WHITE)
        SCREEN.blit(txt, (WIDTH // 2 - txt.get_width() // 2,
                        HEIGHT // 2 - txt.get_height() // 2))
        firebase.updateMarks(login.user, 50)
        pygame.display.update()
        pygame.time.wait(3000)
        over = True
        return


def main():
    global over
    level_width = 4500
    camera_x = 0


    start_x, start_y = 100, HEIGHT - 200
    player = Player(start_x, start_y)
    friend = Friend(level_width - 150, HEIGHT - 200)


    # Platforms
    platforms = pygame.sprite.Group()
    platforms.add(Platform(0, HEIGHT - 40, level_width, 40))
    platforms.add(Platform(300, HEIGHT - 150, 150, 20))
    platforms.add(Platform(650, HEIGHT - 220, 150, 20))
    platforms.add(Platform(1100, HEIGHT - 180, 150, 20))
    platforms.add(Platform(1550, HEIGHT - 240, 150, 20))
    platforms.add(Platform(2000, HEIGHT - 200, 150, 20))
    platforms.add(Platform(2400, HEIGHT - 160, 180, 20))
    platforms.add(Platform(2800, HEIGHT - 230, 150, 20))
    platforms.add(Platform(3200, HEIGHT - 260, 150, 20))
    platforms.add(Platform(3600, HEIGHT - 220, 180, 20))
    platforms.add(Platform(4000, HEIGHT - 180, 150, 20))


    # Coins and stones scattered
    coins = pygame.sprite.Group()
    stones_items = pygame.sprite.Group()


    coin_positions = [ (350, HEIGHT - 190), (380, HEIGHT - 190), (410, HEIGHT - 190),
        (700, HEIGHT - 260), (730, HEIGHT - 260), (760, HEIGHT - 260),
        (1150, HEIGHT - 220), (1180, HEIGHT - 220), (1210, HEIGHT - 220),
        (1600, HEIGHT - 280), (1630, HEIGHT - 280),
        (2050, HEIGHT - 240), (2080, HEIGHT - 240),
        (2450, HEIGHT - 200), (2480, HEIGHT - 200), (2510, HEIGHT - 200),
        (2850, HEIGHT - 270), (2880, HEIGHT - 270),
        (3250, HEIGHT - 300), (3280, HEIGHT - 300),
        (3650, HEIGHT - 260), (3680, HEIGHT - 260),
        (4050, HEIGHT - 220), (4080, HEIGHT - 220)]
    for x, y in coin_positions:
        coins.add(Coin(x, y))


    stone_positions = [(500, HEIGHT - 80), (900, HEIGHT - 80), (1300, HEIGHT - 80),
        (1800, HEIGHT - 80), (2200, HEIGHT - 80), (2600, HEIGHT - 80),
        (3000, HEIGHT - 80), (3400, HEIGHT - 80), (3800, HEIGHT - 80)]
    for x, y in stone_positions:
        stones_items.add(StoneItem(x, y))


    # Treasures and monsters guarding them
    treasures = pygame.sprite.Group()
    monsters = pygame.sprite.Group()


    treasure_positions = [(1800, HEIGHT - 80),
        (3000, HEIGHT - 80),
        (4200, HEIGHT - 80)]
    for x, y in treasure_positions:
        treasures.add(Treasure(x, y))


    monster_positions = [(1800, HEIGHT - 80),
        (3000, HEIGHT - 80),
        (4200, HEIGHT - 80)]
    for x, y in monster_positions:
        monsters.add(Monster(x, y))


    projectiles = pygame.sprite.Group()


    all_sprites = pygame.sprite.Group(
        player, friend,
        *platforms, *coins, *stones_items, *treasures, *monsters
    )


    running = True
    game_over = False
    game_won = False


    # Timer set to 60 seconds
    time_limit = 60.0
    start_ticks = pygame.time.get_ticks()


    # press enter key thrice to kill the monster
    enter_press_count = 0
    enter_press_time = 0  # reset after timeout


    while running:
        dt = CLOCK.tick(FPS) / 1000.0  # seconds
        current_ticks = pygame.time.get_ticks()
        time_taken = (current_ticks - start_ticks) / 1000.0
        time_left = time_limit - time_taken


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
           
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not game_over and not game_won:
                    current_time = pygame.time.get_ticks() # Reset counter if too much time passed since last enter (2 seconds)
                    if current_time - enter_press_time > 2000:
                        enter_press_count = 0
                   
                    enter_press_count += 1
                    enter_press_time = current_time
                   
                    # On 3rd press, kill nearest monster in front
                    if enter_press_count >= 3 and player.stones >= 3:
                        # Find nearest monster in front of player (within 150 pixels)
                        monsters_in_front = []
                        for m in monsters:
                            distance = m.rect.centerx - player.rect.centerx
                            # Check if monster is in front and within range
                            if player.facing == 1 and 0 < distance < 150:
                                monsters_in_front.append((m, distance))
                            elif player.facing == -1 and 0 > distance > -150:
                                monsters_in_front.append((m, -distance))
                       
                        if monsters_in_front:
                            # Sort by distance and kill closest
                            monsters_in_front.sort(key=lambda x: x[1])
                            target_monster, _ = monsters_in_front[0]
                            player.stones -= 3
                            target_monster.health = 0
                            target_monster.kill()
                            print("Monster killed with 3 Enter presses!")
                   
                    enter_press_count = min(enter_press_count, 3)  # Cap at 3
                elif event.key == pygame.K_r and game_over:
                    return main()


        keys = pygame.key.get_pressed()


        if not game_over and not game_won: # Movement
            if keys[pygame.K_LEFT]:
                player.move_left()
            elif keys[pygame.K_RIGHT]:
                player.move_right()
            else:
                player.stop()


            if keys[pygame.K_SPACE]:
                player.jump()


            # Shoot stone using enter key
            if keys[pygame.K_s] and player.stones > 0:
                if len(projectiles) == 0 or projectiles.sprites()[-1].rect.x < player.rect.x - 50:
                    direction = player.facing if player.facing != 0 else 1
                    proj = StoneProjectile(player.rect.centerx, player.rect.centery, direction)
                    projectiles.add(proj)
                    all_sprites.add(proj)
                    player.stones -= 1

        if not game_over and not game_won:
            player.update(platforms)
            monsters.update()
            projectiles.update()


            # Camera updating
            camera_x = player.rect.centerx - WIDTH // 2
            if camera_x < 0:
                camera_x = 0
            if camera_x > level_width - WIDTH:
                camera_x = level_width - WIDTH


            # Collect coins
            collected_coins = pygame.sprite.spritecollide(player, coins, True)
            if collected_coins:
                player.coins += len(collected_coins)


            # Collect stones
            collected_stones = pygame.sprite.spritecollide(player, stones_items, True)
            if collected_stones:
                player.stones += len(collected_stones)


            # Projectiles hit monsters
            for proj in projectiles.copy():
                hit_list = pygame.sprite.spritecollide(proj, monsters, False)
                if hit_list:
                    proj.kill()
                    for m in hit_list:
                        m.health -= 1
                        if m.health <= 0:
                            m.kill()
                    continue


            # Player touches the monster then loses 1 life
            if pygame.sprite.spritecollide(player, monsters, False):
                player.lives -= 1
                if player.lives <= 0:
                    game_over = True
                else:
                    player.reset_position(start_x, start_y)


            # Player can access treasure only after killing monster
            for t in treasures.copy():
                if player.rect.colliderect(t.rect):
                    nearby_monsters = [m for m in monsters if abs(m.rect.centerx - t.rect.centerx) < 80]
                    if not nearby_monsters:
                        player.treasures += 1
                        t.kill()


            # winning
            if player.rect.colliderect(friend.rect) and player.treasures >= 3:
                game_won = True

            # Time up
            if time_left <= 0 and not game_won:
                player.lives -= 1
                if player.lives <= 0:
                    game_over = True
                else:
                    start_ticks = pygame.time.get_ticks()
                    player.reset_position(start_x, start_y)


        # Drawing
        SCREEN.fill(BLUE_DEEP)
        draw_underwater_background(-camera_x)


        # Draw all game objects
        for p in platforms:
            SCREEN.blit(p.image, (p.rect.x - camera_x, p.rect.y))
        for c in coins:
            SCREEN.blit(c.image, (c.rect.x - camera_x, c.rect.y))
        for s_item in stones_items:
            SCREEN.blit(s_item.image, (s_item.rect.x - camera_x, s_item.rect.y))
        for t in treasures:
            SCREEN.blit(t.image, (t.rect.x - camera_x, t.rect.y))
        for m in monsters:
            SCREEN.blit(m.image, (m.rect.x - camera_x, m.rect.y))
        for proj in projectiles:
            SCREEN.blit(proj.image, (proj.rect.x - camera_x, proj.rect.y))
        SCREEN.blit(friend.image, (friend.rect.x - camera_x, friend.rect.y))
        SCREEN.blit(player.image, (player.rect.x - camera_x, player.rect.y))


        # showing how many stones are hit(how many time enter key is clicked)
        if enter_press_count > 0:
            count_text = FONT.render(f"ENTER: {enter_press_count}/3", True, WHITE)
            SCREEN.blit(count_text, (WIDTH - 150, 10))


        text(player, time_left, game_over, game_won)
        if over:
            return
        pygame.display.flip()


    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()