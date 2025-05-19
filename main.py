import time
import curses


def draw(canvas):
    row, column = (5, 20)
    canvas.border()
    while True: 
        canvas.refresh()
        canvas.addstr(row, column, "*",curses.A_DIM)
        time.sleep(2)
        canvas.refresh()
        canvas.addstr(row, column, "*")
        time.sleep(0.3)
        canvas.refresh()
        canvas.addstr(row, column, "*",curses.A_BOLD)
        time.sleep(0.5)
        canvas.refresh()
        canvas.addstr(row, column, "*")
        time.sleep(0.3)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
