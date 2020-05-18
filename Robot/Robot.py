class Robot:
    def __init__(self, x_pos, y_pos):
        self.__directions_funcs = [self.__move_left, self.__move_up, self.__move_right, self.__move_down]
        self.__direction = 0
        self.__directions_count = 4
        self.__x = x_pos
        self.__y = y_pos

    def move(self):
        self.__directions_funcs[self.__direction]()

    def __move_left(self):
        self.__x -= 1

    def __move_right(self):
        self.__x += 1

    def __move_up(self):
        self.__y -= 1

    def __move_down(self):
        self.__y += 1

    def rotate_left(self):
        self.__direction = (self.__direction + 1) % self.__directions_count

    def rotate_right(self):
        self.__direction -= 1
        if self.__direction < 0:
            self.__direction = self.__directions_count - 1

    @staticmethod
    def symbol():
        return '@'


robot = None
