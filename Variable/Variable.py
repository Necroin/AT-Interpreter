import copy
import weakref

_BOOL_TYPE_ID_ = 0
_INT_TYPE_ID_ = 1

_VARIABLE_: bool = True
_NOT_VARIABLE_: bool = False


class reference_wrapper:
    def __init__(self, value):
        self.__value = [value]

    def get(self):
        return self.__value[0]

    def set(self, value):
        self.__value[0] = value
        return self


class Object:
    def __init__(self, type_id, variable_flag: bool):
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
        if self._Object__type_id != other._Object__type_id:
            raise Exception("types are not equal")
        self.__value += other.__value
        return self

    def __add__(self, other):
        ret_var = copy.deepcopy(self)
        ret_var += other
        return ret_var

    def __isub__(self, other):
        if self._Object__type_id != other._Object__type_id:
            raise Exception("types are not equal")
        self.__value -= other.__value
        return self

    def __sub__(self, other):
        ret_var = copy.deepcopy(self)
        ret_var += other
        return ret_var

    def __imul__(self, other):
        if self._Object__type_id != other._Object__type_id:
            raise Exception("types are not equal")
        self.__value *= other.__value
        return self

    def __mul__(self, other):
        ret_var = copy.deepcopy(self)
        ret_var *= other
        return ret_var

    def __itruediv__(self, other):
        if self._Object__type_id != other._Object__type_id:
            raise Exception("types are not equal")
        self.__value /= other.__value
        return self

    def __truediv__(self, other):
        ret_var = copy.deepcopy(self)
        ret_var /= other
        return ret_var


class Variable(Object):
    def __init__(self, _type_id, _init_value, _dimensions):
        super().__init__(_type_id, _VARIABLE_)
        self.__objects = []
        dimension = _dimensions[0]
        if dimension <= 0:
            raise Exception('invalid dimension')
        if len(_dimensions) > 1:
            other_dimensions = _dimensions[1:]
            for _ in range(dimension):
                self.__objects.append(reference_wrapper(Variable(_type_id, _init_value, other_dimensions)))
        else:
            for _ in range(dimension):
                self.__objects.append(reference_wrapper(Value(_type_id, _init_value)))

    def assign(self, _type_id, _value_array):
        if self._Object__type_id != _type_id:
            raise Exception("types are not equal")
        self.__objects.clear()
        for i in range(len(_value_array)):
            self.__objects.append(reference_wrapper(Value(_type_id, _value_array[i])))

    def is_trivial(self):
        if len(self.__objects) == 1 and self.__objects[0].get().is_variable() is False:
            return True
        return False

    def trivial_assignment(self, other):
        self.__objects[0].set(other)

    def get(self, dimensions):
        dimension = dimensions[0]
        if len(dimensions) > len(self.global_size()):
            raise Exception('dim list is too big')
        if dimension > len(self.__objects):
            raise Exception('dimension is too much')
        if len(dimensions) > 1:
            other_dimensions = dimensions[1:]
            return self.__objects[dimension].get().get(other_dimensions)
        else:
            if self.__objects[dimension].get().is_variable():
                return self.__objects[dimension]
            else:
                var = Variable(self._Object__type_id, 0, [1])
                var.__objects[0] = self.__objects[dimension]
                return reference_wrapper(var)

    def global_size(self):
        if self.__objects[0].get().is_variable():
            g_size = self.__objects[0].get().global_size()
            g_size.insert(0, len(self.__objects))
            return g_size
        return [len(self.__objects)]

    def size(self):
        return Variable(_INT_TYPE_ID_, 0, range(0)).assign(_INT_TYPE_ID_, self.global_size())

    def __iadd__(self, other):
        if self._Object__type_id != other._Object__type_id:
            raise Exception("types are not equal")
        for i in range(len(self.__objects)):
            self.__objects[i]._reference_wrapper__value[0] += other.__objects[i]._reference_wrapper__value[0]
        return self

    def __add__(self, other):
        ret_var = copy.deepcopy(self)
        ret_var += other
        return reference_wrapper(ret_var)

    def __isub__(self, other):
        if self._Object__type_id != other._Object__type_id:
            raise Exception("types are not equal")
        for i in range(len(self.__objects)):
            self.__objects[i]._reference_wrapper__value[0] -= other.__objects[i]._reference_wrapper__value[0]
        return self

    def __sub__(self, other):
        ret_var = copy.deepcopy(self)
        ret_var -= other
        return reference_wrapper(ret_var)

    def __imul__(self, other):
        if self._Object__type_id != other._Object__type_id:
            raise Exception("types are not equal")
        for i in range(len(self.__objects)):
            self.__objects[i]._reference_wrapper__value[0] *= other.__objects[i]._reference_wrapper__value[0]
        return self

    def __mul__(self, other):
        ret_var = copy.deepcopy(self)
        ret_var *= other
        return reference_wrapper(ret_var)

    def __itruediv__(self, other):
        if self._Object__type_id != other._Object__type_id:
            raise Exception("types are not equal")
        for i in range(len(self.__objects)):
            self.__objects[i]._reference_wrapper__value[0] /= other.__objects[i]._reference_wrapper__value[0]
        return self

    def __truediv__(self, other):
        ret_var = copy.deepcopy(self)
        ret_var /= other
        return reference_wrapper(ret_var)

    def logitize(self):
        if self._Object__type_id != _INT_TYPE_ID_:
            raise Exception("type is bool")
        if self.__objects[0].get().is_variable():
            for _object in self.__objects:
                _object.get().logitize()
        else:
            for _object in self.__objects:
                _object.get()._Value__value = bool(_object.get()._Value__value)
        return reference_wrapper(self)

    def digitize(self):
        if self._Object__type_id != _BOOL_TYPE_ID_:
            raise Exception("type is bool")
        if self.__objects[0].get().is_variable():
            for _object in self.__objects:
                _object.get().digitize()
        else:
            for _object in self.__objects:
                _object.get()._Value__value = int(_object.get()._Value__value)
        return reference_wrapper(self)

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
                _object.get().reduce(other_dimensions)

        return reference_wrapper(self)

    def extent(self, _dimensions):
        default_value = (True, 0)

        if len(_dimensions) > len(self.global_size()):
            raise Exception("reduce list is too much")

        dimension = _dimensions[0]
        if self.__objects[0].get().is_variable():
            global_size_list = self.global_size().pop()
            for _ in range(dimension):
                self.__objects.append(
                    reference_wrapper(
                        Variable(self._Object__type_id, default_value[self._Object__type_id], global_size_list)))
        else:
            for _ in range(dimension):
                self.__objects.append(
                    reference_wrapper(Value(self._Object__type_id, default_value[self._Object__type_id])))

        other_dimensions = _dimensions[1:]
        if len(other_dimensions) > 0:
            for _object in self.__objects:
                _object.get().extent(other_dimensions)

        return reference_wrapper(self)

    def __mx(self, _operator):
        corrects: int = 0
        if self.__objects[0].get().is_variable():
            for _object in self.__objects:
                corrects += _object.get().__mx(_operator)
        else:
            for _object in self.__objects:
                if _operator(_object.get()._Value__value):
                    corrects += 1
        return corrects

    def __more_than_half(self, _corrects):
        global_size_list = self.global_size()
        elements_count: int = 1
        for el in global_size_list:
            elements_count *= el
        more_than_half_count = elements_count // 2 + 1
        if _corrects >= more_than_half_count:
            return True
        return False

    def mxeq(self):
        return reference_wrapper(
            Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x == 0)), _dimensions=[1]))

    def mxlt(self):
        return reference_wrapper(
            Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x < 0)), _dimensions=[1]))

    def mxgt(self):
        return reference_wrapper(
            Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x > 0)), _dimensions=[1]))

    def mxlte(self):
        return reference_wrapper(
            Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x <= 0)), _dimensions=[1]))

    def mxgte(self):
        return reference_wrapper(
            Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: x >= 0)), _dimensions=[1]))

    def __el(self, _operator):
        if self.__objects[0].get().is_variable():
            for _object in self.__objects:
                _object.get().__el(_operator)
        else:
            for _object in self.__objects:
                _object.get()._Value__value = _operator(_object.get()._Value__value)

    def eleq(self):
        ret_var = copy.deepcopy(self)
        ret_var.__el(lambda x: x == 0)
        return reference_wrapper(ret_var)

    def ellt(self):
        ret_var = copy.deepcopy(self)
        ret_var.__el(lambda x: x < 0)
        return reference_wrapper(ret_var)

    def elgt(self):
        ret_var = copy.deepcopy(self)
        ret_var.__el(lambda x: x > 0)
        return reference_wrapper(ret_var)

    def ellte(self):
        ret_var = copy.deepcopy(self)
        ret_var.__el(lambda x: x <= 0)
        return reference_wrapper(ret_var)

    def elgte(self):
        ret_var = copy.deepcopy(self)
        ret_var.__el(lambda x: x >= 0)
        return reference_wrapper(ret_var)

    def __NOT(self):
        if self.__objects[0].get().is_variable():
            for _object in self.__objects:
                _object.get().__NOT()
        else:
            for _object in self.__objects:
                _object.get()._Value__value = not bool(_object.get()._Value__value)

    def NOT(self):
        if self.__type_id != _BOOL_TYPE_ID_:
            raise Exception("typed not bool")
        ret_var = self
        ret_var.__NOT()
        return reference_wrapper(ret_var)

    def __AND(self, other):
        if len(self.__objects) != len(other.__objects):
            raise Exception("dimensions are not equal")
        if self.__objects[0].get().is_variable():
            for i in range(len(self.__objects)):
                self.__objects[i].get().__AND(other.__objects[i])
        else:
            for i in range(len(self.__objects)):
                self.__objects[i].get()._Value__value = bool(self.__objects[i].get()._Value__value) and bool(
                    other.__objects[i].get()._Value__value)

    def AND(self, other):
        ret_var = copy.deepcopy(self)
        ret_var.__AND(other)
        return reference_wrapper(ret_var)

    def mx_true(self):
        if self._Object__type_id != _BOOL_TYPE_ID_:
            raise Exception("typed not bool")
        return reference_wrapper(
            Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: bool(x) is True)), _dimensions=[1]))

    def mx_false(self):
        if self._Object__type_id != _BOOL_TYPE_ID_:
            raise Exception("typed not bool")
        return reference_wrapper(
            Variable(_BOOL_TYPE_ID_, self.__more_than_half(self.__mx(lambda x: bool(x) is False)), _dimensions=[1]))

    def __bool__(self):
        return bool(self.__objects[0].get()._Value__value)
