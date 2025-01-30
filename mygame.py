import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouse Chase - Try to catch K!")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Character properties
CHAR_SIZE = 30
PLAYER_SPEED = 8  # Increased for smoother mouse following
K_SPEED = 7

class Character:
    def __init__(self, x, y, color, letter):
        self.x = x
        self.y = y
        self.color = color
        self.letter = letter
        self.font = pygame.font.Font(None, 36)
        self.last_positions = [(x, y)] * 5
        
    def draw(self, screen):
        # Draw trail effect
        for i, pos in enumerate(self.last_positions):
            alpha = int(255 * (i / len(self.last_positions)))
            s = pygame.Surface((CHAR_SIZE * 2, CHAR_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), (CHAR_SIZE, CHAR_SIZE), CHAR_SIZE)
            screen.blit(s, (pos[0] - CHAR_SIZE, pos[1] - CHAR_SIZE))
            
        # Draw current position
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), CHAR_SIZE)
        text = self.font.render(self.letter, True, WHITE)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)

class Player(Character):
    def move(self, target_x, target_y):
        # Calculate direction to mouse
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:  # Only move if mouse is far enough
            # Normalize movement
            dx = dx / distance * PLAYER_SPEED
            dy = dy / distance * PLAYER_SPEED
            
            # Update position
            self.x += dx
            self.y += dy
            
            # Keep within bounds
            self.x = max(CHAR_SIZE, min(WIDTH - CHAR_SIZE, self.x))
            self.y = max(CHAR_SIZE, min(HEIGHT - CHAR_SIZE, self.y))
            
            # Update trail
            self.last_positions = self.last_positions[1:] + [(self.x, self.y)]

class SmartCharacter(Character):
    def __init__(self, x, y, color, letter):
        super().__init__(x, y, color, letter)
        self.corner_awareness = 150
        
    def move(self, player):
        distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        safe_distance = 200
        
        if distance < safe_distance:
            # Predict player's next position
            next_player_x = player.x
            next_player_y = player.y
            
            # Calculate angle to player
            angle = math.atan2(next_player_y - self.y, next_player_x - self.x)
            
            # Base movement direction (away from player)
            target_x = self.x - math.cos(angle) * K_SPEED
            target_y = self.y - math.sin(angle) * K_SPEED
            
            # Corner avoidance logic
            corner_force_x = 0
            corner_force_y = 0
            
            # Detect proximity to walls
            if self.x < self.corner_awareness:
                corner_force_x += K_SPEED
            if self.x > WIDTH - self.corner_awareness:
                corner_force_x -= K_SPEED
            if self.y < self.corner_awareness:
                corner_force_y += K_SPEED
            if self.y > HEIGHT - self.corner_awareness:
                corner_force_y -= K_SPEED
                
            # Apply corner avoidance forces
            target_x += corner_force_x
            target_y += corner_force_y
            
            # Additional escape logic when very close
            if distance < 100:
                escape_multiplier = 1.5
                target_x = self.x + (target_x - self.x) * escape_multiplier
                target_y = self.y + (target_y - self.y) * escape_multiplier
            
            # Ensure K stays within bounds
            margin = CHAR_SIZE + 10
            self.x = max(margin, min(WIDTH - margin, target_x))
            self.y = max(margin, min(HEIGHT - margin, target_y))
            
            # Emergency escape to center if cornered
            if ((self.x < margin * 2 and self.y < margin * 2) or
                (self.x < margin * 2 and self.y > HEIGHT - margin * 2) or
                (self.x > WIDTH - margin * 2 and self.y < margin * 2) or
                (self.x > WIDTH - margin * 2 and self.y > HEIGHT - margin * 2)):
                
                center_x = WIDTH / 2
                center_y = HEIGHT / 2
                angle_to_center = math.atan2(center_y - self.y, center_x - self.x)
                self.x += math.cos(angle_to_center) * K_SPEED * 1.5
                self.y += math.sin(angle_to_center) * K_SPEED * 1.5
            
            # Update trail
            self.last_positions = self.last_positions[1:] + [(self.x, self.y)]

def main():
    clock = pygame.time.Clock()
    
    # Create characters
    player = Player(WIDTH//4, HEIGHT//2, RED, "S")
    k_char = SmartCharacter(3*WIDTH//4, HEIGHT//2, BLUE, "K")
    
    # Hide mouse cursor
    pygame.mouse.set_visible(False)
    
    # Game stats
    attempts = 0
    start_time = pygame.time.get_ticks()
    font = pygame.font.Font(None, 36)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        old_player_pos = (player.x, player.y)
        
        # Move characters
        player.move(mouse_x, mouse_y)
        
        # Only count attempt if player moved
        if (player.x, player.y) != old_player_pos:
            attempts += 1
            k_char.move(player)
        
        # Draw everything
        screen.fill(BLACK)
        player.draw(screen)
        k_char.draw(screen)
        
        # Display stats
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        distance = math.sqrt((player.x - k_char.x)**2 + (player.y - k_char.y)**2)
        stats_text = f"Attempts: {attempts} | Time: {elapsed_time}s | Distance: {int(distance)}px"
        text_surface = font.render(stats_text, True, WHITE)
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()