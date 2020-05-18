from ctypes.wintypes import DWORD
from tkinter import *

from pip._vendor.colorama.win32 import COORD
from win32api import *
from win32console import *


class MapObject:
    def __init__(self, symbol):
        self.__symbol = symbol

    def symbol(self):
        return self.__symbol


class Wall(MapObject):
    def __init__(self):
        super().__init__('#')


class Respawn(MapObject):
    def __init__(self):
        super().__init__('*')


class FreeCell(MapObject):
    def __init__(self):
        super().__init__(' ')


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
            if symbol == ' ':
                self.__maze[row_index].append(FreeCell())
            if symbol == '#':
                self.__maze[row_index].append(Wall())
            if symbol == '*':
                self.__maze[row_index].append(Respawn())
            if symbol == '\n':
                row_index += 1
                self.__maze.append([])

    def start_point(self):
        return self.__start_x, self.__start_y

    def __repr__(self):
        for row in self.__maze:
            for map_object in row:
                print(map_object.symbol(), end="")
            print()
        return ""

    def tkprint(self, canvas: Canvas):
        for i in range(len(self.__maze)):
            for j in range(len(self.__maze[i])):
                if self.__maze[i][j].symbol() == '#':
                    canvas.create_rectangle(i, j, 1, 1, fill='red')


maze = None

if __name__ == '__main__':
    map_file = open('Maze.txt')
    maze = Map(map_file.read())
    print(maze)
    # window = Tk()
    # window.title("Findexit")
    # window.geometry('1600x900')
    # canvas = Canvas(window, width=600, height=600)
    # canvas.pack()
    # maze.tkprint(canvas)
    # window.update()
    # window.mainloop()
