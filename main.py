import asyncio
import curses
import random
import time


async def blink(canvas, row, column, symbol, repeat=3):
    while True:
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
    height, width = curses.window.getmaxyx(canvas)

    coroutines = []

    for _ in range(amount):
        row, column = random.randint(1, height - 1), random.randint(1, width - 1)
        symbol = random.choice("+*.:")
        coroutines.append(blink(canvas, row, column, symbol))

    canvas.border()

    while True:
        canvas.refresh()
        for coroutine in coroutines:
            coroutine.send(None)
        time.sleep(0.5)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
