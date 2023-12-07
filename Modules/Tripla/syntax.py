# (c) Stephan Diehl, University of Trier, Germany, 2023
import graphviz 
class IDotExporter:
    def to_dot_parse(self,dot):
        pass
    def to_dot_ast(self,dot):
        pass

    def getNodeString(self):
        return "node_"+str(self.pp)

    def getParseTree(self):
        dot = graphviz.Digraph('Parse-Tree', comment='Parse-Tree')
        dot.attr(bgcolor='#282a36')  # Set the background color to light gray

        dot.attr('node', color='white', fontcolor='white')
        dot.attr('edge', color='white', fontcolor='white')
        self.to_dot_parse(dot)
        return dot

    def getAstTree(self):
        dot = graphviz.Digraph('Ast-Tree', comment='Ast-Tree')
        dot.attr(bgcolor='#282a36')  # Set the background color to light gray

        dot.attr('node', color='white', fontcolor='white')
        dot.attr('edge', color='white', fontcolor='white')
        self.to_dot_ast(dot)
        return dot
    
class EXPRESSION(IDotExporter):
    ppcount=0

    def __init__(self):
        self.pp=EXPRESSION.ppcount
        EXPRESSION.ppcount=EXPRESSION.ppcount+1

    def copy(self):
        return EXPRESSION()

    def allNodes(self):
        ret = [self]
        for node in (self.__getattribute__(a) for a in self.__dict__.keys()):
            if isinstance(node, EXPRESSION):
                ret = ret + node.allNodes()
            if isinstance(node, list):
                for n in node:
                    if isinstance(n, EXPRESSION):
                        ret = ret + n.allNodes()
        return ret

class LET(EXPRESSION):
    def __init__(self, declarations, body):
        super().__init__()
        self.declarations=declarations
        self.body=body

    def __str__(self): return "let " \
        +','.join([ str(decl) for decl in self.declarations ]) \
        + " in " + str(self.body)
    
    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"LET", fontcolor="#ff79c6", shape="doubleoctagon")
        for x in (self.declarations):
            dot.edge(self.getNodeString(),x.to_dot_parse(dot))
        dot.edge(self.getNodeString(),self.body.to_dot_parse(dot))
        return self.getNodeString()
       
    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),"LET", fontcolor="#ff79c6", shape="none")
        for x in (self.declarations):
            dot.edge(self.getNodeString(),x.to_dot_ast(dot))
        dot.edge(self.getNodeString(),self.body.to_dot_ast(dot))
        return self.getNodeString()

class DECL(EXPRESSION):
    def __init__(self, fname, params, body):
        super().__init__()
        self.fname=fname
        self.params=params
        self.body=body

    def __str__(self): return self.fname+"(" \
        +','.join([ str(param) for param in self.params ]) \
        +"){ "+str(self.body)+" }"

    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"DECL: "+self.fname, fontcolor="#ffb86c")
        for x in (self.params):
            dot.edge(self.getNodeString(),x.to_dot_parse(dot))
        
        dot.edge(self.getNodeString(),self.body.to_dot_parse(dot))
        return self.getNodeString()

    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),self.fname, fontcolor="#ffb86c", shape="none")
        for x in (self.params):
            dot.edge(self.getNodeString(),x.to_dot_ast(dot), arrowhead="icurve")
        
        dot.edge(self.getNodeString(),self.body.to_dot_ast(dot), arrowhead="tee")
        return self.getNodeString()
 
class CALL(EXPRESSION):
    def __init__(self, fname, arguments):
        super().__init__()
        self.fname=fname
        self.arguments=arguments

    def __str__(self): return self.fname+"(" \
        +','.join([ str(arg) for arg in self.arguments ]) +")"

    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"CALL: "+self.fname, shape="cds")
        for x in (self.arguments):
            dot.edge(self.getNodeString(),x.to_dot_parse(dot))
        return self.getNodeString()
 

    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),self.fname+"()"
, shape="none")
        for x in (self.arguments):
            dot.edge(self.getNodeString(),x.to_dot_ast(dot))
        return self.getNodeString()

    
class VAR(EXPRESSION):
    def __init__(self,name):
        super().__init__()
        self.name=name

    def __str__(self): return self.name


    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"VAR: "+self.name,fontcolor="#50fa7b", shape="house")
        return self.getNodeString()

    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),self.name,fontcolor="#50fa7b", shape="none")
        return self.getNodeString()


class BINOP(EXPRESSION):
    def __init__(self,operator,arg1,arg2):
        super().__init__()
        self.operator=operator
        self.arg1=arg1
        self.arg2=arg2

    def __str__(self): return "("+str(self.arg1)+self.operator+str(self.arg2)+")"

    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"OP: "+self.operator, fontcolor="#ff5555", shape="rect")
        dot.edge(self.getNodeString(),self.arg1.to_dot_parse(dot))
        dot.edge(self.getNodeString(),self.arg2.to_dot_parse(dot))
        return self.getNodeString()

    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),self.operator, fontcolor="#ff5555", shape="none")
        dot.edge(self.getNodeString(),self.arg1.to_dot_ast(dot))
        dot.edge(self.getNodeString(),self.arg2.to_dot_ast(dot))
        return self.getNodeString()

class CONST(EXPRESSION):
    def __init__(self,value):
        super().__init__()
        self.value=value

    def __str__(self): return str(self.value)

    
    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"CONST: "+str(self.value), fontcolor="#bd93f9")
        return self.getNodeString()

    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),str(self.value), fontcolor="#bd93f9", shape="none")
        return self.getNodeString()
    
class ASSIGN(EXPRESSION):
    def __init__(self, variable, expression):
        super().__init__()
        self.variable=variable
        self.expression=expression

    def __str__(self): return self.variable.name+"="+str(self.expression)

    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"ASSIGN: "+str(self.variable))
        dot.edge(self.getNodeString(),self.expression.to_dot_parse(dot))
        return self.getNodeString()

    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),str(self.variable), shape="none")
        dot.edge(self.getNodeString(),self.expression.to_dot_ast(dot))
        return self.getNodeString()


class SEQ(EXPRESSION):
    def __init__(self, exp1, exp2):
        super().__init__()
        self.exp1=exp1
        self.exp2=exp2

    def __str__(self): return str(self.exp1)+";"+str(self.exp2)

    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"SEQ", shape="egg")
        dot.edge(self.getNodeString(),self.exp1.to_dot_parse(dot))
        dot.edge(self.getNodeString(),self.exp2.to_dot_parse(dot))
        return self.getNodeString()

    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),shape="point")
        dot.edge(self.getNodeString(),self.exp1.to_dot_ast(dot))
        dot.edge(self.getNodeString(),self.exp2.to_dot_ast(dot))
        return self.getNodeString()

class IF(EXPRESSION):
    def __init__(self,condition,exp1,exp2):
        super().__init__()
        self.condition=condition
        self.exp1=exp1
        self.exp2=exp2

    def __str__(self): return "if "+str(self.condition)+" then { " \
            + str(self.exp1)+" } else { "+str(self.exp2)+" } "


    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"if", fontcolor="#2196f3", shape="diamond")

        id = self.condition.to_dot_parse(dot)
        
        dot.node(self.getNodeString()+'t',"then", fontcolor="#2196f3")
        dot.node(self.getNodeString()+'e',"else", fontcolor="#2196f3")

        dot.edge(self.getNodeString(),id)
        dot.edge(self.getNodeString(),self.getNodeString()+'t')
        dot.edge(self.getNodeString(),self.getNodeString()+'e')
                
        dot.edge(self.getNodeString()+'t',self.exp1.to_dot_parse(dot))
        dot.edge(self.getNodeString()+'e',self.exp2.to_dot_parse(dot))
        return self.getNodeString()

    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),"if", fontcolor="#2196f3", shape="none")

        id = self.condition.to_dot_ast(dot)
        
        dot.node(self.getNodeString()+'t',"then", fontcolor="#2196f3", shape="none")
        dot.node(self.getNodeString()+'e',"else", fontcolor="#2196f3", shape="none")

        dot.edge(self.getNodeString(),id)
        dot.edge(self.getNodeString(),self.getNodeString()+'t')
        dot.edge(self.getNodeString(),self.getNodeString()+'e')
                
        dot.edge(self.getNodeString()+'t',self.exp1.to_dot_ast(dot))
        dot.edge(self.getNodeString()+'e',self.exp2.to_dot_ast(dot))
        return self.getNodeString()
    
class WHILE(EXPRESSION):
    def __init__(self,condition,body):
        super().__init__()
        self.condition=condition
        self.body=body

    def __str__(self): return "while "+str(self.condition)+" do { "+str(self.body)+" }"

    
    def to_dot_parse(self,dot):
        dot.node(self.getNodeString(),"WHILE", fontcolor="#f1fa8c")
        dot.edge(self.getNodeString(),self.condition.to_dot_parse(dot))
        dot.edge(self.getNodeString(),self.body.to_dot_parse(dot))
        return self.getNodeString()

    
    def to_dot_ast(self,dot):
        dot.node(self.getNodeString(),"WHILE", fontcolor="#f1fa8c", shape="none")
        dot.edge(self.getNodeString(),self.condition.to_dot_ast(dot))
        dot.edge(self.getNodeString(),self.body.to_dot_ast(dot))
        return self.getNodeString()
# see https://stackoverflow.com/questions/51753937/python-pretty-print-nested-objects

def pretty_print(clas, indent=0):
    print(' ' * indent +  type(clas).__name__ +  ':')
    indent += 4
    for k,v in clas.__dict__.items():
        if '__dict__' in dir(v):
            pretty_print(v,indent)
        else:
            print(' ' * indent +  k + ': ' + str(v))



