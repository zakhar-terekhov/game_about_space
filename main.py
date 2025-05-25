import asyncio
import curses
import random
import time
from itertools import cycle
from pathlib import Path
from statistics import median

TIC_TIMEOUT = 0.1
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def read_controls(canvas):
    """Считывает нажатые клавиши и возвращает кортеж с элементами управления состоянием."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Выводит на экран многострочный текст — кадр анимации.

    Убирает символ при negative=True.
    """

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == " ":
                continue

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else " "
            canvas.addch(row, column, symbol)


async def animate_spaceship(canvas, row, column, frames, max_row, max_column):
    """Анимация звездного корабля."""

    canvas.nodelay(True)

    rows_direction, columns_direction, space_pressed = (0, 0, False)

    for frame in cycle(frames):
        frame_rows_size, frame_columns_size = get_frame_size(frame)

        next_row, next_column = (
            row + rows_direction,
            column + columns_direction,
        )

        last_row_frame = next_row + frame_rows_size - 1
        last_column_frame = next_column + frame_columns_size - 1

        row, column = (
            median(sorted((max_row, last_row_frame, frame_rows_size)))
            - frame_rows_size
            + 1,
            median(sorted((max_column, last_column_frame, frame_columns_size)))
            - frame_columns_size
            + 1,
        )

        draw_frame(canvas, row, column, frame)

        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        await asyncio.sleep(0)

        draw_frame(
            canvas,
            row,
            column,
            frame,
            negative=True,
        )


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Анимация выстрела."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), "O")
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol):
    """Анимация зведного неба."""

    while True:
        repeat = random.randint(1, 10)
        for _ in range(repeat):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)
        for _ in range(repeat):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)
        for _ in range(repeat):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)
        for _ in range(repeat):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


def draw(canvas, amount=100):
    """Отображение анимаций на экране."""

    max_row, max_column = canvas.getmaxyx()

    frames_dir = Path("frames").glob("rocket_*")

    rocket_frames = [Path(frame).read_text() for frame in frames_dir]

    coroutines = [
        animate_spaceship(canvas, 2, 77, rocket_frames, max_row - 2, max_column - 2)
    ]

    # fire(canvas, 6, 77) -- анимация выстрела

    for _ in range(amount):
        row, column = random.randint(1, max_row - 1), random.randint(1, max_column - 1)
        symbol = random.choice("+*.:")
        coroutines.append(blink(canvas, row, column, symbol))

    canvas.border()

    while True:
        canvas.refresh()
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
