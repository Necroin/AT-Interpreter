import sys
from Parser.parser import parser
import Robot.Robot
import Map.Map
from Variable.Variable import reference_wrapper


class Interpreter:
    def __init__(self, _parser=parser()):
        self.__parser = _parser

    def execute(self, program, debug=False, tests=False):
        functions_map, good = self.__parser.parse(program, debug, tests)
        if good is True:
            findexit = functions_map.get('FINDEXIT', None)
            if findexit is None:
                sys.stderr.write(f'Error: FINDEXIT function is not found')
            else:
                try:
                    findexit[1] = reference_wrapper(findexit[0].call([]).get())
                    if not tests:
                        if findexit[1].get()._Variable__objects[0].get()._Value__value == True:
                            print('exit was found')
                        else:
                            print("can't find exit")
                except Exception as exception:
                    sys.stderr.write(str(exception))


interpreter = None
function_name_debug = False
if __name__ == '__main__':
    debug = True
    tests = True
    sys.setrecursionlimit(2000)
    if debug:
        interpreter = Interpreter()
        # print("Fibonacci:")
        # test_file = open('../Tests/Fibonacci.txt')
        # interpreter.execute(test_file.read(), debug, tests)
        # test_file.close()
        # print("Reference callable function:")
        # test_file = open('../Tests/FunctionRefCall.txt')
        # interpreter.execute(test_file.read(), debug, tests)
        # test_file.close()
        # print("For:")
        # test_file = open('../Tests/For.txt')
        # interpreter.execute(test_file.read(), debug, tests)
        # test_file.close()
        print("Syntax errors")
        test_file = open('../Tests/SyntaxErrors.txt')
        interpreter.execute(test_file.read(), debug, tests)
        test_file.close()
    else:
        map_file = open('../Map/Maze.txt')
        Map.Map.maze.set(Map.Map.Map(map_file.read()))
        start_x, start_y = Map.Map.maze.get().start_point()
        Robot.Robot.robot.set(Robot.Robot.Robot(start_x, start_y, False))
        program_file = open('Program.txt')
        print(Map.Map.maze.get())
        interpreter = Interpreter()
        interpreter.execute(program_file.read())
