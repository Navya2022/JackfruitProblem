import pygame
import random

TILE_SIZE = 40
FPS = 60
SHIFT_INTERVAL = 4000  # ms

# Colors
BLACK = (0, 0, 0)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
BROWN = (137, 81, 41)

# Maze layout
MAZE_LAYOUT = [
    "111111111111111111111111111111",
    "1S0010010000001110000000000001",
    "100011011011110101111011111101",
    "100000010000000100000010000001",
    "111000110111011111101110111101",
    "100010000100000000001000100001",
    "101110111101111011111011101101",
    "1000001000000010000000000010E1",
    "111110101111101011111110111111",
    "100000001000001000000010000011",
    "101111101011111011110111110111",
    "100000100010000010000100000011",
    "111110111110111110111101111111",
    "100010000000100000000100000011",
    "111111111111111111111111111111",
]


class ShiftingMaze:
    def __init__(self, x, y, width, height, layout=MAZE_LAYOUT):
        # Window properties
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Maze setup
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.maze = [list(row) for row in layout]
        self.tile_w = width / self.cols
        self.tile_h = height / self.rows

        self.player_pos = self.find_start()
        self.win = False
        self.last_shift = pygame.time.get_ticks()

        # Load vines
        vine_img = pygame.image.load("vines.jpeg").convert_alpha()
        self.vine_img = pygame.transform.scale(vine_img, (int(self.tile_w), int(self.tile_h)))

    def find_start(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] == "S":
                    return [c, r]
        return [0, 0]

    def can_move(self, nx, ny):
        if nx < 0 or ny < 0 or nx >= self.cols or ny >= self.rows:
            return False
        return self.maze[ny][nx] != "1"

    def move_player(self, direction):
        if self.win:
            return

        dx, dy = 0, 0
        if direction == "UP":
            dy = -1
        elif direction == "DOWN":
            dy = 1
        elif direction == "LEFT":
            dx = -1
        elif direction == "RIGHT":
            dx = 1

        nx = self.player_pos[0] + dx
        ny = self.player_pos[1] + dy

        if self.can_move(nx, ny):
            self.player_pos = [nx, ny]

    def shift_maze_region(self):
        region_x = random.randint(1, self.cols - 6)
        region_y = random.randint(1, self.rows - 6)

        for y in range(region_y, region_y + 5):
            for x in range(region_x, region_x + 5):
                if self.maze[y][x] in ("S", "E"):
                    continue
                if [x, y] == self.player_pos:
                    self.maze[y][x] = "0"
                    continue
                self.maze[y][x] = "1" if random.random() < 0.4 else "0"

    def update(self):
        # If already won, freeze maze and return win flag
        if self.win:
            return True

        # Check periodic shifting
        now = pygame.time.get_ticks()
        if now - self.last_shift > SHIFT_INTERVAL:
            self.shift_maze_region()
            self.last_shift = now

        # Check win
        if self.maze[self.player_pos[1]][self.player_pos[0]] == "E":
            self.win = True
            return True

        return False

    def draw(self, surface):
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.maze[r][c]
                x = self.x + c * self.tile_w
                y = self.y + r * self.tile_h

                if tile == "1":
                    surface.blit(self.vine_img, (x, y))
                elif tile == "E":
                    pygame.draw.rect(surface, GREEN, (x, y, self.tile_w, self.tile_h))
                else:
                    pygame.draw.rect(surface, BROWN, (x, y, self.tile_w, self.tile_h))

        # Draw player
        px = self.x + self.player_pos[0] * self.tile_w
        py = self.y + self.player_pos[1] * self.tile_h
        pygame.draw.rect(surface, BLUE, (px + 5, py + 5, self.tile_w - 10, self.tile_h - 10))

        # Win text overlay
        if self.win:
            font = pygame.font.SysFont("arial", 40)
            text = font.render("You Found the Cup!", True, (255, 255, 255))
            rect = text.get_rect(center=(self.x + self.width / 2,
                                         self.y + self.height / 2))
            surface.blit(text, rect)



def run_level3(screen, WIDTH, HEIGHT):
    clock = pygame.time.Clock()
    maze = ShiftingMaze(0, 0, WIDTH, HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    maze.move_player("UP")
                elif event.key == pygame.K_DOWN:
                    maze.move_player("DOWN")
                elif event.key == pygame.K_LEFT:
                    maze.move_player("LEFT")
                elif event.key == pygame.K_RIGHT:
                    maze.move_player("RIGHT")

        win_flag = maze.update()

        screen.fill(BLACK)
        maze.draw(screen)
        pygame.display.update()


        if win_flag:
            maze.draw(screen)
            pygame.display.update()
            pygame.time.wait(2000)
            return   # <-- return to main.py

        clock.tick(FPS)
