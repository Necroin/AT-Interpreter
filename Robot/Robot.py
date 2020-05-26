from Map.Map import maze, wall_symbol, exit_symbol
from Variable.Variable import Variable, Value, reference_wrapper, _BOOL_TYPE_ID_


class Robot:
    def __init__(self, x_pos, y_pos, mood_flag=False):
        self.__directions_funcs = [self.__move_left, self.__move_up, self.__move_right, self.__move_down]
        self.__direction = 0
        self.__directions_count = 4
        self.__x = x_pos
        self.__y = y_pos
        self.__mood_flag = mood_flag
        self.__min_mood = 0
        self.__mood = 50
        self.__max_mood = 100
        self.__extra_mood = 20
        self.__alive = 1
        self.__right_rotate_count = 0
        self.__left_rotate_count = 0
        self.__max_rotate_count = 10
        self.__get_environment_count = 0
        self.__max_get_environment_count = 5
        self.__additional_see_exit_mood = 5

    def __get_mood_level(self):
        if self.__mood > 80:
            return 5
        elif self.__mood > 60:
            return 4
        elif self.__mood > 40:
            return 3
        elif self.__mood > 20:
            return 2
        else:
            return 1

    def move(self):
        self.__get_environment_count = 0
        self.__directions_funcs[self.__direction]()
        print(maze.get())
        if self.__mood_flag:
            if maze.get().get(self.__x, self.__y) == wall_symbol:
                raise Exception("The robot thinks you want to kill it. The robot self-destructed")
        return self

    def __move_left(self):
        self.__x -= 1

    def __move_right(self):
        self.__x += 1

    def __move_up(self):
        self.__y -= 1

    def __move_down(self):
        self.__y += 1

    def rotate_left(self):
        if self.__mood_flag:
            if self.__right_rotate_count:
                self.__right_rotate_count = 0
            if self.__left_rotate_count == self.__max_rotate_count:
                raise Exception("The robot thinks you want to break it. The robot self-destructed")
            self.__left_rotate_count += 1
        self.__direction -= 1
        if self.__direction < 0:
            self.__direction = self.__directions_count - 1
        return self

    def rotate_right(self):
        if self.__mood_flag:
            if self.__left_rotate_count:
                self.__left_rotate_count = 0
            if self.__right_rotate_count == self.__max_rotate_count:
                raise Exception("The robot thinks you want to break it. The robot self-destructed")
            self.__right_rotate_count += 1
        self.__direction = (self.__direction + 1) % self.__directions_count
        return self

    def get_environment(self):
        if self.__mood_flag:
            if self.__get_environment_count == self.__max_get_environment_count:
                raise Exception("The robot thinks you don't trust it. The robot self-destructed")
            self.__get_environment_count += 1
        observe_range = self.__get_mood_level()

        ret_var = Variable(_BOOL_TYPE_ID_, False, [observe_range * 2 + 1, observe_range * 2 + 1, 2])
        for i in range(observe_range * 2 + 1):
            for j in range(observe_range * 2 + 1):
                cell_symbol = maze.get().get(self.__x + j - observe_range, self.__y + i - observe_range)
                if cell_symbol == wall_symbol:
                    ret_var.get([j, i, 0]).get().trivial_assignment(Value(_BOOL_TYPE_ID_, True))
                if cell_symbol == exit_symbol:
                    ret_var.get([j, i, 1]).get().trivial_assignment(Value(_BOOL_TYPE_ID_, True))
                    self.__mood += self.__additional_see_exit_mood
                    if self.__mood > (self.__max_mood + self.__extra_mood):
                        raise Exception("The robot became paranoid. The robot self-destructed")
        return reference_wrapper(ret_var)

    def give_mood_points(self, points):
        if self.__mood_flag:
            self.__mood += points
            if self.__mood > (self.__max_mood + self.__extra_mood):
                raise Exception("The robot became paranoid. The robot self-destructed")
            if self.__mood < self.__min_mood:
                raise Exception("The robot was offended. The robot self-destructed")
        return self

    @staticmethod
    def symbol():
        return '@'

    def position(self):
        return self.__x, self.__y

    def get_dir(self):
        if self.__direction == 0:
            return "left"
        if self.__direction == 1:
            return "up"
        if self.__direction == 2:
            return "right"
        if self.__direction == 3:
            return "down"

robot = reference_wrapper(None)
