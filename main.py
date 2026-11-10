
import pygame
import random
import sys

# =====================================
# MINI RACING - PYTHON PYGAME
# =====================================

pygame.init()

WIDTH = 480
HEIGHT = 650

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("MINI RACING")

clock = pygame.time.Clock()

# Logical game resolution
game_surface = pygame.Surface((WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (15, 15, 20)
GRAY = (65, 65, 70)
DARK_GRAY = (40, 40, 45)
GREEN = (35, 130, 65)
BLUE = (30, 130, 255)
RED = (230, 45, 45)
YELLOW = (255, 210, 40)
CYAN = (0, 220, 255)

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 70)

# =====================================
# GAME SETTINGS
# =====================================

ROAD_LEFT = 65
ROAD_RIGHT = 415

LANES = [125, 240, 355]

player_x = 240
player_y = 590

player_width = 48
player_height = 85

player_speed = 1000
world_speed = 1000

score = 0
game_over = False
game_started = False

enemies = []
spawn_timer = 0

road_offset = 0
road_speed = 300

# Touch controls
left_button = pygame.Rect(25, 690, 100, 85)
right_button = pygame.Rect(140, 690, 100, 85)
gas_button = pygame.Rect(355, 690, 100, 85)

touching = set()

# =====================================
# FUNCTIONS
# =====================================

def draw_text(surface, text, font_type, color, x, y):
    image = font_type.render(text, True, color)
    rect = image.get_rect(center=(x, y))
    surface.blit(image, rect)


def draw_car(surface, x, y, color):
    x = int(x)
    y = int(y)

    # Wheels
    pygame.draw.rect(
        surface, BLACK,
        (x - 26, y + 15, 10, 23),
        border_radius=4
    )
    pygame.draw.rect(
        surface, BLACK,
        (x + 16, y + 15, 10, 23),
        border_radius=4
    )
    pygame.draw.rect(
        surface, BLACK,
        (x - 26, y + 55, 10, 23),
        border_radius=4
    )
    pygame.draw.rect(
        surface, BLACK,
        (x + 16, y + 55, 10, 23),
        border_radius=4
    )

    # Car body
    pygame.draw.rect(
        surface, color,
        (x - 22, y, 44, 85),
        border_radius=10
    )

    # Windows
    pygame.draw.rect(
        surface, (120, 210, 240),
        (x - 16, y + 17, 32, 23),
        border_radius=5
    )

    pygame.draw.rect(
        surface, (30, 60, 90),
        (x - 15, y + 48, 30, 16),
        border_radius=4
    )

    # Headlights
    pygame.draw.rect(
        surface, YELLOW,
        (x - 18, y + 3, 10, 5)
    )
    pygame.draw.rect(
        surface, YELLOW,
        (x + 8, y + 3, 10, 5)
    )


def draw_road(surface, dt):
    global road_offset

    surface.fill(GREEN)

    # Road
    pygame.draw.rect(
        surface, GRAY,
        (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT)
    )

    # Road edges
    pygame.draw.rect(
        surface, WHITE,
        (ROAD_LEFT, 0, 6, HEIGHT)
    )
    pygame.draw.rect(
        surface, WHITE,
        (ROAD_RIGHT - 6, 0, 6, HEIGHT)
    )

    # Moving lane lines
    road_offset += world_speed * dt

    if road_offset >= 100:
        road_offset = 0

    for lane_x in [182, 297]:
        for y in range(-100, HEIGHT + 100, 100):
            line_y = y + int(road_offset)

            pygame.draw.rect(
                surface, WHITE,
                (lane_x, line_y, 6, 50),
                border_radius=3
            )


def spawn_enemy():
    lane = random.choice(LANES)

    enemies.append({
        "x": lane,
        "y": -100,
        "speed": random.randint(50, 150),
        "color": random.choice([
            RED,
            YELLOW,
            (180, 50, 220),
            (255, 120, 20)
        ])
    })


def reset_game():
    global player_x, score, game_over
    global game_started, enemies, spawn_timer
    global world_speed, road_offset

    player_x = 240
    score = 0
    game_over = False
    game_started = True

    enemies = []
    spawn_timer = 0
    world_speed = 300
    road_offset = 0


def collision(x1, y1, x2, y2):
    rect1 = pygame.Rect(x1 - 19, y1 + 5, 38, 75)
    rect2 = pygame.Rect(x2 - 19, y2 + 5, 38, 75)

    return rect1.colliderect(rect2)


def button(surface, rect, text, active=False):
    color = (0, 160, 210) if active else (35, 45, 60)

    pygame.draw.rect(
        surface, color, rect,
        border_radius=15
    )

    pygame.draw.rect(
        surface, WHITE, rect,
        width=2,
        border_radius=15
    )

    draw_text(
        surface, text, font,
        WHITE, rect.centerx, rect.centery
    )


# =====================================
# MAIN GAME LOOP
# =====================================

running = True

while running:

    dt = min(clock.tick(60) / 1000, 0.05)

    # Input state
    keys = pygame.key.get_pressed()

    move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
    move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    accelerate = keys[pygame.K_UP] or keys[pygame.K_w]
    brake = keys[pygame.K_DOWN] or keys[pygame.K_s]

    # Touch controls
    move_left = move_left or "left" in touching
    move_right = move_right or "right" in touching
    accelerate = accelerate or "gas" in touching
    brake = brake or "brake" in touching

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Keyboard restart
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_RETURN:
                if not game_started or game_over:
                    reset_game()

        # Mouse touchscreen support
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx = event.pos[0] * WIDTH / screen.get_width()
            my = event.pos[1] * HEIGHT / screen.get_height()

            if game_over or not game_started:
                if 100 <= mx <= 380 and 350 <= my <= 490:
                    reset_game()
            else:
                if left_button.collidepoint(mx, my):
                    touching.add("left")
                if right_button.collidepoint(mx, my):
                    touching.add("right")
                if gas_button.collidepoint(mx, my):
                    touching.add("gas")

        if event.type == pygame.MOUSEBUTTONUP:
            touching.clear()

        # Native finger touch events
        if event.type == pygame.FINGERDOWN:
            fx = event.x * WIDTH
            fy = event.y * HEIGHT

            if game_over or not game_started:
                if 100 <= fx <= 380 and 350 <= fy <= 490:
                    reset_game()
            else:
                if left_button.collidepoint(fx, fy):
                    touching.add("left")
                if right_button.collidepoint(fx, fy):
                    touching.add("right")
                if gas_button.collidepoint(fx, fy):
                    touching.add("gas")

        if event.type == pygame.FINGERUP:
            touching.clear()

    # =================================
    # UPDATE GAME
    # =================================

    if game_started and not game_over:

        # Speed control
        if accelerate:
            world_speed = min(world_speed + 180 * dt, 600)
        elif brake:
            world_speed = max(world_speed - 250 * dt, 150)
        else:
            world_speed += (300 - world_speed) * dt

        # Player movement
        if move_left:
            player_x -= player_speed * dt

        if move_right:
            player_x += player_speed * dt

        player_x = max(
            ROAD_LEFT + 30,
            min(ROAD_RIGHT - 30, player_x)
        )

        # Spawn enemies
        spawn_timer += dt

        spawn_delay = max(0.45, 1.2 - score / 1000)

        if spawn_timer >= spawn_delay:
            spawn_enemy()
            spawn_timer = 0

        # Move enemies
        for enemy in enemies:
            enemy["y"] += (
                world_speed + enemy["speed"]
            ) * dt

            if collision(
                player_x, player_y,
                enemy["x"], enemy["y"]
            ):
                game_over = True

        # Remove enemies
        for enemy in enemies[:]:
            if enemy["y"] > HEIGHT + 100:
                enemies.remove(enemy)
                score += 10

    # =================================
    # DRAW GAME
    # =================================

    draw_road(game_surface, dt if game_started and not game_over else 0)

    # Enemy cars
    for enemy in enemies:
        draw_car(
            game_surface,
            enemy["x"],
            enemy["y"],
            enemy["color"]
        )

    # Player
    if game_started:
        draw_car(
            game_surface,
            player_x,
            player_y,
            BLUE
        )

    # Score
    pygame.draw.rect(
        game_surface, BLACK,
        (10, 10, 160, 75),
        border_radius=12
    )

    draw_text(
        game_surface,
        f"SCORE: {score}",
        font, WHITE, 90, 35
    )

    draw_text(
        game_surface,
        f"SPEED: {int(world_speed)}",
        pygame.font.Font(None, 25),
        CYAN, 90, 65
    )

    # Touch controls
    button(
        game_surface, left_button,
        "<", "left" in touching
    )

    button(
        game_surface, right_button,
        ">", "right" in touching
    )

    button(
        game_surface, gas_button,
        "GAS", "gas" in touching
    )

    # Start screen
    if not game_started:

        pygame.draw.rect(
            game_surface, BLACK,
            (45, 270, 390, 250),
            border_radius=20
        )

        draw_text(
            game_surface,
            "MINI RACING",
            big_font, CYAN, 240, 330
        )

        draw_text(
            game_surface,
            "PRESS ENTER OR PLAY",
            font, WHITE, 240, 410
        )

        draw_text(
            game_surface,
            "Avoid enemy cars!",
            font, YELLOW, 240, 460
        )

    # Game over screen
    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 175))
        game_surface.blit(overlay, (0, 0))

        draw_text(
            game_surface,
            "GAME OVER",
            big_font, RED, 240, 300
        )

        draw_text(
            game_surface,
            f"FINAL SCORE: {score}",
            font, WHITE, 240, 370
        )

        pygame.draw.rect(
            game_surface, BLUE,
            (100, 420, 280, 80),
            border_radius=15
        )

        draw_text(
            game_surface,
            "PLAY AGAIN",
            font, WHITE, 240, 460
        )

        draw_text(
            game_surface,
            "Press ENTER to restart",
            font, YELLOW, 240, 550
        )

    # Scale game to window
    scaled = pygame.transform.scale(
        game_surface,
        screen.get_size()
    )

    screen.blit(scaled, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()
