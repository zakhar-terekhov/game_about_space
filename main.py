import asyncio
import curses
import random
import time
from itertools import cycle
from pathlib import Path

TIC_TIMEOUT = 0.3

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


async def animate_spaceship(canvas, row, column, frames):
    """Анимация звездного корабля."""
    for frame in cycle(frames):
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


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


def draw(canvas, amount=50):
    """Отображение анимаций на экране."""

    max_row, max_column = canvas.getmaxyx()

    frames_dir = Path("frames").glob("rocket_*")

    rocket_frames = [Path(frame).read_text() for frame in frames_dir]

    coroutines = [fire(canvas, 6, 77), animate_spaceship(canvas, 2, 77, rocket_frames)]

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
