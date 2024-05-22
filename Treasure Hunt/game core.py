
import pygame
import random

# Initialize pygame
pygame.init()

def initialize_game(grid_size):
    TILE_SIZE = 40
    WIDTH = 800
    HEIGHT = 600
     # Additional 100 pixels for the title and scoreboard
    BOARD_WIDTH = grid_size
    BOARD_HEIGHT = grid_size
    TREASURE_COUNT = max(5, grid_size)  # Adjust treasure count based on grid size

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GRAY = (192, 192, 192)

    # Load and scale treasure image
    treasure_img = pygame.image.load("treasure.png")
    treasure_img = pygame.transform.scale(treasure_img, (TILE_SIZE, TILE_SIZE))

    class Node:
        def __init__(self, x, y, value=None):
            self.x = x
            self.y = y
            self.value = value
            self.next = [None] * 16
            self.prev = [None] * 16

    class SkipList:
        def __init__(self):
            self.head = Node(-1, -1)
            self.levels = 1

        def insert(self, x, y):
            node = self.head
            new_nodes = []
            for i in range(self.levels):
                while node.next[i] and (node.next[i].x < x or (node.next[i].x == x and node.next[i].y < y)):
                    node = node.next[i]
                new_nodes.append(Node(x, y))
                if node.next[i] and node.next[i].x == x and node.next[i].y == y:
                    return False
                node = node.next[i]

            new_node = Node(x, y)
            for i in range(self.levels - 1, -1, -1):
                if not new_nodes[i]:
                    new_nodes[i] = new_node
                    new_node.next[i] = node.next[i] if node.next[i] else None
                    if node.next[i]:
                        node.next[i].prev[i] = new_node
                    node.next[i] = new_node
                    new_node.prev[i] = node
                else:
                    new_node.next[i] = new_nodes[i].next[i]
                    if new_nodes[i].next[i]:
                        new_nodes[i].next[i].prev[i] = new_node
                    new_nodes[i].next[i] = new_node
                    new_node.prev[i] = new_nodes[i]
            while len(new_nodes) < self.levels:
                new_nodes.append(None)
            if len(new_nodes) > self.levels:
                self.levels = len(new_nodes)
            return True

        def find(self, x, y):
            node = self.head
            for i in range(self.levels - 1, -1, -1):
                while node.next[i] and (node.next[i].x < x or (node.next[i].x == x and node.next[i].y < y)):
                    node = node.next[i]
                if node.next[i] and node.next[i].x == x and node.next[i].y == y:
                    return node.next[i]
            return None

        def remove(self, x, y):
            node = self.find(x, y)
            if not node:
                return False
            for i in range(self.levels - 1, -1, -1):
                if node.prev[i]:
                    node.prev[i].next[i] = node.next[i]
                if node.next[i]:
                    node.next[i].prev[i] = node.prev[i]
                if self.head.next[i] == node:
                    self.head.next[i] = node.next[i]
            while self.levels > 1 and not self.head.next[self.levels - 1]:
                self.levels -= 1
            return True


    class TreasureHunt:
        def __init__(self):
            self.board = [['.' for _ in range(BOARD_HEIGHT)] for _ in range(BOARD_WIDTH)]
            self.treasures = []
            self.player_treasures_found = 0
            self.ai_treasures_found = 0
            self.tiles_revealed = [[False for _ in range(BOARD_HEIGHT)] for _ in range(BOARD_WIDTH)]

        def place_treasure(self, x, y):
            self.treasures.append((x, y))
            self.board[x][y] = 'T'

        def is_valid_move(self, x, y):
            return 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT

        def move(self, x, y, player):
            if self.is_valid_move(x, y) and not self.tiles_revealed[x][y]:
                self.tiles_revealed[x][y] = True
                if self.board[x][y] == 'T':
                    if player == "Player":
                        self.player_treasures_found += 1
                    else:
                        self.ai_treasures_found += 1
                    print(f"{player} found a treasure at position: ({x}, {y})")
                else:
                    print(f"{player} did not find a treasure at position: ({x}, {y})")
                return True
            else:
                print(f"Invalid move by {player} at position: ({x}, {y})")
                return False

        def computer_move(self):
            if self.treasures:
                x, y = random.choice([(x, y) for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT) if not self.tiles_revealed[x][y]])
                self.move(x, y, "AI")

        def all_tiles_checked(self):
            return all(self.tiles_revealed[x][y] for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT))
        #def win(self):
        #    global player_treasures_found,ai_treasures_found

    def main():
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Treasure Hunt")
        clock = pygame.time.Clock()
        game = TreasureHunt()

        # Place treasures randomly on the board
        while len(game.treasures) < TREASURE_COUNT:
            x, y = random.randint(0, BOARD_WIDTH - 1), random.randint(0, BOARD_HEIGHT - 1)
            if game.board[x][y] != 'T':
                game.place_treasure(x, y)

        title_font = pygame.font.SysFont(None, 36)
        score_font = pygame.font.SysFont(None, 24)

        current_player = "Player"

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and current_player == "Player":
                    if pygame.mouse.get_pressed()[0]:
                        pos = pygame.mouse.get_pos()
                        x = pos[0] // TILE_SIZE
                        y = (pos[1] - 100) // TILE_SIZE
                        if game.move(x, y, "Player"):
                            current_player = "AI"

            if current_player == "AI":
                
                game.computer_move()
                current_player = "Player"

            if game.player_treasures_found + game.ai_treasures_found==5:
                print("Game over")
                running = False

            screen.fill(WHITE)
            title_text = title_font.render("Treasure Hunt", True, BLACK)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))

            player_text = score_font.render(f"Player Treasures: {game.player_treasures_found}", True, BLACK)
            ai_text = score_font.render(f"AI Treasures: {game.ai_treasures_found}", True, BLACK)
            screen.blit(player_text, (10, 50))
            screen.blit(ai_text, (WIDTH - 150, 50))

            for x in range(BOARD_WIDTH):
                for y in range(BOARD_HEIGHT):
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + 100, TILE_SIZE, TILE_SIZE)
                    if game.tiles_revealed[x][y]:
                        if game.board[x][y] == 'T':
                            screen.blit(treasure_img, (x * TILE_SIZE, y * TILE_SIZE + 100))
                        else:
                            pygame.draw.rect(screen, GRAY, rect)
                    else:
                        pygame.draw.rect(screen, BLACK, rect, 1)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    main()

# Main section
if __name__ == "__main__":
    while True:
        try:
            grid_size = int(input("Enter the grid size you want to play on (e.g., 4 for 4x4): "))
            if 3 <= grid_size <= 10:
                break
            else:
                print("Please enter a grid size between 3 and 10.")
        except ValueError:
            print("Please enter a valid integer.")
    
    initialize_game(grid_size)
