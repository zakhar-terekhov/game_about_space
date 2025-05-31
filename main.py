import asyncio
import curses
import random
import time
from itertools import cycle
from pathlib import Path
from statistics import median

from curses_tools import draw_frame, get_frame_size, read_controls

TIC_TIMEOUT = 0.1


async def animate_fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Анимирует мусор, перемещающийся сверху вниз. Положение столбца останется таким же, как указано при запуске."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def animate_spaceship(
    canvas: curses.window,
    row: int,
    column: int,
    frames: list[str],
    max_row: int,
    max_column: int,
) -> None:
    """Анимация звездного корабля."""

    canvas.nodelay(True)

    rows_direction, columns_direction, _ = (0, 0, False)

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

        draw_frame(canvas=canvas, start_row=row, start_column=column, text=frame)

        rows_direction, columns_direction, _ = read_controls(canvas)

        await asyncio.sleep(0)

        draw_frame(
            canvas=canvas,
            start_row=row,
            start_column=column,
            text=frame,
            negative=True,
        )


async def animate_fire(
    canvas: curses.window,
    start_row: int,
    start_column: int,
    rows_speed=-0.3,
    columns_speed=0,
) -> None:
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


async def animate_blink(
    canvas: curses.window,
    row: int,
    column: int,
    symbol: str,
    offset_tics: int,
) -> None:
    """Анимация зведного неба."""

    while True:
        for _ in range(offset_tics):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)
        for _ in range(offset_tics):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)
        for _ in range(offset_tics):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)
        for _ in range(offset_tics):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


def draw_animation(canvas: curses.window, amount=100) -> None:
    """Отображение анимаций на экране."""

    canvas.border()

    max_row, max_column = canvas.getmaxyx()

    frame_max_row, frame_max_column = max_row - 2, max_column - 2

    spaceship_frames_dir = Path("frames").glob("rocket_*")

    spaceship_frames = []

    for frame in spaceship_frames_dir:
        spaceship_frame = Path(frame).read_text(encoding="utf-8")
        spaceship_frames += [spaceship_frame, spaceship_frame]

    spaceship_row, spaceship_column = (2, 77)

    garbage_frames = [
        Path(frame).read_text(encoding="utf-8")
        for frame in Path("frames").glob("trash_*")
    ]

    coroutines = [
        animate_spaceship(
            canvas=canvas,
            row=spaceship_row,
            column=spaceship_column,
            frames=spaceship_frames,
            max_row=frame_max_row,
            max_column=frame_max_column,
        ),
    ]

    # fire(canvas, 6, 77) -- анимация выстрела

    for _ in range(amount):
        row, column = (
            random.randint(1, frame_max_row),
            random.randint(1, frame_max_column),
        )
        symbol = random.choice("+*.:")
        offset_tics = random.randint(1, 10)
        coroutines.append(
            animate_blink(
                canvas=canvas,
                row=row,
                column=column,
                symbol=symbol,
                offset_tics=offset_tics,
            )
        )

    for _ in range(5):
        column = random.randint(1, frame_max_column)
        garbage_frame = random.choice(garbage_frames)
        coroutines.append(
            animate_fly_garbage(
                canvas=canvas, column=column, garbage_frame=garbage_frame
            )
        )

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
    curses.wrapper(draw_animation)


if __name__ == "__main__":
    main()
