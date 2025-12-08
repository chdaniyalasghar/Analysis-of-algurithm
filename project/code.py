import pygame
import random
import math
import time
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
PURPLE = (255, 50, 255)
CYAN = (50, 255, 255)
ORANGE = (255, 150, 50)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

class AlgorithmMode(Enum):
    RANDOMIZED = 1
    DETERMINISTIC = 2

class Racer:
    def __init__(self, name, color, base_speed, acceleration, handling):
        self.name = name
        self.color = color
        self.base_speed = base_speed
        self.acceleration = acceleration
        self.handling = handling
        self.position = 0
        self.x = 100
        self.y = 0
        self.speed = 0
        self.lane = 0
        self.finished = False
        self.finish_time = 0
        self.power_active = False
        self.power_timer = 0
        self.sort_value = self.calculate_sort_value()
        
    def calculate_sort_value(self):
        """Calculate a value used for sorting (combination of attributes)"""
        return self.base_speed * 0.5 + self.acceleration * 0.3 + self.handling * 0.2
    
    def update(self, dt, boost_factor=1.0):
        """Update racer position"""
        if not self.finished:
            # Apply acceleration
            self.speed += self.acceleration * dt * boost_factor
            self.speed = min(self.speed, self.base_speed * boost_factor)
            
            # Update position
            self.position += self.speed * dt
            
            # Apply handling (small random variations)
            if random.random() > self.handling / 100:
                self.speed *= 0.95
            
            # Update x position based on position
            self.x = 100 + self.position * 2
            
            # Check if finished
            if self.x >= SCREEN_WIDTH - 150:
                self.finished = True
                self.x = SCREEN_WIDTH - 150
    
    def activate_power(self):
        """Activate special power (for median racer)"""
        self.power_active = True
        self.power_timer = 3.0  # 3 seconds of power

class RaceSorterGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Race Sorter - Algorithm Racing Game")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        
        self.running = True
        self.racing = False
        self.race_complete = False
        self.algorithm_mode = AlgorithmMode.RANDOMIZED
        self.show_comparison = False
        
        self.racers = []
        self.finish_order = []
        self.race_start_time = 0
        self.sort_operations = 0
        self.pivot_highlights = []
        
        self.init_racers()
        
    def init_racers(self):
        """Initialize racers with different attributes"""
        names = ["Flash", "Turbo", "Nitro", "Blaze", "Storm", "Rocket"]
        colors = [RED, BLUE, GREEN, YELLOW, PURPLE, CYAN]
        
        self.racers = []
        for i in range(6):
            base_speed = random.uniform(80, 120)
            acceleration = random.uniform(20, 40)
            handling = random.uniform(60, 95)
            
            racer = Racer(names[i], colors[i], base_speed, acceleration, handling)
            racer.y = 200 + i * 60
            racer.lane = i
            self.racers.append(racer)
    
    def quicksort_randomized(self, arr, low, high):
        """Randomized QuickSort implementation"""
        if low < high:
            # Random pivot selection
            pivot_index = random.randint(low, high)
            self.pivot_highlights.append(pivot_index)
            self.sort_operations += 1
            
            arr[low], arr[pivot_index] = arr[pivot_index], arr[low]
            
            pi = self.partition(arr, low, high)
            self.quicksort_randomized(arr, low, pi - 1)
            self.quicksort_randomized(arr, pi + 1, high)
    
    def quicksort_deterministic(self, arr, low, high):
        """Deterministic QuickSort (always picks last element as pivot)"""
        if low < high:
            # Deterministic pivot selection (last element)
            pivot_index = high
            self.pivot_highlights.append(pivot_index)
            self.sort_operations += 1
            
            pi = self.partition(arr, low, high)
            self.quicksort_deterministic(arr, low, pi - 1)
            self.quicksort_deterministic(arr, pi + 1, high)
    
    def partition(self, arr, low, high):
        """Partition function for QuickSort"""
        pivot = arr[high].sort_value
        i = low - 1
        
        for j in range(low, high):
            if arr[j].sort_value <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                # Swap lanes for visual effect
                arr[i].lane, arr[j].lane = arr[j].lane, arr[i].lane
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        arr[i + 1].lane, arr[high].lane = arr[high].lane, arr[i + 1].lane
        
        return i + 1
    
    def find_median(self, arr):
        """Find median using order statistics (simplified)"""
        sorted_by_value = sorted(arr, key=lambda r: r.sort_value)
        median_index = len(sorted_by_value) // 2
        return sorted_by_value[median_index]
    
    def start_race(self):
        """Start the race with sorting"""
        self.racing = True
        self.race_complete = False
        self.finish_order = []
        self.race_start_time = time.time()
        self.sort_operations = 0
        self.pivot_highlights = []
        
        # Reset racers
        for racer in self.racers:
            racer.position = 0
            racer.x = 100
            racer.speed = 0
            racer.finished = False
            racer.finish_time = 0
            racer.power_active = False
            racer.power_timer = 0
        
        # Apply sorting based on algorithm mode
        if self.algorithm_mode == AlgorithmMode.RANDOMIZED:
            self.quicksort_randomized(self.racers, 0, len(self.racers) - 1)
        else:
            self.quicksort_deterministic(self.racers, 0, len(self.racers) - 1)
        
        # Update y positions based on new order
        for i, racer in enumerate(self.racers):
            racer.y = 200 + i * 60
        
        # Find median racer and give them special power
        median_racer = self.find_median(self.racers)
        median_racer.activate_power()
    
    def update(self, dt):
        """Update game state"""
        if self.racing and not self.race_complete:
            all_finished = True
            
            for racer in self.racers:
                # Apply power boost if active
                boost = 1.5 if racer.power_active else 1.0
                
                racer.update(dt, boost)
                
                if racer.power_active:
                    racer.power_timer -= dt
                    if racer.power_timer <= 0:
                        racer.power_active = False
                
                if racer.finished and racer not in self.finish_order:
                    racer.finish_time = time.time() - self.race_start_time
                    self.finish_order.append(racer)
                
                if not racer.finished:
                    all_finished = False
            
            if all_finished:
                self.race_complete = True
    
    def draw_track(self):
        """Draw the racing track"""
        # Track background
        pygame.draw.rect(self.screen, DARK_GRAY, (80, 180, SCREEN_WIDTH - 160, 400))
        
        # Lanes
        for i in range(7):
            y = 200 + i * 60
            pygame.draw.line(self.screen, WHITE, (80, y), (SCREEN_WIDTH - 80, y), 2)
        
        # Start line
        pygame.draw.line(self.screen, GREEN, (100, 180), (100, 580), 4)
        
        # Finish line
        pygame.draw.line(self.screen, RED, (SCREEN_WIDTH - 150, 180), (SCREEN_WIDTH - 150, 580), 4)
        
        # Checkered pattern at finish
        for i in range(10):
            for j in range(8):
                x = SCREEN_WIDTH - 150 + i * 10
                y = 180 + j * 25
                color = WHITE if (i + j) % 2 == 0 else BLACK
                pygame.draw.rect(self.screen, color, (x, y, 10, 25))
    
    def draw_racers(self):
        """Draw all racers"""
        for i, racer in enumerate(self.racers):
            # Draw racer car
            car_rect = pygame.Rect(racer.x - 20, racer.y - 15, 40, 30)
            
            # Highlight if pivot was used
            if i in self.pivot_highlights:
                pygame.draw.rect(self.screen, YELLOW, car_rect.inflate(10, 10), 3)
            
            # Draw car
            pygame.draw.rect(self.screen, racer.color, car_rect)
            pygame.draw.rect(self.screen, BLACK, car_rect, 2)
            
            # Power effect
            if racer.power_active:
                for j in range(3):
                    offset = (j + 1) * 5
                    alpha = 100 - j * 30
                    power_rect = car_rect.inflate(offset * 2, offset * 2)
                    pygame.draw.rect(self.screen, (*racer.color, alpha), power_rect, 2)
            
            # Draw name and stats
            name_text = self.font_small.render(racer.name, True, WHITE)
            self.screen.blit(name_text, (racer.x - 25, racer.y - 40))
            
            # Draw speed indicator
            speed_text = self.font_small.render(f"{int(racer.speed)}", True, WHITE)
            self.screen.blit(speed_text, (racer.x - 10, racer.y + 20))
    
    def draw_ui(self):
        """Draw UI elements"""
        # Title
        title = self.font_large.render("RACE SORTER", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Algorithm mode
        mode_text = f"Mode: {'Randomized QuickSort' if self.algorithm_mode == AlgorithmMode.RANDOMIZED else 'Deterministic QuickSort'}"
        mode_surface = self.font_medium.render(mode_text, True, GREEN if self.algorithm_mode == AlgorithmMode.RANDOMIZED else ORANGE)
        self.screen.blit(mode_surface, (50, 80))
        
        # Sort operations counter
        ops_text = f"Sort Operations: {self.sort_operations}"
        ops_surface = self.font_small.render(ops_text, True, WHITE)
        self.screen.blit(ops_surface, (50, 120))
        
        # Instructions
        if not self.racing:
            inst_text = "Press SPACE to start race | R for Randomized | D for Deterministic | C for Comparison"
            inst_surface = self.font_small.render(inst_text, True, LIGHT_GRAY)
            self.screen.blit(inst_surface, (SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT - 30))
        
        # Finish order
        if self.finish_order:
            order_text = "Finish Order:"
            order_surface = self.font_medium.render(order_text, True, WHITE)
            self.screen.blit(order_surface, (SCREEN_WIDTH - 300, 100))
            
            for i, racer in enumerate(self.finish_order):
                pos_text = f"{i+1}. {racer.name} ({racer.finish_time:.2f}s)"
                pos_surface = self.font_small.render(pos_text, True, racer.color)
                self.screen.blit(pos_surface, (SCREEN_WIDTH - 300, 140 + i * 25))
        
        # Legend
        legend_y = 600
        legend_items = [
            ("Attributes: Speed | Accel | Handling", WHITE),
            ("Yellow border: Pivot selection", YELLOW),
            ("Glowing: Median racer power", CYAN)
        ]
        
        for i, (text, color) in enumerate(legend_items):
            surface = self.font_small.render(text, True, color)
            self.screen.blit(surface, (50 + i * 350, legend_y))
    
    def draw_comparison(self):
        """Draw algorithm comparison screen"""
        self.screen.fill(BLACK)
        
        title = self.font_large.render("Algorithm Performance Comparison", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Comparison data
        comparisons = [
            ("Randomized QuickSort", "O(n log n) average", "Unpredictable pivots", "Better worst-case"),
            ("Deterministic QuickSort", "O(n log n) average", "Fixed pivot (last)", "O(n²) worst-case")
        ]
        
        for i, (name, complexity, pivot, worst) in enumerate(comparisons):
            y = 150 + i * 200
            
            # Box
            pygame.draw.rect(self.screen, DARK_GRAY, (100, y, SCREEN_WIDTH - 200, 150))
            pygame.draw.rect(self.screen, GREEN if i == 0 else ORANGE, (100, y, SCREEN_WIDTH - 200, 150), 3)
            
            # Text
            name_surface = self.font_medium.render(name, True, WHITE)
            self.screen.blit(name_surface, (120, y + 10))
            
            comp_surface = self.font_small.render(f"Complexity: {complexity}", True, WHITE)
            self.screen.blit(comp_surface, (120, y + 50))
            
            pivot_surface = self.font_small.render(f"Pivot: {pivot}", True, WHITE)
            self.screen.blit(pivot_surface, (120, y + 80))
            
            worst_surface = self.font_small.render(f"Worst Case: {worst}", True, WHITE)
            self.screen.blit(worst_surface, (120, y + 110))
        
        # Instructions
        inst_text = "Press ESC to return to game"
        inst_surface = self.font_small.render(inst_text, True, LIGHT_GRAY)
        inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(inst_surface, inst_rect)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.show_comparison:
                        self.show_comparison = False
                    else:
                        self.running = False
                
                elif event.key == pygame.K_SPACE and not self.racing:
                    self.start_race()
                
                elif event.key == pygame.K_r:
                    self.algorithm_mode = AlgorithmMode.RANDOMIZED
                    self.init_racers()
                
                elif event.key == pygame.K_d:
                    self.algorithm_mode = AlgorithmMode.DETERMINISTIC
                    self.init_racers()
                
                elif event.key == pygame.K_c:
                    self.show_comparison = True
                
                elif event.key == pygame.K_RETURN and self.race_complete:
                    self.racing = False
                    self.race_complete = False
                    self.init_racers()
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            
            if not self.show_comparison:
                self.update(dt)
                
                # Draw everything
                self.screen.fill(BLACK)
                self.draw_track()
                self.draw_racers()
                self.draw_ui()
                
                # Race complete message
                if self.race_complete:
                    complete_text = "Race Complete! Press ENTER to race again"
                    complete_surface = self.font_medium.render(complete_text, True, GREEN)
                    complete_rect = complete_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
                    self.screen.blit(complete_surface, complete_rect)
            else:
                self.draw_comparison()
            
            pygame.display.flip()
        
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = RaceSorterGame()
    game.run()