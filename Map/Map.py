from ctypes.wintypes import DWORD
from tkinter import *

from pip._vendor.colorama.win32 import COORD
from win32api import *
from win32console import *

from Variable.Variable import reference_wrapper
import Robot.Robot

wall_symbol = "#"
free_cell_symbol = " "
respawn_symbol = "*"
exit_symbol = "~"


class Map:
    def __init__(self, data):
        self.__data = data
        self.__start_x = 0
        self.__start_y = 0
        self.__length = 0
        self.__height = 0
        self.__maze = []

        self.__maze.append([])
        row_index = 0
        for symbol in self.__data:
            if symbol == '*':
                self.__start_x = len(self.__maze[row_index])
                self.__start_y = row_index
            if symbol != '\n':
                self.__maze[row_index].append(symbol)
            else:
                row_index += 1
                self.__maze.append([])

    def start_point(self):
        return self.__start_x, self.__start_y

    def get(self, x, y):
        if x < 0 or x >= len(self.__maze[0]) or y < 0 or y >= len(self.__maze):
            return free_cell_symbol
        return self.__maze[y][x]

    def __repr__(self):
        i = 0
        x, y = Robot.Robot.robot.get().position()
        for row in self.__maze:
            j = 0
            for symbol in row:
                if x == j and y == i:
                    print('@', end="")
                else:
                    print(symbol, end="")
                j += 1
            print()
            i += 1
        print(Robot.Robot.robot.get().get_dir())
        return ""

    def tkprint(self, canvas: Canvas):
        for i in range(len(self.__maze)):
            for j in range(len(self.__maze[i])):
                if self.__maze[i][j] == wall_symbol:
                    canvas.create_rectangle(i, j, 1, 1, fill='red')


maze = reference_wrapper(None)

if __name__ == '__main__':
    map_file = open('Maze.txt')
    maze.set(Map(map_file.read()))
    print(maze.get())
    # window = Tk()
    # window.title("Findexit")
    # window.geometry('1600x900')
    # canvas = Canvas(window, width=600, height=600)
    # canvas.pack()
    # maze.tkprint(canvas)
    # window.update()
    # window.mainloop()
