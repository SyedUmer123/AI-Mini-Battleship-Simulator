import pygame
import numpy as np
import random
import sys
from typing import Tuple, List

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = 5
CELL_SIZE = 80
MARGIN = 50
SHIPS = [3, 2]  # Ship sizes
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE * 2 + MARGIN * 3
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + MARGIN * 2
COLORS = {
    'background': (28, 40, 51),
    'grid': (231, 76, 60),
    'water': (41, 128, 185),
    'ship': (44, 62, 80),
    'hit': (231, 76, 60),
    'miss': (149, 165, 166),
    'text': (255, 255, 255)
}

class BattleshipGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Mini Battleship")
        self.font = pygame.font.SysFont('Arial', 24)
        self.reset_game()
        
    def reset_game(self):
        """Initialize or reset game state"""
        self.player_grid = np.zeros((GRID_SIZE, GRID_SIZE))
        self.ai_grid = np.zeros((GRID_SIZE, GRID_SIZE))
        self.player_ships = []
        self.ai_ships = self.place_ships()
        self.ai_probability = np.ones((GRID_SIZE, GRID_SIZE))
        self.player_turn = True
        self.game_over = False
        self.winner = None
        self.message = "Place your ships! Click on your grid."
        self.placing_ships = True
        self.current_ship_index = 0
        self.current_orientation = 'h'  # 'h' or 'v'
        
    def place_ships(self) -> List[Tuple[int, int, int, str]]:
        """Randomly place ships for AI"""
        ships = []
        grid = np.zeros((GRID_SIZE, GRID_SIZE))
        
        for size in SHIPS:
            placed = False
            while not placed:
                orientation = random.choice(['h', 'v'])
                if orientation == 'h':
                    x = random.randint(0, GRID_SIZE-1)
                    y = random.randint(0, GRID_SIZE-size)
                    if np.all(grid[x, y:y+size] == 0):
                        grid[x, y:y+size] = 1
                        ships.append((x, y, size, orientation))
                        placed = True
                else:
                    x = random.randint(0, GRID_SIZE-size)
                    y = random.randint(0, GRID_SIZE-1)
                    if np.all(grid[x:x+size, y] == 0):
                        grid[x:x+size, y] = 1
                        ships.append((x, y, size, orientation))
                        placed = True
        return ships
    
    def draw_grid(self, grid: np.ndarray, offset_x: int, show_ships: bool):
        """Draw a battleship grid"""
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(
                    offset_x + y * CELL_SIZE,
                    MARGIN + x * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                # Determine cell color
                if grid[x, y] == 0:  # Empty
                    color = COLORS['water']
                elif grid[x, y] == 1:  # Ship (if showing)
                    color = COLORS['ship'] if show_ships else COLORS['water']
                elif grid[x, y] == 2:  # Hit
                    color = COLORS['hit']
                elif grid[x, y] == 3:  # Miss
                    color = COLORS['miss']
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLORS['grid'], rect, 1)
    
    def draw_ship_placement(self, x: int, y: int):
        """Show ship being placed by player"""
        size = SHIPS[self.current_ship_index]
        if self.current_orientation == 'h':
            for i in range(size):
                if y + i < GRID_SIZE:
                    rect = pygame.Rect(
                        MARGIN + (y + i) * CELL_SIZE,
                        MARGIN + x * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, (100, 100, 100), rect)
        else:
            for i in range(size):
                if x + i < GRID_SIZE:
                    rect = pygame.Rect(
                        MARGIN + y * CELL_SIZE,
                        MARGIN + (x + i) * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, (100, 100, 100), rect)
    
    def place_player_ship(self, x: int, y: int):
        """Place player's ship on the grid"""
        size = SHIPS[self.current_ship_index]
        
        # Check if placement is valid
        if self.current_orientation == 'h':
            if y + size > GRID_SIZE:
                return False
            if np.any(self.player_grid[x, y:y+size] != 0):
                return False
            self.player_grid[x, y:y+size] = 1
        else:
            if x + size > GRID_SIZE:
                return False
            if np.any(self.player_grid[x:x+size, y] != 0):
                return False
            self.player_grid[x:x+size, y] = 1
        
        self.player_ships.append((x, y, size, self.current_orientation))
        self.current_ship_index += 1
        if self.current_ship_index >= len(SHIPS):
            self.placing_ships = False
            self.message = "Your turn! Click on the right grid to attack."
        return True
    
    def player_attack(self, x: int, y: int):
        """Player attacks AI's grid"""
        if self.ai_grid[x, y] in [2, 3]:  # Already attacked
            return False
        
        if self.ai_ship_at(x, y):
            self.ai_grid[x, y] = 2  # Hit
            self.message = "Hit! Your turn again."
            if self.check_ai_ships_sunk():
                self.game_over = True
                self.winner = "Player"
            return True
        else:
            self.ai_grid[x, y] = 3  # Miss
            self.message = "Miss! AI's turn."
            self.player_turn = False
            return True
    
    def ai_ship_at(self, x: int, y: int) -> bool:
        """Check if AI has a ship at given coordinates"""
        for ship in self.ai_ships:
            sx, sy, size, orientation = ship
            if orientation == 'h':
                if x == sx and sy <= y < sy + size:
                    return True
            else:
                if y == sy and sx <= x < sx + size:
                    return True
        return False
    
    def check_ai_ships_sunk(self) -> bool:
        """Check if all AI ships are sunk"""
        for ship in self.ai_ships:
            sx, sy, size, orientation = ship
            sunk = True
            if orientation == 'h':
                for y in range(sy, sy + size):
                    if self.ai_grid[sx, y] != 2:
                        sunk = False
                        break
            else:
                for x in range(sx, sx + size):
                    if self.ai_grid[x, sy] != 2:
                        sunk = False
                        break
            if not sunk:
                return False
        return True
    
    def check_player_ships_sunk(self) -> bool:
        """Check if all player ships are sunk"""
        for ship in self.player_ships:
            sx, sy, size, orientation = ship
            sunk = True
            if orientation == 'h':
                for y in range(sy, sy + size):
                    if self.player_grid[sx, y] != 2:
                        sunk = False
                        break
            else:
                for x in range(sx, sx + size):
                    if self.player_grid[x, sy] != 2:
                        sunk = False
                        break
            if not sunk:
                return False
        return True
    
    def ai_turn(self):
        """AI makes a move using probability-based strategy"""
        pygame.time.delay(500)  # Small delay for better UX
        
        # Find all possible moves (cells not yet attacked)
        possible_moves = np.where(self.player_grid == 0)
        if len(possible_moves[0]) == 0:
            return
        
        # If there are hits, target around them
        hits = np.where(self.player_grid == 2)
        if len(hits[0]) > 0:
            # Find all adjacent cells to hits
            candidates = []
            for x, y in zip(*hits):
                for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE 
                        and self.player_grid[nx, ny] == 0):
                        candidates.append((nx, ny))
            
            if candidates:
                # Choose random adjacent cell
                x, y = random.choice(candidates)
                self.make_ai_move(x, y)
                return
        
        # No adjacent hits, use probability density
        flat_prob = self.ai_probability.flatten()
        if np.sum(flat_prob) == 0:
            # All cells have zero probability (shouldn't happen)
            flat_prob = np.ones_like(flat_prob)
        
        # Choose move based on probability
        move = np.random.choice(np.arange(len(flat_prob)), p=flat_prob/np.sum(flat_prob))
        x, y = np.unravel_index(move, self.ai_probability.shape)
        self.make_ai_move(x, y)
    
    def make_ai_move(self, x: int, y: int):
        """Execute AI's move and update probabilities"""
        if self.player_grid[x, y] == 1:  # Hit player's ship
            self.player_grid[x, y] = 2
            self.message = "AI hit your ship! Its turn again."
            
            # Increase probability around hits
            for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    self.ai_probability[nx, ny] *= 2
            
            if self.check_player_ships_sunk():
                self.game_over = True
                self.winner = "AI"
            else:
                # AI gets another turn after hit
                self.ai_turn()
        else:
            self.player_grid[x, y] = 3  # Miss
            self.message = "AI missed! Your turn."
            self.player_turn = True
        
        # Set this cell's probability to zero (already attacked)
        self.ai_probability[x, y] = 0
    
    def draw_text(self):
        """Draw game text and messages"""
        # Player/AI labels
        player_label = self.font.render("Your Fleet", True, COLORS['text'])
        ai_label = self.font.render("Enemy Waters", True, COLORS['text'])
        self.screen.blit(player_label, (MARGIN, 10))
        self.screen.blit(ai_label, (MARGIN * 2 + GRID_SIZE * CELL_SIZE, 10))
        
        # Game message
        msg = self.font.render(self.message, True, COLORS['text'])
        self.screen.blit(msg, (MARGIN, MARGIN + GRID_SIZE * CELL_SIZE + 10))
        
        # Game over message
        if self.game_over:
            result = self.font.render(f"{self.winner} wins! Press R to restart.", True, COLORS['text'])
            self.screen.blit(result, (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT - 30))
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse clicks"""
        if self.game_over:
            return
        
        x, y = pos
        # Player placing ships
        if self.placing_ships:
            # Check if click is within player grid
            if (MARGIN <= x < MARGIN + GRID_SIZE * CELL_SIZE and
                MARGIN <= y < MARGIN + GRID_SIZE * CELL_SIZE):
                grid_x = (y - MARGIN) // CELL_SIZE
                grid_y = (x - MARGIN) // CELL_SIZE
                if self.place_player_ship(grid_x, grid_y):
                    self.message = f"Place your {SHIPS[self.current_ship_index]} length ship (R to rotate)" if self.current_ship_index < len(SHIPS) else ""
        
        # Player attacking
        elif self.player_turn:
            # Check if click is within AI grid
            if (MARGIN * 2 + GRID_SIZE * CELL_SIZE <= x < MARGIN * 2 + GRID_SIZE * CELL_SIZE * 2 and
                MARGIN <= y < MARGIN + GRID_SIZE * CELL_SIZE):
                grid_x = (y - MARGIN) // CELL_SIZE
                grid_y = (x - MARGIN * 2 - GRID_SIZE * CELL_SIZE) // CELL_SIZE
                self.player_attack(grid_x, grid_y)
                
                # If player missed, AI takes turn
                if not self.player_turn and not self.game_over:
                    pygame.time.delay(1000)  # Pause for player to see result
                    self.ai_turn()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset game
                        self.reset_game()
                    elif event.key == pygame.K_o and self.placing_ships:  # Rotate ship
                        self.current_orientation = 'v' if self.current_orientation == 'h' else 'h'
            
            # Draw everything
            self.screen.fill(COLORS['background'])
            
            # Draw player grid (show ships during placement)
            self.draw_grid(self.player_grid, MARGIN, self.placing_ships or self.game_over)
            
            # Draw AI grid (never show ships)
            self.draw_grid(self.ai_grid, MARGIN * 2 + GRID_SIZE * CELL_SIZE, False)
            
            # Draw ship being placed
            if self.placing_ships and self.current_ship_index < len(SHIPS):
                if pygame.mouse.get_focused():
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if (MARGIN <= mouse_x < MARGIN + GRID_SIZE * CELL_SIZE and
                        MARGIN <= mouse_y < MARGIN + GRID_SIZE * CELL_SIZE):
                        grid_x = (mouse_y - MARGIN) // CELL_SIZE
                        grid_y = (mouse_x - MARGIN) // CELL_SIZE
                        self.draw_ship_placement(grid_x, grid_y)
            
            self.draw_text()
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = BattleshipGame()
    game.run()