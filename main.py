import pygame
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2)

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

BG_COLOR = (173, 216, 230)
NUM_LEMONS = 10
COLLECTION_GOAL = 20

LEMON_WIDTH = 30
LEMON_HEIGHT = 15

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lemon Tree Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 48)

# Load lemon and tree images
lemon_img_raw = pygame.image.load("lemon.jpg")
LEMON_IMG = pygame.transform.scale(lemon_img_raw, (LEMON_WIDTH, LEMON_HEIGHT))
tree_img_raw = pygame.image.load("tree.png").convert_alpha()
tree_img = pygame.transform.scale(tree_img_raw, (WIDTH-100, HEIGHT-50))  # adjust size 

TREE_X = WIDTH // 2 - tree_img.get_width() // 2
TREE_Y = HEIGHT - tree_img.get_height()

# Play music
pygame.mixer.music.load("background_music.mp3")  # ✅ Load your file
pygame.mixer.music.play(-1)  # ✅ Loop forever

goal_sound = pygame.mixer.Sound("goal_reached.mp3")

# Lemon class
class Lemon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.falling = False
        self.clicked = False

    def update(self):
        if self.falling:
            self.y += 5

    def draw(self, surface):
        surface.blit(LEMON_IMG, (self.x - LEMON_WIDTH // 2, self.y - LEMON_HEIGHT // 2))

    def check_click(self, pos):
        global collected_count
        if game_paused:
            return  # no clicking when paused

        dx = pos[0] - self.x
        dy = pos[1] - self.y
        if abs(dx) < LEMON_WIDTH // 2 and abs(dy) < LEMON_HEIGHT // 2:
            if not self.clicked:
                self.clicked = True
                collected_count += 1
                self.falling = True

    def is_off_screen(self):
        return self.y > HEIGHT

# Spawn lemon with spacing
def spawn_lemon(others):
    max_attempts = 100
    for _ in range(max_attempts):
        x = random.randint(150, WIDTH-150)
        y = random.randint(100, 200)
        if all((x - other.x) >= (LEMON_WIDTH+1) for other in others) and all((y - other.y) >= (LEMON_HEIGHT+1) for other in others):
            return Lemon(x, y)
    return Lemon(x, y)  # fallback

# Create initial lemons
lemons = []
for _ in range(NUM_LEMONS):
    lemons.append(spawn_lemon(lemons))

collected_count = 0
game_paused = False
running = True

while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)

    screen.blit(tree_img, (TREE_X, TREE_Y))

    # Pause game after goal reached
    if collected_count >= COLLECTION_GOAL:
        game_paused = True
        pygame.mixer.music.pause()
        goal_sound.play()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_paused:
            for lemon in lemons:
                lemon.check_click(event.pos)

    # Update and draw lemons
    for lemon in lemons[:]:
        # Always update falling lemons (even when paused)
        if lemon.falling:
            lemon.update()

        # Remove lemons that fall off screen
        if lemon.is_off_screen():
            lemons.remove(lemon)
            # Respawn ONLY if game is NOT paused and lemon was NOT clicked
            if not game_paused and not lemon.clicked:
                lemons.append(spawn_lemon(lemons))
        else:
            lemon.draw(screen)

    # Show collection goal at the top left
    goal_text = font.render(f"Gather {COLLECTION_GOAL} lemons", True, (0, 0, 0))
    screen.blit(goal_text, (20, 20))

    # Show how many lemons have been collected (under the goal)
    label_text = font.render("Lemons Collected: ", True, (0, 0, 0))
    screen.blit(label_text, (20, 50))
    # Render the number in red, and place it next to the label
    number_text = font.render(str(collected_count), True, (255, 0, 0))
    screen.blit(number_text, (label_text.get_width() + 20, 50))

    # Draw end message if paused
    if game_paused:
        msg = big_font.render("You've collected enough lemons!", True, (0, 100, 0))
        msg_rect = msg.get_rect(center=(WIDTH // 2, 100))
        screen.blit(msg, msg_rect)

    pygame.display.flip()

pygame.quit()
