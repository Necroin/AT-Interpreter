from Variable.Variable import Variable


class OperationObject:
    def __init__(self, lineno):
        self.__lineno = lineno

    def lineno(self):
        return self.__lineno


class Empty:
    def execute(self):
        pass


class Operand(OperationObject):
    def __init__(self, type_id, value, lineno):
        super().__init__(lineno)
        self.__value = value
        self.__type_id = type_id

    def execute(self):
        return self.__value

    def type(self):
        return self.__type_id

    def value(self):
        return self.__value


class NamedOperand(OperationObject):
    def __init__(self, variables_map: dict, variable_name, lineno):
        super().__init__(lineno)
        self.__variables_map = variables_map
        self.__variable_name = variable_name
        self.__lineno = lineno

    def execute(self):
        variable = self.__variables_map.get(self.__variable_name, None)
        if variable is None:
            raise Exception('variable ' + self.__variable_name + 'not defined, at line ' + str(self.__lineno))
        return variable


class BinaryOperator(OperationObject):
    def __init__(self, operator, left, right, lineno):
        super().__init__(lineno)
        self.__operator = operator
        self.__left = left
        self.__right = right

    def execute(self):
        return self.__operator(self.__left.execute(), self.__right.execute())


class UnaryOperator(OperationObject):
    def __init__(self, operator, operand, lineno):
        super().__init__(lineno)
        self.__operator = operator
        self.__operand = operand

    def execute(self):
        return self.__operator(self.__operand.execute())


class VarDeclaration(OperationObject):
    def __init__(self, variables_map: dict, variable_name, dimensions, type_id, init_value, lineno):
        super().__init__(lineno)
        self.__variables_map = variables_map
        self.__dimensions = dimensions
        self.__init_value = init_value
        self.__variable_name = variable_name
        self.__type_id = type_id

    def execute(self):
        if self.__variables_map.get(self.__variable_name, None) is not None:
            raise Exception('Error: this var already exist, at line ' + str(self.__lineno) + '\n')
        self.__variables_map[self.__variable_name] = Variable(self.__type_id,
                                                              self.__init_value,
                                                              self.__dimensions.execute())


class Dimensions(OperationObject):
    __dimensions = []

    def __init__(self, lineno):
        super().__init__(lineno)

    def append(self, dimension):
        self.__dimensions.append(dimension)

    def execute(self):
        for i in range(len(self.__dimensions)):
            if self.__dimensions[i].is_trivial():
                self.__dimensions[i] = int(self.__dimensions[i].__objects[0].value)
            else:
                raise Exception('dimension is not trivial, at line ' + str(self.__lineno) + '\n')
        return self.__dimensions


class Indexing(OperationObject):
    def __init__(self, variables_map: dict, operand, dimensions, lineno):
        super().__init__(lineno)
        self.__dimensions = dimensions
        self.__variables_map = variables_map
        self.__operand = operand

    def execute(self):
        return self.__operand.execute().get(self.__dimensions.execute())


class Assignment(OperationObject):
    def __init__(self, variables_map: dict, operand, other, lineno):
        super().__init__(lineno)
        self.__variables_map = variables_map
        self.__operand = operand
        self.__other = other

    def execute(self):
        variable = self.__operand.execute()
        if variable.is_trivial() and self.__other.is_trivial():
            variable.trivial_assignment(self.__other)
        elif variable.is_trivial() and not self.__other.is_trivial():
            variable.trivial_assignment(self.__other)
            variable = variable.__objects[0]
        else:
            variable = self.__other
        return variable


class Conditional(OperationObject):
    def __init__(self, invert, condition, if_true, if_false, lineno):
        super().__init__(lineno)
        self.__condition = condition
        self.__if_true = if_true
        self.__if_false = if_false
        self.__invert = invert

    def execute(self):
        cond_res = self.__condition.execute()
        if cond_res.is_trivial():
            if self.__invert(bool(cond_res)):
                for statement in self.__if_true:
                    statement.execute()
            else:
                for statement in self.__if_false:
                    statement.execute()
        else:
            raise Exception('condition result is not trivial')


class Function(OperationObject):
    def __init__(self, functions_map, variables_map, function_name, parameters, operations, result_var, lineno):
        super().__init__(lineno)
        self.__operations = operations
        self.__result_var = result_var
        self.__functions_map = functions_map
        self.__function_name = function_name
        self.__parameters = parameters
        self.__stack = []
        self.__variables_map = variables_map

    def call(self, call_parameters):
        if len(call_parameters) != len(self.__parameters):
            raise Exception("incorrect arguments count")
        for i in range(len(self.__parameters)):
            self.__variables_map[self.__parameters[i]] = call_parameters[i].execute()
        try:
            for _operation in self.__operations:
                _operation.execute()
            return self.__result_var.execute()
        except Exception as exception:
            raise exception

    def push(self):
        self.__stack.append(self.__variables_map)
        self.__variables_map = {}

    def pop(self):
        self.__variables_map = self.__stack[-1]
        self.__stack.pop()


class FunctionCall(OperationObject):
    def __init__(self, functions_map, function_name, call_parameters, lineno):
        super().__init__(lineno)
        self.__functions_map = functions_map
        self.__function_name = function_name
        self.__call_parameters = call_parameters

    def execute(self):
        try:
            function = self.__functions_map.get(self.__function_name, None)
            if function is not None:
                function[0].push()
                function[1] = function[0].call(self.__call_parameters)
                function[0].pop()
            else:
                raise Exception('function not exist')
        except Exception as exception:
            raise exception


class GetFunctionResult(OperationObject):
    def __init__(self, functions_map, function_name, lineno):
        super().__init__(lineno)
        self.__functions_map = functions_map
        self.__function_name = function_name

    def execute(self):
        function = self.__functions_map.get(self.__function_name, None)
        if function is not None:
            return function[1]
        else:
            raise Exception('function not exist')


class For(OperationObject):
    def __init__(self, counter, boundary, step, operations, lineno):
        super().__init__(lineno)
        self.__counter = counter
        self.__boundary = boundary
        self.__step = step
        self.__operations = operations

    def execute(self):
        counter = self.__counter.execute()
        boundary = self.__boundary.execute()
        step = self.__step.execute()
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # РЕАЛИЗАЦИЯ
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for operation in self.__operations:
            operation.execute()


class Command(OperationObject):
    def __init__(self, operand, command, lineno):
        super().__init__(lineno)
        self.__operand = operand
        self.__command = command

    def execute(self):
        self.__command(self.__operand)
