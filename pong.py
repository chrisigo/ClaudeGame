import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (50, 50, 50)

# Game settings
PADDLE_WIDTH = 12
PADDLE_HEIGHT = 80
PADDLE_SPEED = 6
BALL_SIZE = 12
BALL_SPEED_INITIAL = 5
BALL_SPEED_MAX = 12


class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move_up(self):
        self.rect.y -= self.speed
        if self.rect.top < 0:
            self.rect.top = 0

    def move_down(self):
        self.rect.y += self.speed
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=4)


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - BALL_SIZE // 2,
            SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
            BALL_SIZE,
            BALL_SIZE,
        )
        speed = BALL_SPEED_INITIAL
        direction_x = random.choice([-1, 1])
        direction_y = random.choice([-1, 1])
        self.vel_x = speed * direction_x
        self.vel_y = speed * direction_y

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Bounce off top and bottom walls
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel_y = abs(self.vel_y)
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = -abs(self.vel_y)

    def bounce_off_paddle(self, paddle):
        # Calculate relative hit position (-1 top, 0 center, 1 bottom)
        relative_y = (self.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
        relative_y = max(-1, min(1, relative_y))

        speed = min(abs(self.vel_x) + 0.3, BALL_SPEED_MAX)
        self.vel_x = speed if self.vel_x < 0 else -speed
        self.vel_y = relative_y * speed * 0.9

    def draw(self, surface):
        pygame.draw.ellipse(surface, GREEN, self.rect)


class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()

        self.left_paddle = Paddle(20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.right_paddle = Paddle(
            SCREEN_WIDTH - 20 - PADDLE_WIDTH,
            SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        )
        self.ball = Ball()

        self.left_score = 0
        self.right_score = 0

        self.font_large = pygame.font.SysFont("monospace", 64, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 24)

        self.game_over = False
        self.winner = ""
        self.winning_score = 7

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Left paddle: W / S
        if keys[pygame.K_w]:
            self.left_paddle.move_up()
        if keys[pygame.K_s]:
            self.left_paddle.move_down()

        # Right paddle: UP / DOWN arrows
        if keys[pygame.K_UP]:
            self.right_paddle.move_up()
        if keys[pygame.K_DOWN]:
            self.right_paddle.move_down()

    def update(self):
        if self.game_over:
            return

        self.ball.update()

        # Ball collision with left paddle
        if self.ball.rect.colliderect(self.left_paddle.rect) and self.ball.vel_x < 0:
            self.ball.rect.left = self.left_paddle.rect.right
            self.ball.bounce_off_paddle(self.left_paddle)

        # Ball collision with right paddle
        if self.ball.rect.colliderect(self.right_paddle.rect) and self.ball.vel_x > 0:
            self.ball.rect.right = self.right_paddle.rect.left
            self.ball.bounce_off_paddle(self.right_paddle)

        # Ball out of bounds - scoring
        if self.ball.rect.right < 0:
            self.right_score += 1
            self.check_winner()
            self.ball.reset()
        elif self.ball.rect.left > SCREEN_WIDTH:
            self.left_score += 1
            self.check_winner()
            self.ball.reset()

    def check_winner(self):
        if self.left_score >= self.winning_score:
            self.game_over = True
            self.winner = "Player 1 Wins!"
        elif self.right_score >= self.winning_score:
            self.game_over = True
            self.winner = "Player 2 Wins!"

    def draw(self):
        self.screen.fill(BLACK)

        # Draw center line
        for y in range(0, SCREEN_HEIGHT, 20):
            if (y // 20) % 2 == 0:
                pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH // 2 - 2, y, 4, 14))

        # Draw scores
        left_text = self.font_large.render(str(self.left_score), True, WHITE)
        right_text = self.font_large.render(str(self.right_score), True, WHITE)
        self.screen.blit(left_text, (SCREEN_WIDTH // 4 - left_text.get_width() // 2, 20))
        self.screen.blit(right_text, (3 * SCREEN_WIDTH // 4 - right_text.get_width() // 2, 20))

        # Draw paddles and ball
        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)
        self.ball.draw(self.screen)

        # Draw controls hint
        controls = self.font_small.render("W/S  vs  UP/DOWN    First to 7 wins", True, GRAY)
        self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 30))

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            win_text = self.font_large.render(self.winner, True, GREEN)
            self.screen.blit(
                win_text,
                (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60),
            )
            restart_text = self.font_small.render("Press R to restart  |  ESC to quit", True, WHITE)
            self.screen.blit(
                restart_text,
                (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20),
            )

        pygame.display.flip()

    def restart(self):
        self.left_score = 0
        self.right_score = 0
        self.left_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ball.reset()
        self.game_over = False
        self.winner = ""

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r and self.game_over:
                        self.restart()

            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = PongGame()
    game.run()
