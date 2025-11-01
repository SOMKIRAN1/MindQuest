from random import *
from turtle import *
from freegames import floor , vector


tiles = {}
neighbors = [vector(100,0),vector(-100,0), vector(0,100),  vector(0,-100)]
def load():
    # load tiles and set up grid
    count = 1 
    for y in range (-200 , 200 ,100):
        for x in range (-200 , 200 , 100):
            mark = vector(x,y)
            tiles[mark] = count
            count = count + 1
    tiles[mark]=None     

    for count in range(1000):      # shuffle the tiles
        neighbor = choice(neighbors)
        spot = mark + neighbor
        if spot in tiles:
            number = tiles[spot]   
            tiles[spot]=None
            tiles[mark]=number
            mark = spot

def square (mark , number):
    #draw square with number
    up()
    goto(mark.x , mark.y)
    down()
    color("#5E095E", "#FFC4FB")
    begin_fill()
    for count in range(4):
        forward(99)
        left(90)
    end_fill()
    if number is None:
        return
    elif number < 10:
        forward(20)

    write(number , font = ("Arial" , 60 , "normal"))  

def tap (x,y):
    # swap tiles 
    x = floor(x , 100)
    y = floor(y , 100)
    mark = vector(x,y)
    for neighbor in neighbors:
        spot = mark + neighbor
        if spot in tiles and tiles[spot] is None:
            number = tiles[mark]
            tiles[spot]=number
            square(spot , number)
            tiles[mark]=None
            square(mark , None) # make space 
def draw():
    for mark in tiles :
        square(mark , tiles[mark])
    update()

setup (412,400,440,390)
title("Maze Game")
# circle (20)
bgcolor("purple")
hideturtle()
tracer (False)

load()

draw()
onscreenclick (tap)
done()



# from random import *
# from turtle import *
# from freegames import floor, vector
# import heapq
# import time

# # Global variables
# tiles = {}
# neighbors = [vector(100,0), vector(-100,0), vector(0,100), vector(0,-100)]
# solving = False
# solution_path = []
# current_step = 0

# def load():
#     # load tiles and set up grid
#     count = 1 
#     for y in range(-200, 200, 100):
#         for x in range(-200, 200, 100):
#             mark = vector(x, y)
#             tiles[mark] = count
#             count += 1
#     tiles[mark] = None     

#     # Shuffle the tiles
#     for _ in range(1000):
#         neighbor = choice(neighbors)
#         spot = mark + neighbor
#         if spot in tiles:
#             number = tiles[spot]   
#             tiles[spot] = None
#             tiles[mark] = number
#             mark = spot

# def square(mark, number):
#     # draw square with number
#     up()
#     goto(mark.x, mark.y)
#     down()
    
#     # Color empty tile differently
#     if number is None:
#         color("#5E095E", "#5E095E")
#     else:
#         color("#5E095E", "#FFC4FB")
        
#     begin_fill()
#     for _ in range(4):
#         forward(99)
#         left(90)
#     end_fill()
    
#     if number is None:
#         return
#     elif number < 10:
#         up()
#         goto(mark.x + 35, mark.y + 20)
#         down()
#     else:
#         up()
#         goto(mark.x + 20, mark.y + 20)
#         down()
        
#     color("white")
#     write(number, font=("Arial", 60, "normal"))

# def draw_button():
#     # Draw help button at the top
#     up()
#     goto(-180, 220)
#     down()
#     color("#5E095E", "#FFC4FB")
#     begin_fill()
#     for _ in range(2):
#         forward(360)
#         right(90)
#         forward(50)
#         right(90)
#     end_fill()
    
#     up()
#     goto(0, 200)
#     down()
#     color("#5E095E")
#     write("HELP - Solve Puzzle", align="center", font=("Arial", 20, "bold"))

# def draw():
#     # Clear the screen first
#     clear()
    
#     # Draw the game title
#     up()
#     goto(0, 260)
#     down()
#     color("white")
#     write("Maze Game", align="center", font=("Arial", 24, "bold"))
    
#     # Draw the help button
#     draw_button()
    
#     # Draw all tiles
#     for mark in tiles:
#         square(mark, tiles[mark])
#     update()

# def tap(x, y):
#     global solving, solution_path, current_step
    
#     # Check if help button was clicked
#     if 220 <= y <= 270 and -180 <= x <= 180:
#         solving = True
#         solution_path = solve_puzzle()
#         if solution_path:
#             current_step = 0
#             animate_solution()
#         else:
#             solving = False
#         return
    
#     # If currently solving, ignore tile taps
#     if solving:
#         return
        
#     # Swap tiles (original functionality)
#     x = floor(x, 100)
#     y = floor(y, 100)
#     mark = vector(x, y)
    
#     # Check if clicked position is a valid tile
#     if mark not in tiles:
#         return
        
#     for neighbor in neighbors:
#         spot = mark + neighbor
#         if spot in tiles and tiles[spot] is None:
#             number = tiles[mark]
#             tiles[spot] = number
#             square(spot, number)
#             tiles[mark] = None
#             square(mark, None)
#             break

# def get_goal_state():
#     """Return the solved state of the puzzle"""
#     goal = {}
#     count = 1
#     for y in range(-200, 200, 100):
#         for x in range(-200, 200, 100):
#             goal[vector(x, y)] = count
#             count += 1
#     goal[vector(100, 100)] = None  # Last tile is empty
#     return goal

# def state_to_tuple(state):
#     """Convert state to hashable tuple"""
#     positions = []
#     for y in range(-200, 200, 100):
#         for x in range(-200, 200, 100):
#             positions.append(state[vector(x, y)])
#     return tuple(positions)

# def heuristic(state):
#     """Manhattan distance heuristic"""
#     distance = 0
#     goal_positions = {}
    
#     # Create mapping of number to goal position
#     count = 1
#     for y in range(-200, 200, 100):
#         for x in range(-200, 200, 100):
#             if count < 16:
#                 goal_positions[count] = vector(x, y)
#             count += 1
    
#     # Calculate Manhattan distance for each tile
#     for pos, num in state.items():
#         if num is not None and num in goal_positions:
#             goal_pos = goal_positions[num]
#             distance += abs(pos.x - goal_pos.x) + abs(pos.y - goal_pos.y)
    
#     return distance

# def get_neighbors(state):
#     """Get all possible next states from current state"""
#     neighbors_list = []
    
#     # Find empty tile
#     empty_pos = None
#     for pos, num in state.items():
#         if num is None:
#             empty_pos = pos
#             break
    
#     if empty_pos is None:
#         return neighbors_list
    
#     # Try moving each adjacent tile into empty space
#     for move in [vector(100, 0), vector(-100, 0), vector(0, 100), vector(0, -100)]:
#         tile_pos = empty_pos + move
        
#         if tile_pos in state:
#             # Create new state by swapping
#             new_state = state.copy()
#             new_state[empty_pos] = new_state[tile_pos]
#             new_state[tile_pos] = None
#             neighbors_list.append((tile_pos, new_state))
    
#     return neighbors_list

# def solve_puzzle():
#     """Solve the puzzle using A* algorithm"""
#     start_state = tiles.copy()
#     goal_state = get_goal_state()
    
#     # Priority queue: (f_score, g_score, state, path)
#     open_set = []
#     start_tuple = state_to_tuple(start_state)
#     heapq.heappush(open_set, (heuristic(start_state), 0, start_state, []))
    
#     # Keep track of visited states and their g_scores
#     g_scores = {start_tuple: 0}
#     came_from = {}
    
#     while open_set:
#         current_f, current_g, current_state, current_path = heapq.heappop(open_set)
#         current_tuple = state_to_tuple(current_state)
        
#         # Check if we've reached the goal
#         if current_state == goal_state:
#             return current_path
        
#         # Skip if we found a better path to this state
#         if current_tuple in g_scores and current_g > g_scores[current_tuple]:
#             continue
        
#         # Explore neighbors
#         for move_pos, neighbor_state in get_neighbors(current_state):
#             neighbor_tuple = state_to_tuple(neighbor_state)
#             tentative_g = current_g + 1
            
#             # If this path to neighbor is better than any previous one
#             if neighbor_tuple not in g_scores or tentative_g < g_scores[neighbor_tuple]:
#                 g_scores[neighbor_tuple] = tentative_g
#                 f_score = tentative_g + heuristic(neighbor_state)
#                 new_path = current_path + [move_pos]
#                 heapq.heappush(open_set, (f_score, tentative_g, neighbor_state, new_path))
    
#     return []  # No solution found

# def animate_solution():
#     global solving, solution_path, current_step
    
#     if current_step < len(solution_path):
#         # Get the position to move
#         pos = solution_path[current_step]
        
#         # Find the empty tile
#         empty_tile = None
#         for tile_pos, value in tiles.items():
#             if value is None:
#                 empty_tile = tile_pos
#                 break
        
#         # Swap the tiles
#         if empty_tile:
#             number = tiles[pos]
#             tiles[empty_tile] = number
#             tiles[pos] = None
            
#             # Redraw
#             draw()
            
#             current_step += 1
            
#             # Schedule next step
#             ontimer(animate_solution, 500)  # 500ms delay between moves
#     else:
#         solving = False
#         # Check if puzzle is solved
#         goal_state = get_goal_state()
#         if tiles == goal_state:
#             up()
#             goto(0, 150)
#             down()
#             color("green")
#             write("Puzzle Solved!", align="center", font=("Arial", 20, "bold"))

# # Setup the game
# setup(412, 500, 440, 390)  # Increased window height to accommodate top space
# title("Maze Game with Help")
# bgcolor("purple")
# hideturtle()
# tracer(False)

# load()
# draw()
# onscreenclick(tap)
# done()