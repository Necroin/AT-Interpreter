import sys
from Parser.parser import parser
from Robot.Robot import Robot, robot
from Map.Map import Map, maze


class Interpreter:
    def __init__(self, _parser=parser()):
        self.__parser = _parser

    def execute(self, program):
        functions_map, good = self.__parser.parse(program)
        if good is True:
            findexit = functions_map('FINDEXIT', None)
            if findexit is None:
                sys.stderr.write(f'Error: FINDEXIT function is not found')
            else:
                try:
                    findexit[0].call()
                except Exception as exception:
                    sys.stderr.write(str(exception))


interpreter = None

if __name__ == '__main__':
    global maze, robot
    map_file = open('Map/Maze.txt')
    maze = Map(map_file.read())
    print(maze)
    # start_x, start_y = maze.start_point()
    # robot = Robot(start_x, start_y)
    # program_file = open('Program.txt')
    # interpreter = Interpreter()
    # interpreter.execute(program_file.read())
