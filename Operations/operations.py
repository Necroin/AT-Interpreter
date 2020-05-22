import copy

from Variable.Variable import Variable, reference_wrapper


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
        return reference_wrapper(Variable(self.__type_id, self.__value, [1]))

    def type(self):
        return self.__type_id

    def value(self):
        return self.__value


class NamedOperand(OperationObject):
    def __init__(self, function_stack, variable_name, lineno):
        super().__init__(lineno)
        self.__function_stack = function_stack
        self.__variable_name = variable_name
        self.__lineno = lineno

    def execute(self):
        variable = self.__function_stack[-1].get(self.__variable_name, None)
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
    def __init__(self, function_stack, variable_name, dimensions, type_id, init_value, lineno):
        super().__init__(lineno)
        self.__function_stack = function_stack
        self.__dimensions = dimensions
        self.__init_value = init_value
        self.__variable_name = variable_name
        self.__type_id = type_id

    def execute(self):
        if self.__function_stack[-1].get(self.__variable_name, None) is not None:
            raise Exception('Error: this var already exist, at line ' + str(self.__lineno) + '\n')
        self.__function_stack[-1][self.__variable_name] = reference_wrapper(Variable(self.__type_id,
                                                                                     self.__init_value,
                                                                                     self.__dimensions.execute()))


class VarDeclarationFromExpr(OperationObject):
    def __init__(self, function_stack, variable_name, expression, lineno):
        super().__init__(lineno)
        self.__function_stack = function_stack
        self.__expression = expression
        self.__variable_name = variable_name

    def execute(self):
        if self.__function_stack[-1].get(self.__variable_name, None) is not None:
            raise Exception('Error: this var already exist, at line ' + str(self.__lineno) + '\n')
        self.__function_stack[-1][self.__variable_name] = reference_wrapper(self.__expression.execute().get())


class Dimensions(OperationObject):
    def __init__(self, dimensions, lineno):
        super().__init__(lineno)
        self.__dimensions = dimensions

    def execute(self):
        executed_dimensions = []
        for i in range(len(self.__dimensions)):
            executed_dimensions.append(self.__dimensions[i].execute())
        for i in range(len(executed_dimensions)):
            if executed_dimensions[i].get().is_trivial():
                executed_dimensions[i] = int(executed_dimensions[i].get()._Variable__objects[0].get()._Value__value)
            else:
                raise Exception('dimension is not trivial, at line ' + str(self.__lineno) + '\n')
        return executed_dimensions


class Indexing(OperationObject):
    def __init__(self, operand, dimensions, lineno):
        super().__init__(lineno)
        self.__dimensions = dimensions
        self.__operand = operand

    def execute(self):
        dimensions = self.__dimensions.execute()
        for i in range(len(dimensions)):
            dimensions[i] -= 1
        return self.__operand.execute().get().get(dimensions)


class Assignment(OperationObject):
    def __init__(self, operand, other, lineno):
        super().__init__(lineno)
        self.__operand = operand
        self.__other = other

    def execute(self):
        variable = self.__operand.execute()
        other = self.__other.execute()
        if variable.get().is_trivial and other.get().is_trivial():
            variable.get().trivial_assignment(other.get()._Variable__objects[0].get())
        elif variable.get().is_trivial() and not other.get().is_trivial():
            t = copy.deepcopy(other.get())
            variable.get().trivial_assignment(t)
            variable.set(t)
        else:
            variable.set(copy.deepcopy(other.get()))
        return variable


class Conditional(OperationObject):
    def __init__(self, invert, condition, if_true, if_false, lineno):
        super().__init__(lineno)
        self.__condition = condition
        self.__if_true = if_true
        self.__if_false = if_false
        self.__invert = invert

    def execute(self):
        cond_res = self.__condition.execute().get()
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
    def __init__(self, functions_map, stack, function_name, parameters, operations, result_var, lineno):
        super().__init__(lineno)
        self.__operations = operations
        self.__result_var = result_var
        self.__functions_map = functions_map
        self.__function_name = function_name
        self.__parameters = parameters
        self.__stack = stack

    def call(self, call_parameters):
        if len(call_parameters) != len(self.__parameters):
            raise Exception("incorrect arguments count")
        call_parameters_dict = {}
        for i in range(len(self.__parameters)):
            call_parameters_dict[self.__parameters[i]] = call_parameters[i].execute()
        self.__stack.append(call_parameters_dict)
        try:
            for _operation in self.__operations:
                _operation.execute()
            result = self.__result_var.execute()
            self.__stack.pop()
            return result
        except Exception as exception:
            raise exception


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
                result = function[0].call(self.__call_parameters)
                function[1] = reference_wrapper(result.get())
                return result
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
            return reference_wrapper(function[1].get())
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
