import ply.yacc as yacc
from ply.lex import LexError
import sys
import Robot.Robot
from Lexer.lexer import lexer
from Operations.operations import *
from Variable.Variable import _BOOL_TYPE_ID_, _INT_TYPE_ID_


class parser(object):
    tokens = lexer.tokens
    precedence = lexer.precedence

    def __init__(self):
        self.functions_map = {}
        self.__function_stack = []
        self.good = True
        self.lexer = lexer()
        self.parser = yacc.yacc(module=self)

    def parse(self, data):
        try:
            self.parser.parse(data, debug=False)
            return self.functions_map, self.good
        except LexError:
            sys.stderr.write(f'Illegal token {data}\n')

    @staticmethod
    def p_program_statements(p):
        """program : functions"""

    @staticmethod
    def p_functions(p):
        """functions : function functions
                     | function"""

    def p_function(self, p):
        """function : func_decl NEWLINE func_body RESULT expression NEWLINE"""

        p[0] = Function(functions_map=self.functions_map,
                        stack=self.__function_stack,
                        function_name=p[1][0],
                        parameters=p[1][1],
                        operations=p[3],
                        result_var=p[5],
                        lineno=p[1][2]
                        )
        self.functions_map[p[1][0]] = [p[0], None]
        self.__function_stack = []

    @staticmethod
    def p_func_body(p):
        """func_body : statements"""
        p[0] = p[1]

    @staticmethod
    def p_func_body_empty(p):
        """func_body : empty"""
        p[0] = []

    @staticmethod
    def p_func_decl(p):
        """func_decl : TASK VARIABLE parameters"""
        p[0] = [p[2], p[3], p.lineno(1)]

    @staticmethod
    def p_func_decl_error(p):
        """func_decl : TASK error"""
        p[0] = ["", [], p.lineno(1)]
        sys.stderr.write(f'>>> incorrect function declaration, at {p.lineno(1)}  line \n')

    @staticmethod
    def p_parameters(p):
        """parameters : VARIABLE parameters
                      | VARIABLE"""
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0]: list = [p[1]]

    @staticmethod
    def p_parameters_empty(p):
        """parameters : empty"""
        p[0] = []

    @staticmethod
    def p_parameters_error(p):
        """parameters : error"""
        p[0] = []
        sys.stderr.write(f'>>> incorrect parameters setting, at {p.lineno(1)}  line \n')

    @staticmethod
    def p_statements(p):
        """statements : statement statements
                      | statement"""
        if len(p) == 3:
            p[0] = [p[1][0], p[1][1]] + p[2]
        else:
            p[0]: list = [p[1][0], p[1][1]]

    @staticmethod
    def p_statement(p):
        """statement : PLEASE statement THANKS NEWLINE
                     | PLEASE statement NEWLINE
                     | var_declaration NEWLINE
                     | expression NEWLINE
                     | for
                     | switch
                     | command NEWLINE
                     | print NEWLINE
                     | print_word NEWLINE
                     | empty NEWLINE"""
        if len(p) == 5:
            p[0] = [p[2][0], Command(operand=Robot.Robot.robot, command=lambda x: x.get().give_mood_points(4),
                                     lineno=p.lineno(1))]
        elif len(p) == 4:
            p[0] = [p[2][0], Command(operand=Robot.Robot.robot, command=lambda x: x.get().give_mood_points(2),
                                     lineno=p.lineno(1))]
        else:
            p[0] = [p[1], Command(operand=Robot.Robot.robot, command=lambda x: x.get().give_mood_points(-4),
                                  lineno=p[1].lineno())]

    @staticmethod
    def p_print_word(p):
        """print_word : PRINT QUOTE VARIABLE QUOTE"""
        p[0] = Empty()  # PrintStr(p[3], p.lineno(1))

    @staticmethod
    def p_print(p):
        """print : PRINT expression"""
        p[0] = Empty()  # Print(p[2], p.lineno(1))

    @staticmethod
    def p_statement_thanks(p):
        """statement : statement THANKS NEWLINE"""
        p[0] = [p[1][0],
                Command(operand=Robot.Robot.robot, command=lambda x: x.get().give_mood_points(2), lineno=p[1].lineno())]

    @staticmethod
    def p_command_move(p):
        """command : MOVE"""
        p[0] = Command(
            operand=Robot.Robot.robot,
            command=lambda x: x.get().move(),
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_command_rotate_left(p):
        """command : ROTATE LEFT"""
        p[0] = Command(
            operand=Robot.Robot.robot,
            command=lambda x: x.get().rotate_left(),
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_command_rotate_right(p):
        """command : ROTATE RIGHT"""
        p[0] = Command(
            operand=Robot.Robot.robot,
            command=lambda x: x.get().rotate_right(),
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_expression_get_environment(p):
        """expression : GET ENVIRONMENT"""
        p[0] = Command(
            operand=Robot.Robot.robot,
            command=lambda x: x.get().get_environment(),
            lineno=p.lineno(1)
        )

    def p_for(self, p):
        """for : FOR VARIABLE BOUNDARY VARIABLE STEP VARIABLE statements_group"""
        lineno = p.lineno(1)
        p[0] = For(
            counter=NamedOperand(self.__function_stack, p[2], lineno),
            boundary=NamedOperand(self.__function_stack, p[4], lineno),
            step=NamedOperand(self.__function_stack, p[6], lineno),
            operations=p[7],
            lineno=lineno
        )

    @staticmethod
    def p_for_error(p):
        """for : FOR error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> incorrect for construction using, at {p.lineno(1)}  line \n')

    @staticmethod
    def p_statements_group_statements(p):
        """statements_group : LBRACKET NEWLINE statements RBRACKET NEWLINE"""
        p[0] = p[3]

    @staticmethod
    def p_statements_group_statement(p):
        """statements_group : statement"""
        p[0] = [p[1][0], p[1][1]]

    @staticmethod
    def p_statements_group_empty(p):
        """statements_group : LBRACKET RBRACKET NEWLINE"""
        p[0] = []

    @staticmethod
    def p_switch_true_false(p):
        """switch : SWITCH expression NEWLINE TRUE statements_group FALSE statements_group"""
        p[0] = Conditional(
            invert=lambda condition: condition,
            condition=p[2],
            if_true=p[5],
            if_false=p[7],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_switch_false_true(p):
        """switch : SWITCH expression NEWLINE FALSE statements_group TRUE statements_group"""
        p[0] = Conditional(
            invert=lambda condition: not condition,
            condition=p[2],
            if_true=p[7],
            if_false=p[5],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_switch_true_only_true(p):
        """switch : SWITCH expression NEWLINE TRUE statements_group"""
        p[0] = Conditional(
            invert=lambda condition: condition,
            condition=p[2],
            if_true=p[5],
            if_false=[Empty()],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_switch_true_only_false(p):
        """switch : SWITCH expression NEWLINE FALSE statements_group"""
        p[0] = Conditional(
            invert=lambda condition: condition,
            condition=p[2],
            if_true=[Empty()],
            if_false=p[5],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_switch_error(p):
        """switch : SWITCH error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> incorrect switch construction using, at {p.lineno(1)}  line \n')

    @staticmethod
    def p_binary_expression(p):
        """expression : expression binary_operator expression"""
        p[0] = BinaryOperator(p[2], p[1], p[3], p[1].lineno())

    @staticmethod
    def p_binary_operator_plus(p):
        """binary_operator : PLUS"""
        p[0] = lambda left, right: left.get() + right.get()

    @staticmethod
    def p_binary_operator_minus(p):
        """binary_operator : MINUS"""
        p[0] = lambda left, right: left.get() - right.get()

    @staticmethod
    def p_binary_operator_multiply(p):
        """binary_operator : MULTIPLY"""
        p[0] = lambda left, right: left.get() * right.get()

    @staticmethod
    def p_binary_operator_divide(p):
        """binary_operator : DIVIDE"""
        p[0] = lambda left, right: left.get() / right.get()

    @staticmethod
    def p_binary_operator_AND(p):
        """binary_operator : AND_OPERATOR"""
        p[0] = lambda left, right: left.get().AND(right.get())

    @staticmethod
    def p_unary_expression(p):
        """expression : unary_operator expression"""
        p[0] = UnaryOperator(p[1], p[2], p[2].lineno())

    @staticmethod
    def p_unary_operator_mxeq(p):
        """unary_operator : MXEQ_OPERATOR"""
        p[0] = lambda operand: operand.get().mxeq()

    @staticmethod
    def p_unary_operator_mxlt(p):
        """unary_operator : MXLT_OPERATOR"""
        p[0] = lambda operand: operand.get().mxlt()

    @staticmethod
    def p_unary_operator_mxgt(p):
        """unary_operator : MXGT_OPERATOR"""
        p[0] = lambda operand: operand.get().mxgt()

    @staticmethod
    def p_unary_operator_mxlte(p):
        """unary_operator : MXLTE_OPERATOR"""
        p[0] = lambda operand: operand.get().mxlte()

    @staticmethod
    def p_unary_operator_mxgte(p):
        """unary_operator : MXGTE_OPERATOR"""
        p[0] = lambda operand: operand.get().mxgte()

    @staticmethod
    def p_unary_operator_eleq(p):
        """unary_operator : ELEQ_OPERATOR"""
        p[0] = lambda operand: operand.get().eleq()

    @staticmethod
    def p_unary_operator_ellt(p):
        """unary_operator : ELLT_OPERATOR"""
        p[0] = lambda operand: operand.get().ellt()

    @staticmethod
    def p_unary_operator_elgt(p):
        """unary_operator : ELGT_OPERATOR"""
        p[0] = lambda operand: operand.get().elgt()

    @staticmethod
    def p_unary_operator_ellte(p):
        """unary_operator : ELLTE_OPERATOR"""
        p[0] = lambda operand: operand.get().ellte()

    @staticmethod
    def p_unary_operator_elgte(p):
        """unary_operator : ELGTE_OPERATOR"""
        p[0] = lambda operand: operand.get().elgte()

    @staticmethod
    def p_unary_operator_NOT(p):
        """unary_operator : NOT_OPERATOR"""
        p[0] = lambda operand: operand.get().NOT()

    @staticmethod
    def p_unary_operator_mx_true(p):
        """unary_operator : MXTRUE_OPERATOR"""
        p[0] = lambda operand: operand.get().mx_true()

    @staticmethod
    def p_unary_operator_mx_false(p):
        """unary_operator : MXFALSE_OPERATOR"""
        p[0] = lambda operand: operand.get().mx_false()

    @staticmethod
    def p_unary_operator_size(p):
        """unary_operator : SIZE_OPERATOR"""
        p[0] = lambda operand: operand.get().size()

    @staticmethod
    def p_unary_operator_logitize(p):
        """unary_operator : LOGITIZE_OPERATOR"""
        p[0] = lambda operand: operand.get().logitize()

    @staticmethod
    def p_unary_operator_digitize(p):
        """unary_operator : DIGITIZE_OPERATOR"""
        p[0] = lambda operand: operand.get().digitize()

    @staticmethod
    def p_expressions(p):
        """expression : base_values
                      | assignment
                      | indexing
                      | do
                      | get
                      | reduce
                      | extend"""
        p[0] = p[1]

    @staticmethod
    def p_assignment(p):
        """assignment : expression ASSIGNMENT expression"""
        p[0] = Assignment(p[1], p[3], p.lineno(2))

    @staticmethod
    def p_reduce(p):
        """reduce : REDUCE_OPERATOR expression dimensions"""
        p[0] = BinaryOperator(
            left=p[2],
            right=p[3],
            operator=lambda operand, dimensions: operand.get().reduce(dimensions),
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_reduce_error(p):
        """reduce : REDUCE_OPERATOR error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> incorrect reduce operator using, at {p.lineno(1)}  line \n')

    @staticmethod
    def p_extend(p):
        """extend : EXTEND_OPERATOR expression dimensions"""
        p[0] = BinaryOperator(
            left=p[2],
            right=p[3],
            operator=lambda operand, dimensions: operand.get().extend(dimensions),
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_extend_error(p):
        """extend : EXTEND_OPERATOR error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> incorrect extend operator using, at {p.lineno(1)}  line \n')

    def p_do(self, p):
        """do : DO VARIABLE call_parameters"""
        p[0] = FunctionCall(
            functions_map=self.functions_map,
            function_name=p[2],
            call_parameters=p[3],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_do_error(p):
        """do : DO error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> incorrect function calling, at {p.lineno(1)}  line \n')

    @staticmethod
    def p_call_parameters(p):
        """call_parameters : call_parameter call_parameters
                           | call_parameter"""
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0]: list = [p[1]]

    @staticmethod
    def p_call_parameter(p):
        """call_parameter : expression"""
        p[0] = p[1]

    @staticmethod
    def p_call_parameter_error(p):
        """call_parameter : error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> incorrect call parameter setting, at {p.lineno(1)}  line \n')

    def p_get(self, p):
        """get : GET VARIABLE"""
        p[0] = GetFunctionResult(
            functions_map=self.functions_map,
            function_name=p[2],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_get_error(p):
        """get : GET error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> incorrect get function last result operator using, at {p.lineno(1)}  line\n'
                         f'    GET operator require function name\n')

    @staticmethod
    def p_expression_bracket(p):
        """expression : LBRACKET expression RBRACKET"""
        p[0] = p[2]

    @staticmethod
    def p_expression_bracket_l_error(p):
        """expression : error expression RBRACKET"""
        p[0] = Empty()
        sys.stderr.write(f'>>> opening bracket missing, at {p.lineno(1)}  line\n')

    @staticmethod
    def p_expression_bracket_r_error(p):
        """expression : LBRACKET expression error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> closing bracket missing, at {p.lineno(1)}  line\n')

    def p_expression_variable(self, p):
        """expression : VARIABLE"""
        p[0] = NamedOperand(self.__function_stack, p[1], p.lineno(1))

    @staticmethod
    def p_number_oct(p):
        """number : OCT_NUMBER"""
        p[0] = Operand(_INT_TYPE_ID_, p[1], p.lineno(1))

    @staticmethod
    def p_number_dec(p):
        """number : DEC_NUMBER"""
        p[0] = Operand(_INT_TYPE_ID_, p[1], p.lineno(1))

    @staticmethod
    def p_number_hex(p):
        """number : HEX_NUMBER"""
        p[0] = Operand(_INT_TYPE_ID_, p[1], p.lineno(1))

    @staticmethod
    def p_boolean_true(p):
        """boolean : TRUE"""
        p[0] = Operand(_BOOL_TYPE_ID_, True, p.lineno(1))

    @staticmethod
    def p_boolean_false(p):
        """boolean : FALSE"""
        p[0] = Operand(_BOOL_TYPE_ID_, False, p.lineno(1))

    @staticmethod
    def p_base_values(p):
        """base_values : number
                       | boolean"""
        p[0] = p[1]

    @staticmethod
    def p_initializer(p):
        """initializer : base_values"""
        p[0] = p[1]

    def p_var_declaration_dim(self, p):
        """var_declaration : VAR VARIABLE OS_BRACKET dimensions CS_BRACKET ASSIGNMENT initializer"""
        p[0] = VarDeclaration(
            function_stack=self.__function_stack,
            variable_name=p[2],
            dimensions=Dimensions(p[4], p.lineno(1)),
            type_id=p[7].type(),
            init_value=p[7].value(),
            lineno=p.lineno(1)
        )

    def p_var_declaration_expression(self, p):
        """var_declaration : VAR VARIABLE ASSIGNMENT expression"""
        p[0] = VarDeclarationFromExpr(
            function_stack=self.__function_stack,
            variable_name=p[2],
            expression=p[4],
            lineno=p.lineno(1)
        )

    @staticmethod
    def p_var_declaration_error(p):
        """var_declaration : VAR error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> incorrect variable declaration, at {p.lineno(1)}  line\n'
                         f'    var declaration require following order: VAR NAME (optional [dim,...]) = initializer\n')

    @staticmethod
    def p_indexing(p):
        """indexing : expression OS_BRACKET dimensions CS_BRACKET"""
        p[0] = Indexing(
            operand=p[1],
            dimensions=Dimensions(p[3], p.lineno(2)),
            lineno=p.lineno(2)
        )

    @staticmethod
    def p_dimensions(p):
        """dimensions : dimension COMMA dimensions
                      | dimension"""
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0]: list = [p[1]]

    @staticmethod
    def p_dimension(p):
        """dimension : expression"""
        p[0] = p[1]

    @staticmethod
    def p_dimension_error(p):
        """dimension : error"""
        p[0] = Empty()
        sys.stderr.write(f'>>> incorrect dimension setting, at {p.lineno(1)}  line \n')

    @staticmethod
    def p_empty(p):
        """empty : """
        p[0] = Empty()

    def p_error(self, p):
        try:
            sys.stderr.write(f'Syntax error at {p.lineno} line\n')
        except:
            sys.stderr.write(f'Syntax error\n')
        self.good = False
