# ------------------------------------------------------------
# triplalex.py
#
# Lexer class for the TRIPLA parser
# ------------------------------------------------------------

import ply.lex as lex

class TriplaLexer:
    def __init__(self):
        self.reserved = {
            'let' : 'LET',
            'in' : 'IN',
            'while' : 'WHILE',
            'do' : 'DO',
            'if' : 'IF',
            'then' : 'THEN',
            'else' : 'ELSE',
            'true' : 'TRUE',
            'false' : 'FALSE',
        }

        self.tokens = [
            'ID',
            'CONST',
            'ADD',
            'SUB',
            'MUL',
            'DIV',
            'GT',
            'LT',
            'GTE',
            'LTE',
            'AND',
            'OR',
            'EQ',
            'NEQ',
            'LBRA',
            'RBRA',
            'LPAR',
            'RPAR',
            'COMMA',
            'ASSIGN',
            'SEMICOLON',
            'COMMENT',
        ]+list(self.reserved.values())


        self.t_ADD = r'\+'
        self.t_SUB = r'-'
        self.t_MUL = r'\*'
        self.t_DIV = r'/'
        self.t_GT = r'>'
        self.t_LT = r'<'
        self.t_GTE = r'>='
        self.t_LTE = r'<='
        self.t_AND = r'&&'
        self.t_OR = r'\|\|'
        self.t_EQ = r'=='
        self.t_NEQ = r'!='
        self.t_LBRA = r'\{'
        self.t_RBRA = r'\}'
        self.t_LPAR = r'\('
        self.t_RPAR = r'\)'
        self.t_COMMA = r','
        self.t_ASSIGN = r'='
        self.t_SEMICOLON = r';'

        self.t_ignore  = ' \t'

        self.lexer = lex.lex(module=self)
        self.lex_errors = []
        self.lexer.lineno = 1

    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.reserved.get(t.value,'ID')    # Check for reserved words
        return t

    def t_CONST(self, t):
        r'0|[1-9][0-9]*'
        t.value = int(t.value)
        return t

    def t_COMMENT(self, t):
        r'/\*[^*]*\*+(?:[^*/][^*]*\*+)*/|//.*'
        pass

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self,t):
        self.lex_errors.append({
        'value': t.value[0],
        'lineno': t.lineno,
        'lexpos': t.lexpos
        })
        t.lexer.skip(1)

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        return self.lexer.token()

    def reset(self):
        self.lexer.lineno = 1
        self.lex_errors = []
