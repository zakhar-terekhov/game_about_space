import asyncio
import curses
import random
import time


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


def draw(canvas, amount=200):
    """Отображение анимаций на экране."""

    max_row, max_column = canvas.getmaxyx()

    coroutines = [fire(canvas, 6, 77)]

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
        time.sleep(0.3)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
