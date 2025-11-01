import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLORS
from games import run_maze, run_puzzle, run_color_match, run_candy_crush

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game Hub")
    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: run_maze()
                if event.key == pygame.K_2: run_puzzle()
                if event.key == pygame.K_3: run_color_match()
                if event.key == pygame.K_4: run_candy_crush()

        screen.fill(COLORS["black"])
        menu_text = [
            "Press 1 - Maze",
            "Press 2 - Puzzle",
            "Press 3 - Color Match",
            "Press 4 - Candy Crush",
            "Press ESC to Quit"
        ]
        for i, line in enumerate(menu_text):
            label = font.render(line, True, COLORS["white"])
            screen.blit(label, (100, 100 + i * 60))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main_menu()
