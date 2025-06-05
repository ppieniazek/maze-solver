import random
import time
from tkinter import BOTH, Canvas, Tk


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def draw(self, canvas: Canvas, fill_color: str):
        canvas.create_line(
            self.start.x, self.start.y, self.end.x, self.end.y, fill=fill_color, width=2
        )


class Window:
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title("Maze Solver")
        self.__root.protocol("WM_DELETE_WINDOW", self.close)
        self.__canvas = Canvas(self.__root, bg="white", height=height, width=width)
        self.__canvas.pack(fill=BOTH, expand=True)
        self.__running = False

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def draw_line(self, line: Line, fill_color: str = "black"):
        line.draw(self.__canvas, fill_color)

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False


class Cell:
    def __init__(self, win=None):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.__x1 = -1
        self.__x2 = -1
        self.__y1 = -1
        self.__y2 = -1
        self.__win = win
        self.visited = False

    def draw(self, x1, y1, x2, y2):
        if self.__win is None:
            return

        self.__x1 = x1
        self.__x2 = x2
        self.__y1 = y1
        self.__y2 = y2

        white_color = "#d9d9d9"

        left_wall = Line(Point(self.__x1, self.__y1), Point(self.__x1, self.__y2))
        if self.has_left_wall:
            self.__win.draw_line(left_wall)
        else:
            self.__win.draw_line(left_wall, white_color)

        right_wall = Line(Point(self.__x2, self.__y1), Point(self.__x2, self.__y2))
        if self.has_right_wall:
            self.__win.draw_line(right_wall)
        else:
            self.__win.draw_line(right_wall, white_color)

        top_wall = Line(Point(self.__x1, self.__y1), Point(self.__x2, self.__y1))
        if self.has_top_wall:
            self.__win.draw_line(top_wall)
        else:
            self.__win.draw_line(top_wall, white_color)

        bottom_wall = Line(Point(self.__x1, self.__y2), Point(self.__x2, self.__y2))
        if self.has_bottom_wall:
            self.__win.draw_line(bottom_wall)
        else:
            self.__win.draw_line(bottom_wall, white_color)

    def draw_move(self, to_cell, undo: bool = False):
        start = Point((self.__x1 + self.__x2) / 2, (self.__y1 + self.__y2) / 2)
        end = Point(
            (to_cell.__x1 + to_cell.__x2) / 2, (to_cell.__y1 + to_cell.__y2) / 2
        )
        color = "gray" if undo else "red"
        if self.__win:
            self.__win.draw_line(Line(start, end), color)


class Maze:
    def __init__(
        self,
        x1,
        y1,
        num_rows,
        num_cols,
        cell_size_x,
        cell_size_y,
        win=None,
        seed=None,
    ):
        self.__x1 = x1
        self.__y1 = y1
        self.__num_rows = num_rows
        self.__num_cols = num_cols
        self.__cell_size_x = cell_size_x
        self.__cell_size_y = cell_size_y
        self.__win = win
        self.__cells = []
        self.__seed = seed
        if seed:
            self.__seed = random.seed(seed)

        self.__create_cells()
        self.__break_entrance_and_exit()
        self.__break_walls_r(0, 0)

    def __create_cells(self):
        self.__cells = [
            [Cell(self.__win) for _ in range(self.__num_rows)]
            for _ in range(self.__num_cols)
        ]

        for i in range(self.__num_cols):
            for j in range(self.__num_rows):
                self.__draw_cell(i, j)

    def __draw_cell(self, i, j):
        if self.__win is None:
            return
        x1 = self.__x1 + i * self.__cell_size_x
        y1 = self.__y1 + j * self.__cell_size_y
        x2 = x1 + self.__cell_size_x
        y2 = y1 + self.__cell_size_y
        self.__cells[i][j].draw(x1, y1, x2, y2)
        self._animate()

    def _animate(self):
        if self.__win is None:
            return
        self.__win.redraw()
        time.sleep(0.01)

    def __break_entrance_and_exit(self):
        self.__cells[0][0].has_top_wall = False
        self.__draw_cell(0, 0)
        self.__cells[-1][-1].has_bottom_wall = False
        self.__draw_cell(self.__num_cols - 1, self.__num_rows - 1)

    def __break_walls_r(self, i, j):
        self.__cells[i][j].visited = True
        while True:
            need_to_visit = []

            visit_left = i > 0 and not self.__cells[i - 1][j].visited
            visit_right = i < self.__num_cols - 1 and not self.__cells[i + 1][j].visited
            visit_up = j > 0 and not self.__cells[i][j - 1].visited
            visit_bottom = (
                j < self.__num_rows - 1 and not self.__cells[i][j + 1].visited
            )

            if visit_left:
                need_to_visit.append((i - 1, j))
            if visit_right:
                need_to_visit.append((i + 1, j))
            if visit_up:
                need_to_visit.append((i, j - 1))
            if visit_bottom:
                need_to_visit.append((i, j + 1))

            if not need_to_visit:
                self.__draw_cell(i, j)
                return

            direction = random.choice(need_to_visit)
            new_i, new_j = direction

            if new_i == i + 1:
                self.__cells[i][j].has_right_wall = False
                self.__cells[i + 1][j].has_left_wall = False

            if new_i == i - 1:
                self.__cells[i][j].has_left_wall = False
                self.__cells[i - 1][j].has_right_wall = False

            if new_j == j + 1:
                self.__cells[i][j].has_bottom_wall = False
                self.__cells[i][j + 1].has_top_wall = False

            if new_j == j - 1:
                self.__cells[i][j].has_top_wall = False
                self.__cells[i][j - 1].has_bottom_wall = False

            self.__break_walls_r(new_i, new_j)
