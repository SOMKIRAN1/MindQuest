import pygame
from pygame.locals import *
import random

pygame.init()

# Background music setup
pygame.mixer.music.load("retro-arcade-game-music-297305.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.6)

# Game window
width = 600
height = 600
scoreboard_height = 40
window_size = (width, height + scoreboard_height)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Mini Candy Crush")

# List of colors for candies
candy_colors = ['blue', 'green', 'orange', 'purple', 'pink', 'red', 'teal']

# Candy size in pixels
candy_width = 50
candy_height = 50
candy_size = (candy_width, candy_height)

class Candy:
    def __init__(self, row_num, col_num):
        self.row_num = row_num
        self.col_num = col_num
        self.color = random.choice(candy_colors)
        image_name = f'swirl_{self.color}.png'
        self.image = pygame.image.load(image_name)
        self.image = pygame.transform.smoothscale(self.image, candy_size)
        self.rect = self.image.get_rect()
        self.rect.left = col_num * candy_width
        self.rect.top = row_num * candy_height

    def draw(self):
        screen.blit(self.image, self.rect)     # blit is like copy paste the image onto the screen

    def snap(self):
        self.rect.top = self.row_num * candy_height
        self.rect.left = self.col_num * candy_width

# Create the board of candies
board = []
for row_num in range(height // candy_height):
    board.append([])
    for col_num in range(width // candy_width):
        candy = Candy(row_num, col_num)
        board[row_num].append(candy)

def draw():
    # Draw background
    pygame.draw.rect(screen, (255,255,255), (0, 0, width, height + scoreboard_height))

    # Draw candies
    for row in board:
        for candy in row:
            candy.draw()

    # Highlight selected candy
    if selected_candy is not None:
        pygame.draw.rect(screen, (0,0,0), selected_candy.rect, 2)

    # Display score and moves
    font = pygame.font.SysFont('monoface', 29)
    score_text = font.render(f'Score: {score}', 1, (0, 0, 0))
    score_text_rect = score_text.get_rect(center=(width / 4, height + scoreboard_height / 2))
    screen.blit(score_text, score_text_rect)

    moves_text = font.render(f'Moves: {moves}', 1, (0, 0, 0))
    moves_text_rect = moves_text.get_rect(center=(3 * width / 4, height + scoreboard_height / 2))
    screen.blit(moves_text, moves_text_rect)

def swap(candy1, candy2):
    temp_row = candy1.row_num
    temp_col = candy1.col_num
    candy1.row_num = candy2.row_num
    candy1.col_num = candy2.col_num
    candy2.row_num = temp_row
    candy2.col_num = temp_col

    board[candy1.row_num][candy1.col_num] = candy1
    board[candy2.row_num][candy2.col_num] = candy2

    candy1.snap()
    candy2.snap()

def find_matches(candy, matches):  # candy(i) : elements in each row 
      # dfs on 2d to find all the candies of the same color connected to the given candy
    matches.add(candy)

    # top
    if candy.row_num > 0:  # check if row_num is not the first row
        neighbor = board[candy.row_num - 1][candy.col_num]
        if candy.color == neighbor.color and neighbor not in matches:
            matches.update(find_matches(neighbor, matches))
    # bottom
    if candy.row_num < height / candy_height - 1: # check if row_num is not the last row
        neighbor = board[candy.row_num + 1][candy.col_num]
        if candy.color == neighbor.color and neighbor not in matches:
            matches.update(find_matches(neighbor, matches))
    # left
    if candy.col_num > 0: # check if col_num is not the first column
        neighbor = board[candy.row_num][candy.col_num - 1]
        if candy.color == neighbor.color and neighbor not in matches:
            matches.update(find_matches(neighbor, matches))
    # right
    if candy.col_num < width / candy_width - 1: # check if col_num is not the last column
        neighbor = board[candy.row_num][candy.col_num + 1]
        if candy.color == neighbor.color and neighbor not in matches:
            matches.update(find_matches(neighbor, matches))

    return matches

def match_three(candy):  
    matches = find_matches(candy, set())
    if len(matches) >= 3:
        return matches
    else:
        return set()

# Game variables
selected_candy = None
score = 0
moves = 0
clock = pygame.time.Clock()
running = True

while running:
    matches = set()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # Select a candy on mouse click
        if event.type == MOUSEBUTTONDOWN:
            for row in board:
                for candy in row:
                    if candy.rect.collidepoint(event.pos):
                        selected_candy = candy

        # Swap using arrow keys
        if event.type == KEYDOWN and selected_candy is not None:
            neighbor = None
            if event.key == K_LEFT and selected_candy.col_num > 0:
                neighbor = board[selected_candy.row_num][selected_candy.col_num - 1]
            elif event.key == K_RIGHT and selected_candy.col_num < width / candy_width - 1:
                neighbor = board[selected_candy.row_num][selected_candy.col_num + 1]
            elif event.key == K_UP and selected_candy.row_num > 0:
                neighbor = board[selected_candy.row_num - 1][selected_candy.col_num]
            elif event.key == K_DOWN and selected_candy.row_num < height / candy_height - 1:
                neighbor = board[selected_candy.row_num + 1][selected_candy.col_num]

            if neighbor:
                swap(selected_candy, neighbor)
                matches.update(match_three(selected_candy))
                matches.update(match_three(neighbor))
                moves += 1
                selected_candy = None  # Deselect after move

    draw()
    pygame.display.update()

    # Handle matches
    if len(matches) >= 3:
        score += len(matches)
        while len(matches) > 0:
            clock.tick(60)
            for candy in matches:
                new_width = candy.image.get_width() - 1
                new_height = candy.image.get_height() - 1
                new_size = (new_width, new_height)
                candy.image = pygame.transform.smoothscale(candy.image, new_size)
                candy.rect.left = candy.col_num * candy_width + (candy_width - new_width) / 2
                candy.rect.top = candy.row_num * candy_height + (candy_height - new_height) / 2

            # Replace vanished candies 
            for row_num in range(len(board)):
                for col_num in range(len(board[row_num])):
                    candy = board[row_num][col_num]
                    if candy.image.get_width() <= 0 or candy.image.get_height() <= 0:
                        matches.remove(candy)
                        board[row_num][col_num] = Candy(row_num, col_num)

            draw()
            pygame.display.update()

pygame.quit()
