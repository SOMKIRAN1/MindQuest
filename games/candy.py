import pygame, random, sys, time
from pygame.locals import *

# ---------- Game Constants ----------
BOARDWIDTH = 8
BOARDHEIGHT = 8
TILESIZE = 64
MARGIN_TOP = 100  # space for score/timer above board
WINDOWWIDTH = BOARDWIDTH * TILESIZE
WINDOWHEIGHT = BOARDHEIGHT * TILESIZE + MARGIN_TOP
FPS = 30
NUMCOLORS = 6
GAMETIME = 60  # seconds

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255)   # Cyan
]


def getRandomBoard():
    board = [[random.randint(0, NUMCOLORS - 1) for i in range(BOARDHEIGHT)] for j in range(BOARDWIDTH)]
    while findMatches(board):
        board = [[random.randint(0, NUMCOLORS - 1) for i in range(BOARDHEIGHT)] for j in range(BOARDWIDTH)]
    return board

def drawBoard(screen, board, selected, ai_move=None):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            color = COLORS[board[x][y]]
            rect = pygame.Rect(x*TILESIZE, y*TILESIZE + MARGIN_TOP, TILESIZE, TILESIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2) # for boundry around tiles

            # Highlight player's selected tile
            if selected == (x, y):
                pygame.draw.rect(screen, (255, 255, 255), rect, 4)

            # Highlight AI-suggested move
            if ai_move and (x, y) in ai_move:
                pygame.draw.rect(screen, (0, 0, 0), rect, 4)

def findMatches(board):
    matches = set()
    # Horizontal
    for y in range(BOARDHEIGHT):
        for x in range(BOARDWIDTH - 2):
            if board[x][y] == board[x+1][y] == board[x+2][y]:
                matches.update([(x+i, y) for i in range(3)])
                i = x + 3
                while i < BOARDWIDTH and board[i][y] == board[x][y]:
                    matches.add((i, y))
                    i += 1
    # Vertical
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT - 2):
            if board[x][y] == board[x][y+1] == board[x][y+2]:
                matches.update([(x, y+i) for i in range(3)])
                i = y + 3
                while i < BOARDHEIGHT and board[x][i] == board[x][y]:
                    matches.add((x, i))
                    i += 1
    return list(matches)

def removeMatches(board, matches):
    for (x, y) in matches:
        board[x][y] = None

def dropTiles(board):  # to refill the board after matches are removed
    for x in range(BOARDWIDTH):
        col = [board[x][y] for y in range(BOARDHEIGHT) if board[x][y] is not None]
        missing = BOARDHEIGHT - len(col)
        new_col = [random.randint(0, NUMCOLORS - 1) for i in range(missing)] + col
        for y in range(BOARDHEIGHT):
            board[x][y] = new_col[y]

def swapTiles(board, pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    board[x1][y1], board[x2][y2] = board[x2][y2], board[x1][y1]

def isAdjacent(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2) == 1

# DFS: Cluster Detection 
def dfsCluster(board, x, y, color, visited):
    if (x, y) in visited or board[x][y] != color:
        return []
    visited.add((x, y))
    cluster = [(x, y)]
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < BOARDWIDTH and 0 <= ny < BOARDHEIGHT:
            cluster += dfsCluster(board, nx, ny, color, visited)
    return cluster

def findAllClusters(board):
    visited = set()
    clusters = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if (x, y) not in visited:
                cluster = dfsCluster(board, x, y, board[x][y], visited)
                if len(cluster) >= 3:
                    clusters.append(cluster)
    return clusters

# BFS: AI Move Finder 
def bfsBestMove(board):
    best_move = None
    best_score = 0

    directions = [(1,0), (-1,0), (0,1), (0,-1)]
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < BOARDWIDTH and 0 <= ny < BOARDHEIGHT:
                    new_board = [row[:] for row in board]
                    swapTiles(new_board, (x, y), (nx, ny))
                    matches = findMatches(new_board)
                    score_gain = len(matches)
                    if score_gain > best_score:
                        best_score = score_gain
                        best_move = ((x, y), (nx, ny))
    return best_move, best_score

# Main Game
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Tile Matching Game (with DFS & BFS AI)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Load match sound
    try:
        match_sound = pygame.mixer.Sound("game-start-6104.mp3")
    except:
        match_sound = None
        print("Could not load sound")

    board = getRandomBoard()
    score = 0
    start_time = time.time()
    selected = None

    while True:
        elapsed = time.time() - start_time
        remaining = int(GAMETIME - elapsed)
        if remaining <= 0:
            break

        # Compute AI best move suggestion (BFS-based)
        ai_move, ai_gain = bfsBestMove(board)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                grid_x = x // TILESIZE
                grid_y = (y - MARGIN_TOP) // TILESIZE
                if 0 <= grid_x < BOARDWIDTH and 0 <= grid_y < BOARDHEIGHT:
                    selected = (grid_x, grid_y)

            elif event.type == KEYDOWN and selected is not None:
                x, y = selected
                if event.key == K_LEFT and x > 0:
                    target = (x - 1, y)
                elif event.key == K_RIGHT and x < BOARDWIDTH - 1:
                    target = (x + 1, y)
                elif event.key == K_UP and y > 0:
                    target = (x, y - 1)
                elif event.key == K_DOWN and y < BOARDHEIGHT - 1:
                    target = (x, y + 1)
                else:
                    target = None

                if target and isAdjacent(selected, target):
                    swapTiles(board, selected, target)
                    matches = findMatches(board)
                    if matches:
                        if match_sound:
                            match_sound.play()
                        while matches:
                            removeMatches(board, matches)
                            score += len(matches)
                            dropTiles(board)
                            matches = findMatches(board)
                    else:
                        swapTiles(board, selected, target)

        # Draw UI
        screen.fill(WHITE)
        score_text = font.render(f"Score: {score}", True, BLACK)
        time_text = font.render(f"Time: {remaining}s", True, BLACK)
        ai_text = font.render("AI Suggestion (BFS)", True, (100, 0, 100))
        screen.blit(score_text, (20, 30))
        screen.blit(time_text, (WINDOWWIDTH - 180, 30))
        screen.blit(ai_text, (WINDOWWIDTH//2 - 100, 60))

        drawBoard(screen, board, selected, ai_move)

        pygame.display.update()
        clock.tick(FPS)

    # Game Over Screen
    screen.fill(WHITE)
    game_over = font.render("TIME UP!", True, (255, 0, 0))
    final_score = font.render(f"Final Score: {score}", True, BLACK)
    screen.blit(game_over, (WINDOWWIDTH//2 - 60, WINDOWHEIGHT//2 - 40))
    screen.blit(final_score, (WINDOWWIDTH//2 - 90, WINDOWHEIGHT//2 + 10))
    pygame.display.update()
    pygame.time.wait(4000)
    pygame.quit()

# ---------- Run ----------
if __name__ == "__main__":
    main()







    
   
                     
                             
                             
                      
    
                                              
                