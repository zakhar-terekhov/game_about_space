import time
import curses
import asyncio


async def blink(canvas, row, column, symbol="*"):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

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
        time.sleep(1)
    # canvas.addstr(row, column, "*",curses.A_DIM)
    # time.sleep(2)
    # canvas.refresh()
    # canvas.addstr(row, column, "*")
    # time.sleep(0.3)
    # canvas.refresh()
    # canvas.addstr(row, column, "*",curses.A_BOLD)
    # time.sleep(0.5)
    # canvas.refresh()
    # canvas.addstr(row, column, "*")
    # time.sleep(0.3)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
