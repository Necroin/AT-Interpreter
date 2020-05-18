import ply.yacc as yacc
from ply.lex import LexError
import sys
from Robot.Robot import robot
from Lexer.lexer import lexer
from Operations.operations import *
from Variable.Variable import _BOOL_TYPE_ID_, _INT_TYPE_ID_


class parser(object):
    tokens = lexer.tokens
    precedence = lexer.precedence

    def __init__(self):
        self.functions_map = {}
        self.__variables_map = {}
        self.good = True
        self.lexer = lexer()
        self.parser = yacc.yacc(module=self)

    def parse(self, s):
        try:
            self.parser.parse(s)
            return self.functions_map, self.good
        except LexError:
            sys.stderr.write(f'Illegal token {s}\n')

    @staticmethod
    def p_program_statements(p):
        """program: functions"""

    @staticmethod
    def p_functions(p):
        """functions: function functions
                    | function"""

    def p_function(self, p):
        """function: fun_decl statements RESULT VARIABLE"""

        p[0] = Function(functions_map=self.functions_map,
                        variables_map=self.__variables_map,
                        function_name=p[1][0],
                        parameters=p[1][1],
                        operations=p[2],
                        result_var=NamedOperand(self.__variables_map, p[4].value, p[1][2]),
                        lineno=p[1][2]
                        )
        self.functions_map[p[1][0]] = [p[0], None]
        self.__variables_map = {}

    @staticmethod
    def p_fun_decl(p):
        """fun_decl: TASK VARIABLE parameters"""
        p[0] = [p[2].value, p[3], p.lineno(1)]

    @staticmethod
    def p_parameters(p):
        """parameters: parameters VARIABLE
                     | VARIABLE"""
        if len(p) == 3:
            p[0] = p[1].append(p[2].value)
        else:
            p[0] = [p[1].value]

    @staticmethod
    def p_parameters_empty(p):
        """parameters: empty"""
        p[0] = []

    @staticmethod
    def p_statements(p):
        """statements: statements statement
                     | statement"""
        if len(p) == 3:
            p[0] = p[1].append(p[2])
        else:
            p[0] = [p[1]]

    @staticmethod
    def p_statement(p):
        """statement: PLEASE statement THANKS NEWLINE
                     | var_declaration NEWLINE
                     | expression NEWLINE
                     | for
                     | switch
                     | command NEWLINE
                     | empty NEWLINE"""
        if len(p) == 5:
            p[0] = p[2]
        else:
            p[0] = p[1]

    @staticmethod
    def p_command_move(p):
        """command: MOVE"""
        p[0] = Command(
            operand=robot,
            command=lambda x: x.move(),
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_command_rotate_left(p):
        """command: ROTATE_LEFT"""
        p[0] = Command(
            operand=robot,
            command=lambda x: x.rotate_left(),
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_command_rotate_right(p):
        """command: ROTATE_RIGHT"""
        p[0] = Command(
            operand=robot,
            command=lambda x: x.rotate_right(),
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_command_get_environment(p):
        """command: GET_ENVIRONMENT"""
        p[0] = Command(
            operand=robot,
            command=lambda x: x.get_environment(),
            lineno=p.lineno(1)
        )

    def p_for(self, p):
        """for : FOR VARIABLE BOUNDARY VARIABLE STEP VARIABLE statements_group"""
        lineno = p.lineno(1)
        p[0] = For(
            counter=NamedOperand(self.__variables_map, p[2].value, lineno),
            boundary=NamedOperand(self.__variables_map, p[4].value, lineno),
            step=NamedOperand(self.__variables_map, p[6].value, lineno),
            operations=p[7],
            lineno=lineno
        )

    @staticmethod
    def p_statements_group_statements(p):
        """statements_group: LBRACKET NEWLINE statements RBRACKET NEWLINE"""
        p[0] = p[2]

    @staticmethod
    def p_statements_group_statement(p):
        """statements_group: statement"""
        p[0] = [p[1]]

    @staticmethod
    def p_switch_true_false(p):
        """switch: SWITCH expression NEWLINE
        TRUE  statements_group
        FALSE statements_group"""
        p[0] = Conditional(
            invert=lambda x: x,
            condition=p[1],
            if_true=p[3],
            if_false=p[5],
            lineno=p[1].lineno()
        )

    @staticmethod
    def p_switch_false_true(p):
        """switch: SWITCH expression NEWLINE
        FALSE statements_group
        TRUE  statements_group"""
        p[0] = Conditional(
            invert=lambda x: not x,
            condition=p[2],
            if_true=p[5],
            if_false=p[3],
            lineno=p[1].lineno()
        )

    @staticmethod
    def p_assignment(p):
        """assignment: expression ASSIGNMENT expression"""

    @staticmethod
    def p_binary_expression(p):
        """expression: expression binary_operator expression"""
        p[0] = BinaryOperator(p[2], p[1], p[3], p[1].lineno())

    @staticmethod
    def p_binary_operator_plus(p):
        """binary_operator : PLUS"""
        p[0] = lambda left, right: left + right

    @staticmethod
    def p_binary_operator_minus(p):
        """binary_operator : MINUS"""
        p[0] = lambda left, right: left - right

    @staticmethod
    def p_binary_operator_multiply(p):
        """binary_operator : MULTIPLY"""
        p[0] = lambda left, right: left * right

    @staticmethod
    def p_binary_operator_divide(p):
        """binary_operator : DIVIDE"""
        p[0] = lambda left, right: left / right

    @staticmethod
    def p_binary_operator_AND(p):
        """binary_operator: AND_OPERATOR"""
        p[0] = lambda left, right: left.AND(right)

    @staticmethod
    def p_unary_expression(p):
        """expression: unary_operator expression"""
        p[0] = UnaryOperator(p[1], p[2], p[2].lineno())

    @staticmethod
    def p_unary_operator_mxeq(p):
        """unary_operator: MXEQ_OPERATOR"""
        p[0] = lambda operand: operand.mxeq()

    @staticmethod
    def p_unary_operator_mxlt(p):
        """unary_operator: MXLT_OPERATOR"""
        p[0] = lambda operand: operand.mxlt()

    @staticmethod
    def p_unary_operator_mxgt(p):
        """unary_operator: MXGT_OPERATOR"""
        p[0] = lambda operand: operand.mxgt()

    @staticmethod
    def p_unary_operator_mxlte(p):
        """unary_operator: MXLTE_OPERATOR"""
        p[0] = lambda operand: operand.mxlte()

    @staticmethod
    def p_unary_operator_mxgte(p):
        """unary_operator: MXGTE_OPERATOR"""
        p[0] = lambda operand: operand.mxgte()

    @staticmethod
    def p_unary_operator_eleq(p):
        """unary_operator: ELEQ_OPERATOR"""
        p[0] = lambda operand: operand.eleq()

    @staticmethod
    def p_unary_operator_ellt(p):
        """unary_operator: ELLT_OPERATOR"""
        p[0] = lambda operand: operand.ellt()

    @staticmethod
    def p_unary_operator_elgt(p):
        """unary_operator: ELGT_OPERATOR"""
        p[0] = lambda operand: operand.elgt()

    @staticmethod
    def p_unary_operator_ellte(p):
        """unary_operator: ELLTE_OPERATOR"""
        p[0] = lambda operand: operand.ellte()

    @staticmethod
    def p_unary_operator_elgte(p):
        """unary_operator: ELGTE_OPERATOR"""
        p[0] = lambda operand: operand.elgte()

    @staticmethod
    def p_unary_operator_NOT(p):
        """unary_operator: NOT_OPERATOR"""
        p[0] = lambda operand: operand.NOT()

    @staticmethod
    def p_unary_operator_mx_true(p):
        """unary_operator: MXTRUE_OPERATOR"""
        p[0] = lambda operand: operand.mx_true()

    @staticmethod
    def p_unary_operator_mx_false(p):
        """unary_operator: MXFALSE_OPERATOR"""
        p[0] = lambda operand: operand.mx_false()

    @staticmethod
    def p_expressions(p):
        """expression: base_value
                     | assignment
                     | indexing
                     | do
                     | get"""
        p[0] = p[1]

    def p_do(self, p):
        """do: DO VARIABLE call_parameters"""
        p[0] = FunctionCall(
            functions_map=self.functions_map,
            function_name=p[2],
            call_parameters=p[3],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_call_parameters(p):
        """call_parameters: call_parameters call_parameter
                          | call_parameters"""
        if len(p) == 3:
            p[0] = p[1].append(p[2])
        else:
            p[0] = [p[1]]

    def p_call_parameter(self, p):
        """call_parameter: VARIABLE"""
        p[0] = NamedOperand(self.__variables_map, p[1].value, p.lineno(1))

    def p_get(self, p):
        """get: GET VARIABLE"""
        p[0] = GetFunctionResult(
            functions_map=self.functions_map,
            function_name=p[2],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_expression_bracket(p):
        """expression: LBRACKET expression RBRACKET"""
        p[0] = p[2]

    def p_expression_variable(self, p):
        """expression: VARIABLE"""
        p[0] = NamedOperand(self.__variables_map, p[1].value, p.lineno(1))

    @staticmethod
    def p_number_oct(p):
        """number : OCT_NUMBER"""
        p[0] = Operand(_INT_TYPE_ID_, p[1].value, p.lineno(1))

    @staticmethod
    def p_number_dec(p):
        """number : DEC_NUMBER"""
        p[0] = Operand(_INT_TYPE_ID_, p[1].value, p.lineno(1))

    @staticmethod
    def p_number_hex(p):
        """number : HEX_NUMBER"""
        p[0] = Operand(_INT_TYPE_ID_, p[1].value, p.lineno(1))

    @staticmethod
    def p_boolean_true(p):
        """boolean: TRUE"""
        p[0] = Operand(_BOOL_TYPE_ID_, True, p.lineno(1))

    @staticmethod
    def p_boolean_false(p):
        """boolean: FALSE"""
        p[0] = Operand(_BOOL_TYPE_ID_, False, p.lineno(1))

    @staticmethod
    def p_base_values(p):
        """base_values: number
                      | boolean"""
        p[0] = p[1]

    @staticmethod
    def p_initializer(p):
        """initializer: base_values"""
        p[0] = p[1]

    def p_var_declaration_dim(self, p):
        """var_declaration: VAR VARIABLE OS_BRACKET dimensions CS_BRACKET ASSIGNMENT initializer"""
        p[0] = VarDeclaration(
            variables_map=self.__variables_map,
            variable_name=p[2].value,
            dimensions=p[4].execute(),
            type_id=p[7].type(),
            init_value=p[7].value(),
            lineno=p.lineno(1)
        )

    def p_var_declaration(self, p):
        """var_declaration: VAR VARIABLE ASSIGNMENT initializer"""
        p[0] = VarDeclaration(
            variables_map=self.__variables_map,
            variable_name=p[2].value,
            dimensions=[1],
            type_id=p[7].type(),
            init_value=p[7].value(),
            lineno=p.lineno(1)
        )

    def p_indexing(self, p):
        """indexing: expression OS_BRACKET dimensions CS_BRACKET"""
        p[0] = Indexing(
            variables_map=self.__variables_map,
            operand=p[1],
            dimensions=p[3],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_dimensions(p):
        """dimensions: dimensions COMMA dimension
                     | dimension"""
        if len(p) == 3:
            p[0] = p[1].append(p[3])
        else:
            p[0] = p[1]

    @staticmethod
    def p_dimension(p):
        """dimension : expression"""
        p[0] = Dimensions(p[1].lineno()).append(p[1])

    @staticmethod
    def p_empty(p):
        """empty : """
        p[0] = Empty()
