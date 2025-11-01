import pygame
from random import choice
from collections import deque
import heapq

pygame.init()

# --- Game setup ---
TILE = 60
cols = 15
rows = 15
WIDTH = cols * TILE + 200
HEIGHT = rows * TILE
FPS = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐇 Rabbit Maze Game")
clock = pygame.time.Clock()

# --- Load images ---
rabbit_img = pygame.image.load("rabbit.png")
carrot_img = pygame.image.load("carrot.png")
rabbit_img = pygame.transform.scale(rabbit_img, (TILE - 10, TILE - 10))
carrot_img = pygame.transform.scale(carrot_img, (TILE - 10, TILE - 10))

# --- Colors ---
WALL_COLOR = (157, 0, 255)
BG_COLOR = (30, 5, 60)
VISITED_COLOR = (255, 200, 0)
GLOW_COLOR = (255, 255, 180)

# Cell class
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            pygame.draw.rect(screen, (255, 60, 255), (x, y, TILE, TILE))
        if self.walls['top']:
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x + TILE, y), 2)
        if self.walls['right']:
            pygame.draw.line(screen, WALL_COLOR, (x + TILE, y), (x + TILE, y + TILE), 2)
        if self.walls['bottom']:
            pygame.draw.line(screen, WALL_COLOR, (x + TILE, y + TILE), (x, y + TILE), 2)
        if self.walls['left']:
            pygame.draw.line(screen, WALL_COLOR, (x, y + TILE), (x, y), 2)

    def draw_current_cell(self):
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(screen, (255, 240, 180), (x + 2, y + 2, TILE - 4, TILE - 4), border_radius=6)

    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x >= cols or y < 0 or y >= rows:
            return None
        return grid[find_index(x, y)]

    def check_neighbors(self):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        for cell in [top, right, bottom, left]:
            if cell and not cell.visited:
                neighbors.append(cell)
        return choice(neighbors) if neighbors else None

# Maze generation (DFS)
grid = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid[0]
stack = []

while True:
    current_cell.visited = True
    next_cell = current_cell.check_neighbors()
    if next_cell:
        next_cell.visited = True
        dx, dy = current_cell.x - next_cell.x, current_cell.y - next_cell.y
        if dx == 1:
            current_cell.walls['left'] = False
            next_cell.walls['right'] = False
        elif dx == -1:
            current_cell.walls['right'] = False
            next_cell.walls['left'] = False
        if dy == 1:
            current_cell.walls['top'] = False
            next_cell.walls['bottom'] = False
        elif dy == -1:
            current_cell.walls['bottom'] = False
            next_cell.walls['top'] = False
        stack.append(current_cell)
        current_cell = next_cell
    elif stack:
        current_cell = stack.pop()
    else:
        break

# Game variables
rabbit_pos = [0, 0]
goal_pos = [cols - 1, rows - 1]
visited_cells = set()
auto_mode = False
auto_path = []
move_counter = 0
MOVE_DELAY = 5  # frames per move
score = 0

# Helper functions
def get_neighbors(cell):
    x, y = cell
    neighbors = []
    current = grid[x + y * cols]
    if not current.walls['top']:
        neighbors.append((x, y - 1))
    if not current.walls['right']:
        neighbors.append((x + 1, y))
    if not current.walls['bottom']:
        neighbors.append((x, y + 1))
    if not current.walls['left']:
        neighbors.append((x - 1, y))
    return [(nx, ny) for nx, ny in neighbors if 0 <= nx < cols and 0 <= ny < rows]

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])
def draw_multiline_text(text, x, y, max_width, font, color):
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, color), (x, y + i*font.get_height()))


def best_first_search(start, goal):
    open_set = [(heuristic(start, goal), start)]
    came_from = {}
    visited_bfs = set()
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        visited_bfs.add(current)
        for neighbor in get_neighbors(current):
            if neighbor not in visited_bfs and neighbor not in [c[1] for c in open_set]:
                heapq.heappush(open_set, (heuristic(neighbor, goal), neighbor))
                came_from[neighbor] = current
    return []

# --- Button setup ---
font = pygame.font.SysFont("arial", 24)
help_rect = pygame.Rect(cols*TILE + 30, 120, 140, 40)

# --- Game loop ---
running = True
while running:
    screen.fill(BG_COLOR)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if help_rect.collidepoint(event.pos):
                auto_path = best_first_search(tuple(rabbit_pos), tuple(goal_pos))
                auto_mode = True
                score -= 5  # optional

    keys = pygame.key.get_pressed()
    if not auto_mode:
        x, y = rabbit_pos
        current = grid[x + y * cols]
        if keys[pygame.K_UP] and not current.walls['top']:
            rabbit_pos[1] -= 1
        elif keys[pygame.K_DOWN] and not current.walls['bottom']:
            rabbit_pos[1] += 1
        elif keys[pygame.K_LEFT] and not current.walls['left']:
            rabbit_pos[0] -= 1
        elif keys[pygame.K_RIGHT] and not current.walls['right']:
            rabbit_pos[0] += 1
    else:
        move_counter += 1
        if move_counter >= MOVE_DELAY and auto_path:
            rabbit_pos = list(auto_path.pop(0))
            move_counter = 0
        elif not auto_path:
            auto_mode = False

    visited_cells.add(tuple(rabbit_pos))

    # --- Draw maze ---
    for cell in grid:
        cell.draw()

    # --- Glow visited cells ---
    for vx, vy in visited_cells:
        pygame.draw.rect(screen, GLOW_COLOR, (vx*TILE+8, vy*TILE+8, TILE-16, TILE-16), border_radius=8)

    # --- Draw rabbit & carrot ---
    screen.blit(carrot_img, (goal_pos[0]*TILE+5, goal_pos[1]*TILE+5))
    screen.blit(rabbit_img, (rabbit_pos[0]*TILE+5, rabbit_pos[1]*TILE+5))

    # Draw help button
    pygame.draw.rect(screen, (0,150,255), help_rect, border_radius=10)
    help_text = font.render("HELP", True, (255,255,255))
    screen.blit(help_text, (cols*TILE + 70, 130))

    # Additional text below HELP button
    long_text = "Press the Help button to find the best way to reach the carrot !"
    draw_multiline_text(long_text, cols*TILE + 20, 170, 160, font, (255, 255, 0))


    # --- Check win ---
    if tuple(rabbit_pos) == tuple(goal_pos):
        win_text = font.render("You reached the carrot! 🥕", True, (0,0,0))
        screen.blit(win_text, (WIDTH//2 - 150, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()





