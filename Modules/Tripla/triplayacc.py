
# ------------------------------------------------------------
# triplayacc.py
#
# Yacc grammar of the TRIPLA language
''' 
    	E -> let D in E
		| ID
		| ID ( A )
		| E AOP E
		| ( E )
		| CONST
		| ID = E
		| E ; E
		| if B then E else E
		| while B do { E }
	A -> E | A , E
	D -> ID ( V ) { E }
		| D ID ( V ) { E }
	V -> ID | V , V
	B -> (B)
		| true | false
		| B LOP B
		| E RELOP E

	ID : Bezeichner = [A-Za-z_] [A-Za-z0-9_] *
	CONST: Positive, ganze Zahl = 0 | [1-9] [0-9] *
	AOP: Operatoren (+, - , * , /)
	RELOP: Vergleichsoperatoren (==, !=, <, >, <=, >=)
	LOP: Logische Operatoren (||, &&, ==, !=)
'''

import ply.yacc as yacc
import Modules.Tripla.syntax as ast
from Modules.Tripla.triplalex import TriplaLexer

class TriplaYacc:
    def __init__(self):
        self.lexer_instance = TriplaLexer()
        self.tokens = self.lexer_instance.tokens
        self.precedence = (
            ('nonassoc', 'RPAR', 'IN'),
            ('left', 'SEMICOLON', 'COMMA', 'ID'),
            ('nonassoc', 'ASSIGN', 'ELSE', 'WHILE', 'IF', 'DO', 'LET'),
            ('left', 'OR'),
            ('left', 'AND'),
            ('nonassoc', 'LT', 'GT', 'EQ', 'NEQ', 'LTE', 'GTE'),
            ('left', 'ADD', 'SUB'),
            ('left', 'MUL', 'DIV'),
        )
        self.parser = yacc.yacc(debug=True, module=self)
        self.yacc_errors = []
        self.lex_errors = []

 
    def p_E_let(self, p):
        'E : LET D IN E'
        p[0] = ast.LET(p[2], p[4])

    def p_E_id(self, p):
        'E : ID'
        p[0] = ast.VAR(p[1])

    def p_E_id_arg(self, p):
        'E : ID LPAR A RPAR'
        p[0] = ast.CALL(p[1], p[3])

    def p_E_binop(self, p):
        '''
        E : E ADD E
        | E SUB E
        | E MUL E
        | E DIV E
        '''
        p[0] = ast.BINOP(p[2], p[1], p[3])

    def p_E_parentheses(self, p):
        'E : LPAR E RPAR'
        p[0] = p[2]

    def p_E_const(self, p):
        'E : CONST'
        p[0] = ast.CONST(p[1])

    def p_E_assign(self, p):
        'E : ID ASSIGN E'
        p[0] = ast.ASSIGN(ast.VAR(p[1]), p[3])

    def p_E_semicolon(self, p):
        'E : E SEMICOLON E'
        p[0] = ast.SEQ(p[1], p[3])

    def p_E_if_ele(self, p):
        'E : IF B THEN E ELSE E'
        p[0] = ast.IF(p[2], p[4], p[6])

    def p_E_while(self, p):
        'E : WHILE B DO LBRA E RBRA'
        p[0] = ast.WHILE(p[2],p[5])

    def p_A_single(self, p):
        'A : E'
        p[0] = [p[1]]

    def p_A_multiple(self, p):
        'A : A COMMA E'
        p[0] = p[1] + [p[3]]

    def p_D_single(self, p):
        'D : ID LPAR V RPAR LBRA E RBRA'
        p[0] = [ast.DECL(p[1], p[3], p[6])]

    def p_D_multiple(self, p):
        'D : D ID LPAR V RPAR LBRA E RBRA'
        p[0] = p[1] + [ast.DECL(p[2], p[4], p[7])]

    def p_V_single(self, p):
        'V : ID'
        p[0] = [ast.VAR(p[1])]

    def p_V_multiple(self, p):
        'V : V COMMA V'
        p[0] = p[1] + p[3]

    def p_B_parentheses(self, p):
        'B : LPAR B RPAR'
        p[0] = p[2]

    def p_B_true(self, p):
        'B : TRUE'
        p[0] = ast.CONST(True)

    def p_B_false(self, p):
        'B : FALSE'
        p[0] = ast.CONST(False)

    def p_B_lop(self, p):
        '''
        B : B OR B
        | B AND B
        | B NEQ B
        | B EQ B
        '''
        p[0] = ast.BINOP(p[2], p[1], p[3])

    def p_B_relop(self, p):
        '''
        B : E EQ E
        | E NEQ E
        | E LT E
        | E GT E
        | E LTE E
        | E GTE E
        '''
        p[0] = ast.BINOP(p[2], p[1], p[3])
        
    def p_error(self, p):
        if p:
            self.yacc_errors.append({
                'value': p.value,
                'lineno': p.lineno,
                'lexpos': p.lexpos
            })
        else:
            self.yacc_errors.append({
                'value': "",
                'lineno': 1,
                'lexpos': 0
            })

            
    def parse(self, input_string):
        self.yacc_errors = []
        self.lex_errors = []
        self.lexer_instance.reset()
        ast = self.parser.parse(input_string, lexer=self.lexer_instance)
        self.lex_errors = self.lexer_instance.lex_errors
        return ast


