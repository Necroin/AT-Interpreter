import sys
import ply.lex as lex

reserved = {
    'PLEASE': 'PLEASE',
    'THANKS': 'THANKS',
    'TRUE': 'TRUE',
    'FALSE': 'FALSE',
    'VAR': 'VAR',
    'SIZE': 'SIZE_OPERATOR',
    'LOGITIZE': 'LOGITIZE_OPERATOR',
    'DIGITIZE': 'DIGITIZE_OPERATOR',
    'REDUCE': 'REDUCE_OPERATOR',
    'EXTEND': 'EXTEND_OPERATOR',
    'MXEQ': 'MXEQ_OPERATOR',
    'MXLT': 'MXLT_OPERATOR',
    'MXGT': 'MXGT_OPERATOR',
    'MXLTE': 'MXLTE_OPERATOR',
    'MXGTE': 'MXGTE_OPERATOR',
    'ELEQ': 'ELEQ_OPERATOR',
    'ELLT': 'ELLT_OPERATOR',
    'ELGT': 'ELGT_OPERATOR',
    'ELLTE': 'ELLTE_OPERATOR',
    'ELGTE': 'ELGTE_OPERATOR',
    'NOT': 'NOT_OPERATOR',
    'AND': 'AND_OPERATOR',
    'MXTRUE': 'MXTRUE_OPERATOR',
    'MXFALSE': 'MXFALSE_OPERATOR',
    'FOR': 'FOR',
    'BOUNDARY': 'BOUNDARY',
    'STEP': 'STEP',
    'SWITCH': 'SWITCH',
    'PRINT':'PRINT',

    # robot
    'MOVE': 'MOVE',
    'ROTATE': 'ROTATE',
    'LEFT': 'LEFT',
    'RIGHT': 'RIGHT',
    'ENVIRONMENT': 'ENVIRONMENT',

    # function
    'TASK': 'TASK',
    # 'FINDEXIT': 'FINDEXIT',
    'RESULT': 'RESULT',
    'DO': 'DO',
    'GET': 'GET'
}


class lexer(object):

    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = ['OCT_NUMBER', 'HEX_NUMBER', 'DEC_NUMBER', 'VARIABLE',
              'ASSIGNMENT', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE',
              'LBRACKET', 'RBRACKET',
              'OS_BRACKET', 'CS_BRACKET', 'QUOTE',
              'COMMA', 'NEWLINE'] + list(reserved.values())

    precedence = (
        ('right', 'ASSIGNMENT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('left', 'AND_OPERATOR'),
        ('right',
         'LOGITIZE_OPERATOR',
         'DIGITIZE_OPERATOR',
         'REDUCE_OPERATOR',
         'EXTEND_OPERATOR',
         'SIZE_OPERATOR',
         'MXEQ_OPERATOR',
         'MXLT_OPERATOR',
         'MXGT_OPERATOR',
         'MXLTE_OPERATOR',
         'MXGTE_OPERATOR',
         'ELEQ_OPERATOR',
         'ELLT_OPERATOR',
         'ELGT_OPERATOR',
         'ELLTE_OPERATOR',
         'ELGTE_OPERATOR',
         'NOT_OPERATOR',
         'MXTRUE_OPERATOR',
         'MXFALSE_OPERATOR'
         )
    )

    t_ASSIGNMENT = r'\='
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'\/'

    t_OS_BRACKET = r'\['
    t_CS_BRACKET = r'\]'

    t_QUOTE = r'"'

    t_LBRACKET = r'\('
    t_RBRACKET = r'\)'

    t_COMMA = r'\,'

    @staticmethod
    def t_OCT_NUMBER(t):
        r'[0][0-9]+'
        t.value = int(t.value, 8)
        return t

    @staticmethod
    def t_HEX_NUMBER(t):
        r'[0x][0-9A-F]+'
        t.value = int(t.value, 16)
        return t

    @staticmethod
    def t_DEC_NUMBER(t):
        r'[1-9][0-9]*|[0]'
        t.value = int(t.value)
        return t

    @staticmethod
    def t_VARIABLE(t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'VARIABLE')
        return t

    @staticmethod
    def t_NEWLINE(t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')
        t.lexer.linestart = t.lexer.lexpos
        return t

    @staticmethod
    def t_error(t):
        sys.stderr.write(f'Error: Illegal character: {t.value[0]} at line {t.lexer.lineno}\n')
        t.lexer.skip(1)

    t_ignore = ' \t'

    def input(self, _data):
        return self.lexer.input(_data)

    def token(self):
        return self.lexer.token()


if __name__ == '__main__':
    f = open('../Interpreter/Program.txt')
    data = f.read()
    f.close()
    lexer = lexer()
    lexer.input(data)
    while True:
        token = lexer.token()
        if token is None:
            break
        else:
            print(token)
