from typing import overload

_BOOL_TYPE_ID_ = 0
_INT_TYPE_ID_ = 1

_VARIABLE_ = True
_NOT_VARIABLE_ = False


class Object:
    def __init__(self, type_id, variable_flag):
        self.__type_id = type_id
        self.__variable_flag = variable_flag

    def type(self):
        return self.__type_id

    def is_variable(self):
        return self.__variable_flag


class Value(Object):
    def __init__(self, type_id, init_value):
        super().__init__(type_id, _NOT_VARIABLE_)
        self.__value = init_value

    def __iadd__(self, other):
        if self.__type_id != other.__type_id:
            raise Exception("types are not equal")
        self.__value += other.__value
        return self

    def __add__(self, other):
        ret_var = self
        ret_var += other
        return ret_var

    def __isub__(self, other):
        if self.__type_id != other.__type_id:
            raise Exception("types are not equal")
        self.__value -= other.__value
        return self

    def __sub__(self, other):
        ret_var = self
        ret_var += other
        return ret_var

    def __imul__(self, other):
        if self.__type_id != other.__type_id:
            raise Exception("types are not equal")
        self.__value *= other.__value
        return self

    def __mul__(self, other):
        ret_var = self
        ret_var *= other
        return ret_var

    def __itruediv__(self, other):
        if self.__type_id != other.__type_id:
            raise Exception("types are not equal")
        self.__value /= other.__value
        return self

    def __truediv__(self, other):
        ret_var = self
        ret_var /= other
        return ret_var


class Variable(Object):
    def __init__(self, _type_id, _init_value, _dimensions):
        super().__init__(_type_id, _VARIABLE_)
        self.__objects = []
        self.__type_id = _type_id
        dimension = _dimensions[0]
        if len(_dimensions) > 1:
            other_dimensions = _dimensions[1:]
            for _ in range(dimension):
                self.__objects.append(Variable(_type_id, _init_value, other_dimensions))
        else:
            for _ in range(dimension):
                self.__objects.append(Value(_type_id, _init_value))

    @overload
    def assign(self, _type_id, _count, _value):
        if self.__type_id != _type_id:
            raise Exception("types are not equal")
        self.__objects.clear()
        for i in range(_count):
            self.__objects.append(_value)

    @assign.overload
    def assign(self, _type_id, _value_array):
        if self.__type_id != _type_id:
            raise Exception("types are not equal")
        self.__objects.clear()
        for i in range(len(_value_array)):
            self.__objects.append(Value(_type_id, _value_array[i]))

    def global_size(self):
        g_size = []
        if self.__objects[0].is_variable():
            g_size = self.__objects[0].global_size()
            g_size.insert(0, len(self.__objects))
            return g_size
        return g_size.append(len(self.__objects))

    def size(self):
        return Variable(_INT_TYPE_ID_, 0, range(0)).assign(_INT_TYPE_ID_, self.global_size())

    def __iadd__(self, other):
        if self.__type_id != other.__type_id:
            raise Exception("types are not equal")
        for i in range(len(self.__objects)):
            self.__objects[i] += other.__objects[i]
        return self

    def __add__(self, other):
        ret_var = self
        ret_var += other
        return ret_var

    def __isub__(self, other):
        if self.__type_id != other.__type_id:
            raise Exception("types are not equal")
        for i in range(len(self.__objects)):
            self.__objects[i] -= other.__objects[i]
        return self

    def __sub__(self, other):
        ret_var = self
        ret_var -= other
        return ret_var

    def __imul__(self, other):
        if self.__type_id != other.__type_id:
            raise Exception("types are not equal")
        for i in range(len(self.__objects)):
            self.__objects[i] *= other.__objects[i]
        return self

    def __mul__(self, other):
        ret_var = self
        ret_var *= other
        return ret_var

    def __itruediv__(self, other):
        if self.__type_id != other.__type_id:
            raise Exception("types are not equal")
        for i in range(len(self.__objects)):
            self.__objects[i] /= other.__objects[i]
        return self

    def __truediv__(self, other):
        ret_var = self
        ret_var /= other
        return ret_var

    def logitize(self):
        if self.__type_id != _INT_TYPE_ID_:
            raise Exception("type is bool")
        if self.__objects[0].is_variable():
            for _object in self.__objects:
                _object.logitize()
        else:
            for _object in self.__objects:
                _object.__value = bool(_object.__value)
        return self

    def digitize(self):
        if self.__type_id != _BOOL_TYPE_ID_:
            raise Exception("type is bool")
        if self.__objects[0].is_variable():
            for _object in self.__objects:
                _object.digitize()
        else:
            for _object in self.__objects:
                _object.__value = int(_object.__value)
        return self

    def reduce(self, _dimensions):
        if len(_dimensions) > len(self.global_size()):
            raise Exception("reduce list is too much")
        if _dimensions[0] >= len(self.__objects):
            raise Exception("reduce size is too much")
        for _ in range(_dimensions[0]):
            self.__objects.pop()
        if len(_dimensions) > 1:
            for _object in self.__objects:
                other_dimensions = _dimensions[1:]
                _object.reduce(other_dimensions)

    def extent(self, _dimensions):
        default_value = (True, 0)

        if len(_dimensions) > len(self.global_size()):
            raise Exception("reduce list is too much")

        dimension = _dimensions[0]
        if self.__objects[0].is_variable():
            global_size_list = self.global_size().pop()
            for _ in range(dimension):
                self.__objects.append(Variable(self.__type_id, default_value[self.__type_id], global_size_list))
        else:
            for _ in range(dimension):
                self.__objects.append(Value(self.__type_id, default_value[self.__type_id]))

        other_dimensions = _dimensions[1:]
        if len(other_dimensions) > 0:
            for _object in self.__objects:
                _object.extent(other_dimensions)

    def __mx(self, _operator):
        corrects: int = 0
        if self.__objects[0].is_variable():
            for _object in self.__objects:
                corrects += _object.__mx(_operator)
        else:
            for _object in self.__objects:
                if _operator(_object.__value):
                    corrects += 1
        return corrects

    def __more_than_half(self, _corrects):
        global_size_list = self.global_size()
        elements_count: int = 1
        for el in global_size_list:
            elements_count *= el
        more_than_half_count = elements_count / 2 + 1
        if _corrects > more_than_half_count:
            return True
        return False

    def mxeq(self):
        return Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x == 0)), _dimensions=[1])

    def mxlt(self):
        return Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x < 0)), _dimensions=[1])

    def mxgt(self):
        return Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x > 0)), _dimensions=[1])

    def mxlte(self):
        return Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x <= 0)), _dimensions=[1])

    def mxgte(self):
        return Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x >= 0)), _dimensions=[1])

    def __el(self, _operator):
        if self.__objects[0].is_variable():
            for _object in self.__objects:
                _object.__el(_operator)
        else:
            for _object in self.__objects:
                _object.__value = _operator(_object.__value)

    def eleq(self):
        ret_var = self
        ret_var.__el(lambda x: x == 0)
        return ret_var

    def ellt(self):
        ret_var = self
        ret_var.__el(lambda x: x < 0)
        return ret_var

    def elgt(self):
        ret_var = self
        ret_var.__el(lambda x: x > 0)
        return ret_var

    def ellte(self):
        ret_var = self
        ret_var.__el(lambda x: x <= 0)
        return ret_var

    def elgte(self):
        ret_var = self
        ret_var.__el(lambda x: x >= 0)
        return ret_var

    def __NOT(self):
        if self.__objects[0].is_variable():
            for _object in self.__objects:
                _object.__NOT()
        else:
            for _object in self.__objects:
                _object.__value = not bool(_object.__value)

    def NOT(self):
        if self.__type_id != _BOOL_TYPE_ID_:
            raise Exception("typed not bool")
        ret_var = self
        ret_var.__NOT()
        return ret_var

    def __AND(self, other):
        if len(self.__objects) != len(other.__objects):
            raise Exception("dimensions are not equal")
        if self.__objects[0].is_variable():
            for i in range(len(self.__objects)):
                self.__objects[i].__AND(other.__objects[i])
        else:
            for i in range(len(self.__objects)):
                self.__objects[i].__value = bool(self.__objects[i].__value) and bool(other.__objects[i].__value)

    def AND(self, other):
        ret_var = self
        ret_var.__AND(other)
        return ret_var

    def mx_true(self):
        if self.__type_id != _BOOL_TYPE_ID_:
            raise Exception("typed not bool")
        return Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: bool(x) is True)), _dimensions=[1])

    def mx_false(self):
        if self.__type_id != _BOOL_TYPE_ID_:
            raise Exception("typed not bool")
        return Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: bool(x) is False)), _dimensions=[1])
