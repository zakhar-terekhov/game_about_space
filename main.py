import asyncio
import curses
import random
import time
from itertools import cycle
from pathlib import Path
from statistics import median

from curses_tools import draw_frame, get_frame_size, read_controls
from explosion import explode
from game_scenario import PHRASES, get_garbage_delay_tics
from obstacles import Obstacle
from physics import update_speed
from state import coroutines, obstacles, obstacles_in_last_collisions, year

TIC_TIMEOUT = 0.1


async def sleep(tics=1) -> None:
    """Задержка между кадрами анимации в секундах."""
    for _ in range(tics):
        await asyncio.sleep(0)


async def show_gameover(canvas: curses.window, row=5, column=25) -> None:
    """Отображает заставку Game Over при столкновнении мусора со звездолетом."""

    game_over_frame = Path("frames/game_over.txt").read_text(encoding="utf-8")

    while True:
        draw_frame(
            canvas=canvas, start_row=row, start_column=column, text=game_over_frame
        )
        await asyncio.sleep(0)


async def shows_year_description(
    canvas: curses.window,
    rows_size=5,
    columns_size=40,
    row=15,
    column=1,
) -> None:
    """Отсчитывает года и выводит на экран событие, произошедшее в мире космонавтики в конкретном году."""
    global year
    while True:
        canvas.derwin(rows_size, columns_size, row, column).box()
        phrase = f"{year} year \n {PHRASES.get(year, '')}"
        draw_frame(
            canvas=canvas,
            start_row=row + 1,
            start_column=column + 1,
            text=phrase,
        )
        await sleep(15)
        draw_frame(
            canvas=canvas,
            start_row=row + 1,
            start_column=column + 1,
            text=phrase,
            negative=True,
        )
        year += 1


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

    rows_direction, columns_direction, space_pressed = (0, 0, False)
    row_speed = column_speed = 0

    for frame in cycle(frames):
        frame_rows_size, frame_columns_size = get_frame_size(frame)

        next_row, next_column = (
            row + rows_direction,
            column + columns_direction,
        )

        last_row_frame = next_row + frame_rows_size - 1
        last_column_frame = next_column + frame_columns_size - 1

        row_speed, column_speed = update_speed(
            row_speed,
            column_speed,
            rows_direction,
            columns_direction,
        )

        row, column = (
            median(sorted((max_row, last_row_frame, frame_rows_size)))
            - frame_rows_size
            + 1
            + row_speed,
            median(sorted((max_column, last_column_frame, frame_columns_size)))
            - frame_columns_size
            + 1
            + column_speed,
        )

        for obstacle in obstacles:
            if obstacle.has_collision(row + 2, column + 2):
                coroutines.append(show_gameover(canvas=canvas))
                return

        draw_frame(
            canvas=canvas,
            start_row=row,
            start_column=column,
            text=frame,
        )

        if space_pressed:
            coroutines.append(
                animate_fire(
                    canvas=canvas,
                    start_row=row + 2,
                    start_column=column + 2,
                )
            )

        rows_direction, columns_direction, space_pressed = read_controls(canvas)

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

    row += rows_speed
    column += columns_speed

    canvas.addstr(round(row), round(column), " ")
    symbol = "-" if columns_speed else "|"

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        obstacles_in_last_collisions.clear()
        obstacles_in_last_collisions.extend(
            [obstacle for obstacle in obstacles if obstacle.has_collision(row, column)]
        )
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
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(offset_tics)
        canvas.addstr(row, column, symbol)
        await sleep(offset_tics)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(offset_tics)
        canvas.addstr(row, column, symbol)
        await sleep(offset_tics)


async def animate_flying_garbage(
    canvas: curses.window,
    column: int,
    garbage_frame: str,
    speed=0.5,
) -> None:
    """Анимирует мусор, перемещающийся сверху вниз.

    Положение столбца останется таким же, как указано при запуске."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    rows_size, columns_size = get_frame_size(garbage_frame)

    while row < rows_number:
        obstacles.clear()
        obstacles.append(
            Obstacle(
                row=row,
                column=column,
                rows_size=rows_size + 1,
                columns_size=columns_size + 1,
            )
        )
        for collision in obstacles_in_last_collisions:
            if collision.has_collision(row, column):
                coroutines.append(
                    explode(canvas=canvas, center_row=row, center_column=column)
                )
                return
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(
    canvas: curses.window,
    garbage_frames: list,
    frame_max_column: int,
) -> None:
    """Разбрасывает звездный мусор по небу."""

    while True:
        garbage_column = random.randint(1, frame_max_column)

        garbage_frame = random.choice(garbage_frames)

        delay = get_garbage_delay_tics(year)

        if delay is not None:
            garbage_column = random.randint(1, frame_max_column)
            garbage_frame = random.choice(garbage_frames)
            coroutines.append(
                animate_flying_garbage(
                    canvas=canvas,
                    column=garbage_column,
                    garbage_frame=garbage_frame,
                )
            )

            await sleep(delay)

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
        spaceship_frames += [spaceship_frame] * 2

    spaceship_row, spaceship_column = 12, 50

    garbage_frames = [
        Path(frame).read_text(encoding="utf-8")
        for frame in Path("frames").glob("trash_*")
    ]

    coroutines.extend(
        [
            shows_year_description(canvas=canvas, row=15, column=1),
            animate_spaceship(
                canvas=canvas,
                row=spaceship_row,
                column=spaceship_column,
                frames=spaceship_frames,
                max_row=frame_max_row,
                max_column=frame_max_column,
            ),
        ]
    )

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

    garbage_coroutine = fill_orbit_with_garbage(
        canvas=canvas,
        garbage_frames=garbage_frames,
        frame_max_column=frame_max_column,
    )

    while True:
        canvas.refresh()

        garbage_coroutine.send(None)

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