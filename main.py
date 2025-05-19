import time
import curses


def draw(canvas):
    row, column = (5, 20)
    canvas.addstr(row, column, "Hello, World!")
    canvas.refresh()
    time.sleep(10)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
