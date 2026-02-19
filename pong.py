import curses
import random
import time

PADDLE_HEIGHT = 5
BALL_CHAR = "O"
WINNING_SCORE = 7


def clamp(value, low, high):
    return max(low, min(high, value))


def draw_dashed_line(win, height, mid_x):
    for y in range(1, height - 1):
        if y % 2 == 0:
            try:
                win.addch(y, mid_x, "|", curses.color_pair(3))
            except curses.error:
                pass


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)  # ~20 fps

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # paddles / text
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # ball
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # center line (dim)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # scores

    height, width = stdscr.getmaxyx()

    # Game state
    left_score = right_score = 0
    left_y = height // 2 - PADDLE_HEIGHT // 2
    right_y = height // 2 - PADDLE_HEIGHT // 2

    ball_x = width / 2
    ball_y = height / 2
    speed = 1.0
    angle_x = random.choice([-1, 1]) * speed
    angle_y = random.uniform(-0.6, 0.6) * speed

    game_over = False
    winner = ""

    last_time = time.time()

    while True:
        now = time.time()
        dt = now - last_time
        last_time = now

        key = stdscr.getch()

        if key == ord("q") or key == 27:  # q or ESC
            break

        if game_over:
            if key == ord("r"):
                # Restart
                left_score = right_score = 0
                left_y = height // 2 - PADDLE_HEIGHT // 2
                right_y = height // 2 - PADDLE_HEIGHT // 2
                ball_x = width / 2
                ball_y = height / 2
                speed = 1.0
                angle_x = random.choice([-1, 1]) * speed
                angle_y = random.uniform(-0.6, 0.6) * speed
                game_over = False
                winner = ""
            stdscr.erase()
            # Draw game over screen
            msg = f"{winner}"
            sub = "Press R to restart  |  Q to quit"
            stdscr.addstr(
                height // 2 - 1,
                max(0, width // 2 - len(msg) // 2),
                msg,
                curses.color_pair(2) | curses.A_BOLD,
            )
            stdscr.addstr(
                height // 2 + 1,
                max(0, width // 2 - len(sub) // 2),
                sub,
                curses.color_pair(1),
            )
            stdscr.refresh()
            continue

        # Paddle input
        if key == ord("w"):
            left_y = clamp(left_y - 1, 1, height - 2 - PADDLE_HEIGHT)
        if key == ord("s"):
            left_y = clamp(left_y + 1, 1, height - 2 - PADDLE_HEIGHT)
        if key == curses.KEY_UP:
            right_y = clamp(right_y - 1, 1, height - 2 - PADDLE_HEIGHT)
        if key == curses.KEY_DOWN:
            right_y = clamp(right_y + 1, 1, height - 2 - PADDLE_HEIGHT)

        # Move ball
        ball_x += angle_x
        ball_y += angle_y

        bx = int(round(ball_x))
        by = int(round(ball_y))

        # Bounce off top/bottom walls
        if ball_y <= 1:
            ball_y = 1
            angle_y = abs(angle_y)
        elif ball_y >= height - 2:
            ball_y = height - 2
            angle_y = -abs(angle_y)

        # Collision with left paddle (column 2)
        if bx == 2 and left_y <= by < left_y + PADDLE_HEIGHT and angle_x < 0:
            rel = (by - (left_y + PADDLE_HEIGHT / 2)) / (PADDLE_HEIGHT / 2)
            speed = min(speed + 0.15, 2.5)
            angle_x = abs(angle_x) * speed / abs(angle_x) if angle_x != 0 else speed
            angle_x = speed
            angle_y = rel * speed * 0.8
            ball_x = 3

        # Collision with right paddle (column width-3)
        right_col = width - 3
        if bx == right_col and right_y <= by < right_y + PADDLE_HEIGHT and angle_x > 0:
            rel = (by - (right_y + PADDLE_HEIGHT / 2)) / (PADDLE_HEIGHT / 2)
            speed = min(speed + 0.15, 2.5)
            angle_x = -speed
            angle_y = rel * speed * 0.8
            ball_x = right_col - 1

        # Scoring
        if ball_x < 1:
            right_score += 1
            ball_x, ball_y = width / 2, height / 2
            speed = 1.0
            angle_x = random.choice([-1, 1]) * speed
            angle_y = random.uniform(-0.6, 0.6) * speed
            if right_score >= WINNING_SCORE:
                game_over = True
                winner = "Player 2 Wins!"

        elif ball_x >= width - 1:
            left_score += 1
            ball_x, ball_y = width / 2, height / 2
            speed = 1.0
            angle_x = random.choice([-1, 1]) * speed
            angle_y = random.uniform(-0.6, 0.6) * speed
            if left_score >= WINNING_SCORE:
                game_over = True
                winner = "Player 1 Wins!"

        # ---- Draw ----
        stdscr.erase()

        # Border
        stdscr.border()

        # Center dashed line
        draw_dashed_line(stdscr, height, width // 2)

        # Scores
        score_str = f"{left_score}   {right_score}"
        stdscr.addstr(
            0,
            width // 2 - len(score_str) // 2,
            score_str,
            curses.color_pair(4) | curses.A_BOLD,
        )

        # Controls hint at bottom
        hint = "W/S  vs  UP/DOWN    First to 7  |  Q to quit"
        try:
            stdscr.addstr(height - 1, max(0, width // 2 - len(hint) // 2), hint, curses.color_pair(3))
        except curses.error:
            pass

        # Left paddle
        for i in range(PADDLE_HEIGHT):
            try:
                stdscr.addch(left_y + i, 2, "|", curses.color_pair(1) | curses.A_BOLD)
            except curses.error:
                pass

        # Right paddle
        for i in range(PADDLE_HEIGHT):
            try:
                stdscr.addch(right_y + i, width - 3, "|", curses.color_pair(1) | curses.A_BOLD)
            except curses.error:
                pass

        # Ball (green)
        bx = int(round(ball_x))
        by = int(round(ball_y))
        try:
            stdscr.addch(by, bx, BALL_CHAR, curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass

        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
