import asyncio
import curses
import time


async def blink(canvas, row, column, symbol="*", repeat=3):
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


def draw(canvas):
    row, column = (5, 20)
    canvas.border()
    coroutines = [blink(canvas, row, column) for column in range(column, 30, 2)]
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
