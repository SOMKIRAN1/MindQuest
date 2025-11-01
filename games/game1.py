import pygame
import random
import os
import time
from collections import deque

pygame.mixer.init()
pygame.init()

screen_width = 900
screen_height = 720
TOP_PANEL = 120
GAME_HEIGHT = 600

snake_size = 15
GRID_W = screen_width // snake_size
GRID_H = GAME_HEIGHT // snake_size


gameWindow = pygame.display.set_mode((screen_width, screen_height))

bgimg = pygame.image.load("snake.png")
bgimg = pygame.transform.scale(bgimg, (screen_width, GAME_HEIGHT)).convert_alpha()

pygame.display.set_caption("Snake game")
pygame.display.update()
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)


# Functions

def plot_snake(gameWindow, color, snk_list, snake_size):
    for x, y in snk_list:
        pygame.draw.rect(gameWindow, color, [x, y, snake_size, snake_size])

def screen_score(text, color, x, y):
    screen_text = font.render(text, True, color)
    gameWindow.blit(screen_text, [x, y])

def pix_to_grid(px, py):
    gy = (py - TOP_PANEL) // snake_size
    gx = px // snake_size
    return gx, gy

def grid_to_pix(gx, gy):
    return gx * snake_size, (gy * snake_size) + TOP_PANEL

def bfs(start, goal, grid_w, grid_h, blocked):
    q = deque([start])
    visited = set([start])
    parent = {}
    while q:
        node = q.popleft()
        if node == goal:
            path = []
            cur = goal
            while cur != start:
                path.append(cur)
                cur = parent[cur]
            path.append(start)
            path.reverse()
            return path
        x, y = node
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<grid_w and 0<=ny<grid_h and (nx,ny) not in visited and (nx,ny) not in blocked:
                visited.add((nx,ny))
                parent[(nx,ny)] = node
                q.append((nx,ny))
    return []

def build_blocked_set(snk_list, exclude_tail=True):
    blocked = set()
    upto = len(snk_list)-1 if exclude_tail else len(snk_list)
    for i in range(upto):
        gx, gy = pix_to_grid(snk_list[i][0], snk_list[i][1])
        blocked.add((gx, gy))
    return blocked

# Game Screens

def welcome():
    exit_game = False
    while not exit_game:
        gameWindow.fill((0, 140, 0))
        screen_score("Welcome to Snakes", (255, 255, 255), 260, 250)
        screen_score("Press Space Bar To Play", (255, 255, 255), 240, 290)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mixer.music.load('snkbg.mp3')
                    pygame.mixer.music.play(-1)
                    gameLoop()
        pygame.display.update()
        clock.tick(60)

# Game Loop

def gameLoop():
    exit_game = False
    game_over = False
    snake_x = 45
    snake_y = TOP_PANEL + 55
    velocity_x = 0
    velocity_y = 0
    init_valocity = snake_size  # move one cell per frame for BFS mode
    food_x = random.randint(0, GRID_W-1) * snake_size
    food_y = random.randint(0, GRID_H-1) * snake_size + TOP_PANEL
    score = 0
    fps = 15  # slower for visible BFS moves

    if not os.path.exists("highscore.txt"):
        with open("highscore.txt","w") as f:
            f.write("0")
    with open("highscore.txt","r") as f:
        highscore = f.read()

    snk_list = []
    snk_length = 1

    ai_mode = 'player'
    planned_path = []
    path_step_index = 0
    bfs_start_time = None

    while not exit_game:
        if game_over:
            gameWindow.fill((255,0,0))
            screen_score("Game Over! score: "+str(score)+" , press Enter to restart", (255,255,255), 100,100)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        welcome()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:
                        ai_mode = 'bfs'
                        bfs_start_time = time.time()
                        planned_path = []
                    if event.key == pygame.K_p:
                        ai_mode = 'player'
                        planned_path = []
                    if ai_mode == 'player':
                        if event.key == pygame.K_RIGHT:
                            velocity_x = init_valocity
                            velocity_y = 0
                        if event.key == pygame.K_LEFT:
                            velocity_x = -init_valocity
                            velocity_y = 0
                        if event.key == pygame.K_UP:
                            velocity_x = 0
                            velocity_y = -init_valocity
                        if event.key == pygame.K_DOWN:
                            velocity_x = 0
                            velocity_y = init_valocity
                    if event.key == pygame.K_q:
                        score += 10

            # BFS Auto Mode 
            if ai_mode == 'bfs':
                if time.time() - bfs_start_time >= 60:
                    game_over = True
                    pygame.mixer.music.load('gameover.wav')
                    pygame.mixer.music.play(-1)
                    print("Time Up! Game Over!")
                    continue

                head_grid = pix_to_grid(snake_x, snake_y)
                food_grid = pix_to_grid(food_x, food_y)
                blocked = build_blocked_set(snk_list)

                if not planned_path or planned_path[-1]!=food_grid:
                    planned_path = bfs(head_grid, food_grid, GRID_W, GRID_H, blocked)
                    path_step_index = 0

                if planned_path and path_step_index < len(planned_path)-1:
                    next_cell = planned_path[path_step_index+1]
                    snake_x, snake_y = grid_to_pix(next_cell[0], next_cell[1])
                    path_step_index += 1

            else:
                snake_x += velocity_x
                snake_y += velocity_y

            # collision with food
            if abs(snake_x - food_x)<10 and abs(snake_y - food_y)<10:
                score += 10
                food_x = random.randint(0, GRID_W-1)*snake_size
                food_y = random.randint(0, GRID_H-1)*snake_size + TOP_PANEL
                snk_length +=5
                planned_path=[]
                if score>int(highscore):
                    highscore=score
                    with open("highscore.txt","w") as f:
                        f.write(str(highscore))

            #Draw UI + Game
            pygame.draw.rect(gameWindow, (34,34,34), [0,0,screen_width, TOP_PANEL])
            screen_score(f"Score: {score}  |  Highscore: {highscore}", (255,255,255), 10,8)
            screen_score("Press P - Manual  |  B - BFS Auto", (255,255,255), 10,40)
            screen_score("Press Q - +10 score  |  Enter - Restart", (255,255,255), 10,72)
            screen_score(f"Mode: {'BFS Auto' if ai_mode=='bfs' else 'Manual'}", (255,255,255), 700,8)
            if ai_mode=='bfs' and bfs_start_time:
                remaining=int(60-(time.time()-bfs_start_time))
                screen_score(f"Time Left: {remaining}s",(255,255,0),700,40)

            gameWindow.blit(bgimg,(0,TOP_PANEL))

            # Draw BFS path visually
            if ai_mode=='bfs' and planned_path:
                for cell in planned_path[path_step_index:]:
                    cx, cy = grid_to_pix(cell[0], cell[1])
                    pygame.draw.rect(gameWindow,(173,216,230),(cx,cy,snake_size,snake_size))

            head=[snake_x,snake_y]
            snk_list.append(head)
            if len(snk_list)>snk_length:
                del snk_list[0]

            if head in snk_list[:-1]:
                game_over=True
                pygame.mixer.music.load('gameover.wav')
                pygame.mixer.music.play(-1)
                print("Game Over! Your score is:", score)

            if snake_x<0 or snake_x>screen_width-snake_size or snake_y<TOP_PANEL or snake_y>TOP_PANEL+GAME_HEIGHT-snake_size:
                game_over=True
                pygame.mixer.music.load('gameover.wav')
                pygame.mixer.music.play(-1)
                print("Game Over! Your score is:", score)

            plot_snake(gameWindow,(255,211,172),snk_list,snake_size)
            pygame.draw.rect(gameWindow,(0,0,0),[food_x,food_y,snake_size,snake_size])
            pygame.draw.rect(gameWindow,(255,0,0),[snake_x,snake_y,snake_size,snake_size])

        pygame.display.update()
        clock.tick(fps)

    pygame.quit()
    quit()

welcome()
gameLoop()






