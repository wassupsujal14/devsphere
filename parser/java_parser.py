






"""
Complete Java Parser and Evaluator
A comprehensive Java interpreter with classes, methods, and advanced features
"""

import re
import math
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional, Union
import json

# ===========================
# AST (Abstract Syntax Tree)
# ===========================

@dataclass
class Expr:
    
    pass

@dataclass
class IntLit(Expr):
    value: int

@dataclass
class FloatLit(Expr):
    value: float

@dataclass
class StringLit(Expr):
    value: str

@dataclass
class BoolLit(Expr):
    value: bool

@dataclass
class CharLit(Expr):
    value: str

@dataclass
class NullLit(Expr):
    pass

@dataclass
class Variable(Expr):
    name: str

@dataclass
class BinOp(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr

@dataclass
class TernaryOp(Expr):
    condition: Expr
    true_expr: Expr
    false_expr: Expr

@dataclass
class ArrayAccess(Expr):
    array: Expr
    index: Expr

@dataclass
class FieldAccess(Expr):
    obj: Expr
    field: str

@dataclass
class MethodCall(Expr):
    obj: Optional[Expr]
    method: str
    args: List[Expr]

@dataclass
class NewObject(Expr):
    class_name: str
    args: List[Expr]

@dataclass
class NewArray(Expr):
    element_type: str
    sizes: List[Expr]

@dataclass
class ArrayInit(Expr):
    elements: List[Expr]

@dataclass
class Cast(Expr):
    target_type: str
    expr: Expr

# Statements

@dataclass
class Stmt:
    
    pass

@dataclass
class VarDecl(Stmt):
    var_type: str
    name: str
    value: Optional[Expr]

@dataclass
class Assign(Stmt):
    target: str
    value: Expr

@dataclass
class ArrayAssign(Stmt):
    array: str
    index: Expr
    value: Expr

@dataclass
class FieldAssign(Stmt):
    obj: Expr
    field: str
    value: Expr

@dataclass
class If(Stmt):
    condition: Expr
    then_block: List[Stmt]
    else_block: List[Stmt]

@dataclass
class While(Stmt):
    condition: Expr
    body: List[Stmt]

@dataclass
class DoWhile(Stmt):
    body: List[Stmt]
    condition: Expr

@dataclass
class For(Stmt):
    init: Optional[Stmt]
    condition: Optional[Expr]
    update: Optional[Stmt]
    body: List[Stmt]

@dataclass
class ForEach(Stmt):
    var_type: str
    var: str
    iterable: Expr
    body: List[Stmt]

@dataclass
class Switch(Stmt):
    expr: Expr
    cases: List[tuple]  # [(value, stmts), ...]
    default: Optional[List[Stmt]]

@dataclass
class Break(Stmt):
    pass

@dataclass
class Continue(Stmt):
    pass

@dataclass
class Return(Stmt):
    expr: Optional[Expr]

@dataclass
class ExprStmt(Stmt):
    expr: Expr

@dataclass
class Try(Stmt):
    try_block: List[Stmt]
    catch_blocks: List[tuple]  # [(exception_type, var, stmts), ...]
    finally_block: Optional[List[Stmt]]

# Top-level declarations

@dataclass
class MethodDecl:
    modifiers: List[str]
    return_type: str
    name: str
    params: List[tuple]  # [(type, name), ...]
    body: List[Stmt]

@dataclass
class FieldDecl:
    modifiers: List[str]
    field_type: str
    name: str
    value: Optional[Expr]

@dataclass
class Constructor:
    modifiers: List[str]
    name: str
    params: List[tuple]
    body: List[Stmt]

@dataclass
class ClassDecl:
    modifiers: List[str]
    name: str
    fields: List[FieldDecl]
    constructors: List[Constructor]
    methods: List[MethodDecl]

# ===========================
# EXCEPTIONS
# ===========================

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

# ===========================
# LEXER (Tokenizer)
# ===========================

class TokenType(Enum):
    # Literals
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    CHAR = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    
    # Keywords
    CLASS = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()
    STATIC = auto()
    FINAL = auto()
    VOID = auto()
    INT_TYPE = auto()
    FLOAT_TYPE = auto()
    DOUBLE_TYPE = auto()
    BOOLEAN_TYPE = auto()
    CHAR_TYPE = auto()
    STRING_TYPE = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    FOR = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    NEW = auto()
    THIS = auto()
    SUPER = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    THROWS = auto()
    EXTENDS = auto()
    IMPLEMENTS = auto()
    
    # Identifiers
    ID = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    PLUSPLUS = auto()
    MINUSMINUS = auto()
    PLUSASSIGN = auto()
    MINUSASSIGN = auto()
    QUESTION = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    ASSIGN = auto()
    COLON = auto()
    
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    col: int

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.col = 1
        
    def error(self, msg: str):
        raise SyntaxError(f"Line {self.line}, Col {self.col}: {msg}")
    
    def peek(self, offset=0):
        pos = self.pos + offset
        if pos < len(self.code):
            return self.code[pos]
        return None
    
    def advance(self):
        if self.pos < len(self.code):
            if self.code[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1
    
    def skip_whitespace(self):
        while self.peek() and self.peek() in ' \t\n\r':
            self.advance()
    
    def skip_comment(self):
        if self.peek() == '/' and self.peek(1) == '/':
            while self.peek() and self.peek() != '\n':
                self.advance()
            return True
        
        if self.peek() == '/' and self.peek(1) == '*':
            self.advance()
            self.advance()
            while self.peek():
                if self.peek() == '*' and self.peek(1) == '/':
                    self.advance()
                    self.advance()
                    return True
                self.advance()
            self.error("Unterminated comment")
        
        return False
    
    def read_number(self):
        start_col = self.col
        num_str = ''
        has_dot = False
        
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            if self.peek() == '.':
                if has_dot or (self.peek(1) and not self.peek(1).isdigit()):
                    break
                has_dot = True
            num_str += self.peek()
            self.advance()
        
        if self.peek() and self.peek() in 'fFdD':
            self.advance()
            has_dot = True
        
        if has_dot:
            return Token(TokenType.FLOAT, float(num_str), self.line, start_col)
        else:
            return Token(TokenType.INT, int(num_str), self.line, start_col)
    
    def read_string(self):
        start_col = self.col
        self.advance()
        string = ''
        
        while self.peek() and self.peek() != '"':
            if self.peek() == '\\':
                self.advance()
                escape_chars = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', '\'': '\''}
                string += escape_chars.get(self.peek(), self.peek() or '')
            else:
                string += self.peek()
            self.advance()
        
        if self.peek() != '"':
            self.error("Unterminated string")
        self.advance()
        
        return Token(TokenType.STRING, string, self.line, start_col)
    
    def read_char(self):
        start_col = self.col
        self.advance()
        
        if self.peek() == '\\':
            self.advance()
            escape_chars = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '\'': '\''}
            char = escape_chars.get(self.peek(), self.peek() or '')
            self.advance()
        else:
            char = self.peek() or ''
            self.advance()
        
        if self.peek() != '\'':
            self.error("Unterminated char literal")
        self.advance()
        
        return Token(TokenType.CHAR, char, self.line, start_col)
    
    def read_identifier(self):
        start_col = self.col
        ident = ''
        
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            ident += self.peek()
            self.advance()
        
        keywords = {
            'class': TokenType.CLASS, 'public': TokenType.PUBLIC, 'private': TokenType.PRIVATE,
            'protected': TokenType.PROTECTED, 'static': TokenType.STATIC, 'final': TokenType.FINAL,
            'void': TokenType.VOID, 'int': TokenType.INT_TYPE, 'float': TokenType.FLOAT_TYPE,
            'double': TokenType.DOUBLE_TYPE, 'boolean': TokenType.BOOLEAN_TYPE,
            'char': TokenType.CHAR_TYPE, 'String': TokenType.STRING_TYPE,
            'if': TokenType.IF, 'else': TokenType.ELSE, 'while': TokenType.WHILE,
            'do': TokenType.DO, 'for': TokenType.FOR, 'switch': TokenType.SWITCH,
            'case': TokenType.CASE, 'default': TokenType.DEFAULT,
            'break': TokenType.BREAK, 'continue': TokenType.CONTINUE,
            'return': TokenType.RETURN, 'new': TokenType.NEW,
            'this': TokenType.THIS, 'super': TokenType.SUPER,
            'try': TokenType.TRY, 'catch': TokenType.CATCH, 'finally': TokenType.FINALLY,
            'throw': TokenType.THROW, 'throws': TokenType.THROWS,
            'extends': TokenType.EXTENDS, 'implements': TokenType.IMPLEMENTS,
            'true': TokenType.TRUE, 'false': TokenType.FALSE, 'null': TokenType.NULL,
        }
        
        token_type = keywords.get(ident, TokenType.ID)
        value = ident if token_type == TokenType.ID else None
        
        return Token(token_type, value, self.line, start_col)
    
    def tokenize(self) -> List[Token]:
        tokens = []
        
        while self.pos < len(self.code):
            self.skip_whitespace()
            
            while self.skip_comment():
                self.skip_whitespace()
            
            if self.pos >= len(self.code):
                break
            
            ch = self.peek()
            start_col = self.col
            
            if ch.isdigit():
                tokens.append(self.read_number())
                continue
            
            if ch == '"':
                tokens.append(self.read_string())
                continue
            
            if ch == '\'':
                tokens.append(self.read_char())
                continue
            
            if ch.isalpha() or ch == '_':
                tokens.append(self.read_identifier())
                continue
            
            # Two-character operators
            two_char = {
                '++': TokenType.PLUSPLUS, '--': TokenType.MINUSMINUS,
                '==': TokenType.EQ, '!=': TokenType.NE,
                '<=': TokenType.LE, '>=': TokenType.GE,
                '&&': TokenType.AND, '||': TokenType.OR,
                '+=': TokenType.PLUSASSIGN, '-=': TokenType.MINUSASSIGN,
            }
            
            two_ch = ch + (self.peek(1) or '')
            if two_ch in two_char:
                tokens.append(Token(two_char[two_ch], None, self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            # Single-character
            single_char = {
                '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.STAR,
                '/': TokenType.SLASH, '%': TokenType.PERCENT, '=': TokenType.ASSIGN,
                '<': TokenType.LT, '>': TokenType.GT, '!': TokenType.NOT,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
                ';': TokenType.SEMICOLON, ',': TokenType.COMMA,
                '.': TokenType.DOT, ':': TokenType.COLON, '?': TokenType.QUESTION,
            }
            
            if ch in single_char:
                tokens.append(Token(single_char[ch], None, self.line, start_col))
                self.advance()
                continue
            
            self.error(f"Unexpected character: {ch}")
        
        tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return tokens

# ===========================
# PARSER
# ===========================

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        
    def error(self, msg: str):
        token = self.current()
        raise SyntaxError(f"Line {token.line}, Col {token.col}: {msg}")
    
    def current(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]
    
    def peek(self, offset=1) -> Token:
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def expect(self, token_type: TokenType):
        if self.current().type != token_type:
            self.error(f"Expected {token_type.name}, got {self.current().type.name}")
        self.advance()
    
    def is_type(self) -> bool:
        return self.current().type in (
            TokenType.INT_TYPE, TokenType.FLOAT_TYPE, TokenType.DOUBLE_TYPE,
            TokenType.BOOLEAN_TYPE, TokenType.CHAR_TYPE, TokenType.STRING_TYPE,
            TokenType.VOID, TokenType.ID
        )
    
    def parse_type(self) -> str:
        type_map = {
            TokenType.INT_TYPE: 'int', TokenType.FLOAT_TYPE: 'float',
            TokenType.DOUBLE_TYPE: 'double', TokenType.BOOLEAN_TYPE: 'boolean',
            TokenType.CHAR_TYPE: 'char', TokenType.STRING_TYPE: 'String',
            TokenType.VOID: 'void',
        }
        
        if self.current().type == TokenType.ID:
            type_str = self.current().value
            self.advance()
        elif self.current().type in type_map:
            type_str = type_map[self.current().type]
            self.advance()
        else:
            self.error("Expected type")
        
        while self.current().type == TokenType.LBRACKET:
            self.advance()
            self.expect(TokenType.RBRACKET)
            type_str += '[]'
        
        return type_str
    
    # Expression parsing
    
    def parse_expr(self) -> Expr:
        return self.parse_ternary()
    
    def parse_ternary(self) -> Expr:
        expr = self.parse_or()
        
        if self.current().type == TokenType.QUESTION:
            self.advance()
            true_expr = self.parse_expr()
            self.expect(TokenType.COLON)
            false_expr = self.parse_expr()
            return TernaryOp(expr, true_expr, false_expr)
        
        return expr
    
    def parse_or(self) -> Expr:
        left = self.parse_and()
        while self.current().type == TokenType.OR:
            self.advance()
            right = self.parse_and()
            left = BinOp('||', left, right)
        return left
    
    def parse_and(self) -> Expr:
        left = self.parse_equality()
        while self.current().type == TokenType.AND:
            self.advance()
            right = self.parse_equality()
            left = BinOp('&&', left, right)
        return left
    
    def parse_equality(self) -> Expr:
        left = self.parse_relational()
        
        while self.current().type in (TokenType.EQ, TokenType.NE):
            op = '==' if self.current().type == TokenType.EQ else '!='
            self.advance()
            right = self.parse_relational()
            left = BinOp(op, left, right)
        
        return left
    
    def parse_relational(self) -> Expr:
        left = self.parse_additive()
        
        ops = {TokenType.LT: '<', TokenType.LE: '<=', TokenType.GT: '>', TokenType.GE: '>='}
        
        if self.current().type in ops:
            op = ops[self.current().type]
            self.advance()
            right = self.parse_additive()
            return BinOp(op, left, right)
        
        return left
    
    def parse_additive(self) -> Expr:
        left = self.parse_multiplicative()
        
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = '+' if self.current().type == TokenType.PLUS else '-'
            self.advance()
            right = self.parse_multiplicative()
            left = BinOp(op, left, right)
        
        return left
    
    def parse_multiplicative(self) -> Expr:
        left = self.parse_unary()
        
        ops = {TokenType.STAR: '*', TokenType.SLASH: '/', TokenType.PERCENT: '%'}
        
        while self.current().type in ops:
            op = ops[self.current().type]
            self.advance()
            right = self.parse_unary()
            left = BinOp(op, left, right)
        
        return left
    
    def parse_unary(self) -> Expr:
        if self.current().type == TokenType.NOT:
            self.advance()
            return UnaryOp('!', self.parse_unary())
        
        if self.current().type == TokenType.MINUS:
            self.advance()
            return UnaryOp('-', self.parse_unary())
        
        if self.current().type == TokenType.PLUS:
            self.advance()
            return self.parse_unary()
        
        if self.current().type == TokenType.PLUSPLUS:
            self.advance()
            return UnaryOp('++pre', self.parse_unary())
        
        if self.current().type == TokenType.MINUSMINUS:
            self.advance()
            return UnaryOp('--pre', self.parse_unary())
        
        # Type cast
        if self.current().type == TokenType.LPAREN and self.peek().type in (
            TokenType.INT_TYPE, TokenType.FLOAT_TYPE, TokenType.DOUBLE_TYPE,
            TokenType.BOOLEAN_TYPE, TokenType.CHAR_TYPE):
            self.advance()
            target_type = self.parse_type()
            self.expect(TokenType.RPAREN)
            expr = self.parse_unary()
            return Cast(target_type, expr)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> Expr:
        expr = self.parse_primary()
        
        while True:
            if self.current().type == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expr()
                self.expect(TokenType.RBRACKET)
                expr = ArrayAccess(expr, index)
            
            elif self.current().type == TokenType.DOT:
                self.advance()
                if self.current().type != TokenType.ID:
                    self.error("Expected field or method name")
                name = self.current().value
                self.advance()
                
                if self.current().type == TokenType.LPAREN:
                    self.advance()
                    args = self.parse_args()
                    self.expect(TokenType.RPAREN)
                    expr = MethodCall(expr, name, args)
                else:
                    expr = FieldAccess(expr, name)
            
            elif self.current().type == TokenType.PLUSPLUS:
                self.advance()
                expr = UnaryOp('++post', expr)
            
            elif self.current().type == TokenType.MINUSMINUS:
                self.advance()
                expr = UnaryOp('--post', expr)
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> Expr:
        token = self.current()
        
        if token.type == TokenType.INT:
            self.advance()
            return IntLit(token.value)
        
        if token.type == TokenType.FLOAT:
            self.advance()
            return FloatLit(token.value)
        
        if token.type == TokenType.STRING:
            self.advance()
            return StringLit(token.value)
        
        if token.type == TokenType.CHAR:
            self.advance()
            return CharLit(token.value)
        
        if token.type == TokenType.TRUE:
            self.advance()
            return BoolLit(True)
        
        if token.type == TokenType.FALSE:
            self.advance()
            return BoolLit(False)
        
        if token.type == TokenType.NULL:
            self.advance()
            return NullLit()
        
        if token.type == TokenType.THIS:
            self.advance()
            return Variable('this')
        
        # New object or array
        if token.type == TokenType.NEW:
            self.advance()
            
            # Get the type/class name
            if self.current().type == TokenType.ID:
                type_name = self.current().value
                self.advance()
            else:
                # Primitive type for array
                type_name = self.parse_type()
            
            if self.current().type == TokenType.LBRACKET:
                # Array creation
                sizes = []
                while self.current().type == TokenType.LBRACKET:
                    self.advance()
                    if self.current().type != TokenType.RBRACKET:
                        sizes.append(self.parse_expr())
                    self.expect(TokenType.RBRACKET)
                return NewArray(type_name, sizes)
            elif self.current().type == TokenType.LPAREN:
                # Object creation
                self.advance()
                args = self.parse_args()
                self.expect(TokenType.RPAREN)
                return NewObject(type_name, args)
            else:
                self.error("Expected ( or [ after new")
        
        # Array initialization
        if token.type == TokenType.LBRACE:
            self.advance()
            elements = []
            
            if self.current().type != TokenType.RBRACE:
                elements.append(self.parse_expr())
                while self.current().type == TokenType.COMMA:
                    self.advance()
                    if self.current().type == TokenType.RBRACE:
                        break
                    elements.append(self.parse_expr())
            
            self.expect(TokenType.RBRACE)
            return ArrayInit(elements)
        
        # Identifier
        if token.type == TokenType.ID:
            name = token.value
            self.advance()
            
            if self.current().type == TokenType.LPAREN:
                self.advance()
                args = self.parse_args()
                self.expect(TokenType.RPAREN)
                return MethodCall(None, name, args)
            
            return Variable(name)
        
        # Parenthesized expression
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return expr
        
        self.error(f"Unexpected token: {token.type.name}")
    
    def parse_args(self) -> List[Expr]:
        args = []
        
        if self.current().type not in (TokenType.RPAREN, TokenType.EOF):
            args.append(self.parse_expr())
            while self.current().type == TokenType.COMMA:
                self.advance()
                args.append(self.parse_expr())
        
        return args
    
    # Statement parsing
    
    def parse_stmt(self) -> Optional[Stmt]:
        token = self.current()
        
        # Check for control flow keywords first
        if token.type == TokenType.IF:
            return self.parse_if()
        
        if token.type == TokenType.WHILE:
            return self.parse_while()
        
        if token.type == TokenType.DO:
            return self.parse_do_while()
        
        if token.type == TokenType.FOR:
            return self.parse_for()
        
        if token.type == TokenType.SWITCH:
            return self.parse_switch()
        
        if token.type == TokenType.BREAK:
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return Break()
        
        if token.type == TokenType.CONTINUE:
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return Continue()
        
        if token.type == TokenType.RETURN:
            self.advance()
            expr = None
            if self.current().type != TokenType.SEMICOLON:
                expr = self.parse_expr()
            self.expect(TokenType.SEMICOLON)
            return Return(expr)
        
        if token.type == TokenType.TRY:
            return self.parse_try()
        
        if token.type == TokenType.LBRACE:
            return None
        
        # This keyword for field assignment
        if token.type == TokenType.THIS:
            self.advance()
            self.expect(TokenType.DOT)
            
            if self.current().type != TokenType.ID:
                self.error("Expected field name")
            field_name = self.current().value
            self.advance()
            
            self.expect(TokenType.ASSIGN)
            value = self.parse_expr()
            self.expect(TokenType.SEMICOLON)
            return FieldAssign(Variable('this'), field_name, value)
        
        # Variable declaration - must have type followed by ID
        if self.is_type():
            # Look ahead to see if this is really a declaration
            # Type followed by ID followed by = or ; means declaration
            # Type followed by ID followed by ( means method call (not declaration in statement context)
            start_pos = self.pos
            var_type = self.parse_type()
            
            if self.current().type == TokenType.ID:
                name = self.current().value
                self.advance()
                
                # Check what comes after the identifier
                if self.current().type in (TokenType.ASSIGN, TokenType.SEMICOLON):
                    # This is a variable declaration
                    value = None
                    if self.current().type == TokenType.ASSIGN:
                        self.advance()
                        value = self.parse_expr()
                    self.expect(TokenType.SEMICOLON)
                    return VarDecl(var_type, name, value)
                elif self.current().type == TokenType.LPAREN:
                    # This looks like a method call, not a declaration
                    # Back up and parse as expression statement
                    self.pos = start_pos
                    expr = self.parse_expr()
                    self.expect(TokenType.SEMICOLON)
                    return ExprStmt(expr)
                else:
                    # Unexpected token after ID in declaration context
                    value = None
                    if self.current().type == TokenType.ASSIGN:
                        self.advance()
                        value = self.parse_expr()
                    self.expect(TokenType.SEMICOLON)
                    return VarDecl(var_type, name, value)
            else:
                # Type not followed by ID - this is strange, back up
                self.pos = start_pos
        
        # Assignment or expression with ID
        if token.type == TokenType.ID:
            name = token.value
            self.advance()
            
            # Array assignment
            if self.current().type == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expr()
                self.expect(TokenType.RBRACKET)
                
                if self.current().type == TokenType.ASSIGN:
                    self.advance()
                    value = self.parse_expr()
                    self.expect(TokenType.SEMICOLON)
                    return ArrayAssign(name, index, value)
                else:
                    # Just array access as expression
                    self.pos -= 3  # Back up to start of expression
                    expr = self.parse_expr()
                    self.expect(TokenType.SEMICOLON)
                    return ExprStmt(expr)
            
            # Field assignment or method call
            if self.current().type == TokenType.DOT:
                # Parse the full postfix expression
                self.pos -= 1  # Back up to the ID
                expr = self.parse_expr()
                
                # Check if it's being assigned to (shouldn't happen for method calls)
                if self.current().type == TokenType.ASSIGN and isinstance(expr, FieldAccess):
                    self.advance()
                    value = self.parse_expr()
                    self.expect(TokenType.SEMICOLON)
                    return FieldAssign(expr.obj, expr.field, value)
                else:
                    # It's an expression statement (method call or field access)
                    self.expect(TokenType.SEMICOLON)
                    return ExprStmt(expr)
            
            # Regular assignment
            if self.current().type == TokenType.ASSIGN:
                self.advance()
                value = self.parse_expr()
                self.expect(TokenType.SEMICOLON)
                return Assign(name, value)
            
            # Compound assignment
            if self.current().type == TokenType.PLUSASSIGN:
                self.advance()
                value = self.parse_expr()
                self.expect(TokenType.SEMICOLON)
                return Assign(name, BinOp('+', Variable(name), value))
            
            if self.current().type == TokenType.MINUSASSIGN:
                self.advance()
                value = self.parse_expr()
                self.expect(TokenType.SEMICOLON)
                return Assign(name, BinOp('-', Variable(name), value))
            
            # Method call or other expression
            if self.current().type == TokenType.LPAREN:
                # Back up and parse as full expression
                self.pos -= 1
                expr = self.parse_expr()
                self.expect(TokenType.SEMICOLON)
                return ExprStmt(expr)
            
            # Just a standalone identifier or increment/decrement
            if self.current().type in (TokenType.PLUSPLUS, TokenType.MINUSMINUS):
                self.pos -= 1
                expr = self.parse_expr()
                self.expect(TokenType.SEMICOLON)
                return ExprStmt(expr)
            
            # Unknown case - treat as expression
            self.pos -= 1
            expr = self.parse_expr()
            self.expect(TokenType.SEMICOLON)
            return ExprStmt(expr)
        
        return None
    
    def parse_if(self) -> If:
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expr()
        self.expect(TokenType.RPAREN)
        
        then_block = self.parse_block()
        else_block = []
        
        if self.current().type == TokenType.ELSE:
            self.advance()
            if self.current().type == TokenType.IF:
                else_block = [self.parse_if()]
            else:
                else_block = self.parse_block()
        
        return If(condition, then_block, else_block)
    
    def parse_while(self) -> While:
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expr()
        self.expect(TokenType.RPAREN)
        
        body = self.parse_block()
        return While(condition, body)
    
    def parse_do_while(self) -> DoWhile:
        self.expect(TokenType.DO)
        body = self.parse_block()
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expr()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return DoWhile(body, condition)
    
    def parse_for(self) -> Union[For, ForEach]:
        self.expect(TokenType.FOR)
        self.expect(TokenType.LPAREN)
        
        # Enhanced for loop
        if self.is_type():
            start_pos = self.pos
            var_type = self.parse_type()
            
            if self.current().type == TokenType.ID:
                var = self.current().value
                self.advance()
                
                if self.current().type == TokenType.COLON:
                    self.advance()
                    iterable = self.parse_expr()
                    self.expect(TokenType.RPAREN)
                    body = self.parse_block()
                    return ForEach(var_type, var, iterable, body)
            
            self.pos = start_pos
        
        # Regular for loop
        init = None
        if self.current().type != TokenType.SEMICOLON:
            init = self.parse_stmt()
        else:
            self.advance()
        
        condition = None
        if self.current().type != TokenType.SEMICOLON:
            condition = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        
        update = None
        if self.current().type != TokenType.RPAREN:
            update_expr = self.parse_expr()
            update = ExprStmt(update_expr)
        
        self.expect(TokenType.RPAREN)
        body = self.parse_block()
        
        return For(init, condition, update, body)
    
    def parse_switch(self) -> Switch:
        self.expect(TokenType.SWITCH)
        self.expect(TokenType.LPAREN)
        expr = self.parse_expr()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        
        cases = []
        default = None
        
        while self.current().type in (TokenType.CASE, TokenType.DEFAULT):
            if self.current().type == TokenType.CASE:
                self.advance()
                value = self.parse_expr()
                self.expect(TokenType.COLON)
                
                stmts = []
                while self.current().type not in (TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE):
                    stmt = self.parse_stmt()
                    if stmt:
                        stmts.append(stmt)
                
                cases.append((value, stmts))
            
            elif self.current().type == TokenType.DEFAULT:
                self.advance()
                self.expect(TokenType.COLON)
                
                default = []
                while self.current().type not in (TokenType.CASE, TokenType.RBRACE):
                    stmt = self.parse_stmt()
                    if stmt:
                        default.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return Switch(expr, cases, default)
    
    def parse_try(self) -> Try:
        self.expect(TokenType.TRY)
        try_block = self.parse_block()
        
        catch_blocks = []
        while self.current().type == TokenType.CATCH:
            self.advance()
            self.expect(TokenType.LPAREN)
            exception_type = self.parse_type()
            var = self.current().value
            self.expect(TokenType.ID)
            self.expect(TokenType.RPAREN)
            catch_body = self.parse_block()
            catch_blocks.append((exception_type, var, catch_body))
        
        finally_block = None
        if self.current().type == TokenType.FINALLY:
            self.advance()
            finally_block = self.parse_block()
        
        return Try(try_block, catch_blocks, finally_block)
    
    def parse_block(self) -> List[Stmt]:
        if self.current().type == TokenType.LBRACE:
            self.expect(TokenType.LBRACE)
            stmts = []
            
            while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
                stmt = self.parse_stmt()
                if stmt:
                    stmts.append(stmt)
            
            self.expect(TokenType.RBRACE)
            return stmts
        else:
            # Single statement without braces
            stmt = self.parse_stmt()
            return [stmt] if stmt else []
    
    # Class and method parsing
    
    def parse_modifiers(self) -> List[str]:
        modifiers = []
        while self.current().type in (TokenType.PUBLIC, TokenType.PRIVATE, 
                                       TokenType.PROTECTED, TokenType.STATIC, TokenType.FINAL):
            modifiers.append(self.current().type.name.lower())
            self.advance()
        return modifiers
    
    def parse_method(self, modifiers: List[str]) -> MethodDecl:
        return_type = self.parse_type()
        
        if self.current().type != TokenType.ID:
            self.error("Expected method name")
        name = self.current().value
        self.advance()
        
        self.expect(TokenType.LPAREN)
        params = []
        if self.current().type != TokenType.RPAREN:
            param_type = self.parse_type()
            if self.current().type != TokenType.ID:
                self.error("Expected parameter name")
            param_name = self.current().value
            self.advance()
            params.append((param_type, param_name))
            
            while self.current().type == TokenType.COMMA:
                self.advance()
                param_type = self.parse_type()
                if self.current().type != TokenType.ID:
                    self.error("Expected parameter name")
                param_name = self.current().value
                self.advance()
                params.append((param_type, param_name))
        
        self.expect(TokenType.RPAREN)
        body = self.parse_block()
        
        return MethodDecl(modifiers, return_type, name, params, body)
    
    def parse_class(self) -> ClassDecl:
        modifiers = self.parse_modifiers()
        self.expect(TokenType.CLASS)
        name = self.current().value
        self.expect(TokenType.ID)
        self.expect(TokenType.LBRACE)
        
        fields = []
        constructors = []
        methods = []
        
        while self.current().type != TokenType.RBRACE and self.current().type != TokenType.EOF:
            member_mods = self.parse_modifiers()
            
            # Constructor (same name as class)
            if self.current().type == TokenType.ID and self.current().value == name:
                self.advance()
                self.expect(TokenType.LPAREN)
                params = []
                
                # Parse constructor parameters
                if self.current().type != TokenType.RPAREN:
                    param_type = self.parse_type()
                    if self.current().type != TokenType.ID:
                        self.error("Expected parameter name")
                    param_name = self.current().value
                    self.advance()
                    params.append((param_type, param_name))
                    
                    while self.current().type == TokenType.COMMA:
                        self.advance()
                        param_type = self.parse_type()
                        if self.current().type != TokenType.ID:
                            self.error("Expected parameter name")
                        param_name = self.current().value
                        self.advance()
                        params.append((param_type, param_name))
                
                self.expect(TokenType.RPAREN)
                body = self.parse_block()
                constructors.append(Constructor(member_mods, name, params, body))
            
            # Method or field
            elif self.is_type():
                start_pos = self.pos
                member_type = self.parse_type()
                
                if self.current().type != TokenType.ID:
                    self.error("Expected member name")
                member_name = self.current().value
                self.advance()
                
                if self.current().type == TokenType.LPAREN:
                    # It's a method - reset and parse properly
                    self.pos = start_pos
                    methods.append(self.parse_method(member_mods))
                else:
                    # It's a field
                    value = None
                    if self.current().type == TokenType.ASSIGN:
                        self.advance()
                        value = self.parse_expr()
                    self.expect(TokenType.SEMICOLON)
                    fields.append(FieldDecl(member_mods, member_type, member_name, value))
            else:
                self.advance()
        
        self.expect(TokenType.RBRACE)
        return ClassDecl(modifiers, name, fields, constructors, methods)
    
    def parse_program(self):
        classes = []
        stmts = []
        
        while self.current().type != TokenType.EOF:
            if self.current().type in (TokenType.PUBLIC, TokenType.PRIVATE, TokenType.CLASS):
                classes.append(self.parse_class())
            elif self.is_type() or self.current().type in (TokenType.IF, TokenType.WHILE, 
                                                             TokenType.FOR, TokenType.ID):
                stmt = self.parse_stmt()
                if stmt:
                    stmts.append(stmt)
            else:
                self.advance()
        
        return classes, stmts

# ===========================
# EVALUATOR
# ===========================

class JavaObject:
    def __init__(self, class_name: str, fields: Dict[str, Any]):
        self.class_name = class_name
        self.fields = fields

class Evaluator:
    def __init__(self):
        self.global_env: Dict[str, Any] = {}
        self.env_stack: List[Dict[str, Any]] = [self.global_env]
        self.classes: Dict[str, ClassDecl] = {}
        self.methods: Dict[str, MethodDecl] = {}
        self.current_object = None
    
    def current_env(self):
        return self.env_stack[-1]
    
    def push_env(self, env: Dict[str, Any] = None):
        self.env_stack.append(env if env else {})
    
    def pop_env(self):
        if len(self.env_stack) > 1:
            self.env_stack.pop()
    
    def get_var(self, name: str):
        # First check local/parameter variables
        for env in reversed(self.env_stack):
            if name in env:
                return env[name]
        
        # Then check current object's fields
        if self.current_object and isinstance(self.current_object, JavaObject):
            if name in self.current_object.fields:
                return self.current_object.fields[name]
        
        raise NameError(f"Variable '{name}' is not defined")
    
    def set_var(self, name: str, value: Any):
        # Check if variable exists in any scope
        for env in reversed(self.env_stack):
            if name in env:
                env[name] = value
                return
        
        # Check if it's a field of the current object
        if self.current_object and isinstance(self.current_object, JavaObject):
            if name in self.current_object.fields:
                self.current_object.fields[name] = value
                return
        
        # Otherwise create new variable in current scope
        self.current_env()[name] = value
    
    def eval_expr(self, expr: Expr) -> Any:
        
        if isinstance(expr, IntLit):
            return expr.value
        
        if isinstance(expr, FloatLit):
            return expr.value
        
        if isinstance(expr, StringLit):
            return expr.value
        
        if isinstance(expr, CharLit):
            return expr.value
        
        if isinstance(expr, BoolLit):
            return expr.value
        
        if isinstance(expr, NullLit):
            return None
        
        if isinstance(expr, Variable):
            if expr.name == 'this':
                return self.current_object
            return self.get_var(expr.name)
        
        if isinstance(expr, BinOp):
            left = self.eval_expr(expr.left)
            
            # Short-circuit evaluation
            if expr.op == '&&':
                return left and self.eval_expr(expr.right)
            if expr.op == '||':
                return left or self.eval_expr(expr.right)
            
            right = self.eval_expr(expr.right)
            
            # Special handling for + operator (addition or string concatenation)
            if expr.op == '+':
                # If either operand is a string, convert both to strings and concatenate
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                else:
                    return left + right
            
            ops = {
                '-': lambda l, r: l - r,
                '*': lambda l, r: l * r,
                '/': lambda l, r: l / r if r != 0 else self.error("Division by zero"),
                '%': lambda l, r: l % r,
                '==': lambda l, r: l == r,
                '!=': lambda l, r: l != r,
                '<': lambda l, r: l < r,
                '<=': lambda l, r: l <= r,
                '>': lambda l, r: l > r,
                '>=': lambda l, r: l >= r,
            }
            
            if expr.op in ops:
                return ops[expr.op](left, right)
        
        if isinstance(expr, UnaryOp):
            if expr.op == '!':
                return not self.eval_expr(expr.operand)
            elif expr.op == '-':
                return -self.eval_expr(expr.operand)
            elif expr.op == '++pre':
                var = expr.operand
                if isinstance(var, Variable):
                    val = self.get_var(var.name) + 1
                    self.set_var(var.name, val)
                    return val
            elif expr.op == '--pre':
                var = expr.operand
                if isinstance(var, Variable):
                    val = self.get_var(var.name) - 1
                    self.set_var(var.name, val)
                    return val
            elif expr.op == '++post':
                var = expr.operand
                if isinstance(var, Variable):
                    old = self.get_var(var.name)
                    self.set_var(var.name, old + 1)
                    return old
            elif expr.op == '--post':
                var = expr.operand
                if isinstance(var, Variable):
                    old = self.get_var(var.name)
                    self.set_var(var.name, old - 1)
                    return old
        
        if isinstance(expr, TernaryOp):
            cond = self.eval_expr(expr.condition)
            return self.eval_expr(expr.true_expr) if cond else self.eval_expr(expr.false_expr)
        
        if isinstance(expr, Cast):
            value = self.eval_expr(expr.expr)
            if 'int' in expr.target_type:
                return int(value)
            elif 'float' in expr.target_type or 'double' in expr.target_type:
                return float(value)
            elif 'String' in expr.target_type:
                return str(value)
            return value
        
        if isinstance(expr, NewArray):
            if expr.sizes:
                size = self.eval_expr(expr.sizes[0])
                return [0] * size if 'int' in expr.element_type else [None] * size
            return []
        
        if isinstance(expr, ArrayInit):
            return [self.eval_expr(e) for e in expr.elements]
        
        if isinstance(expr, ArrayAccess):
            array = self.eval_expr(expr.array)
            index = self.eval_expr(expr.index)
            return array[index]
        
        if isinstance(expr, FieldAccess):
            obj = self.eval_expr(expr.obj)
            if isinstance(obj, JavaObject):
                return obj.fields.get(expr.field)
            elif isinstance(obj, list) and expr.field == 'length':
                return len(obj)
            elif isinstance(obj, str) and expr.field == 'length':
                return len(obj)
        
        if isinstance(expr, NewObject):
            class_decl = self.classes.get(expr.class_name)
            if class_decl:
                fields = {}
                for field in class_decl.fields:
                    fields[field.name] = self.eval_expr(field.value) if field.value else None
                
                obj = JavaObject(expr.class_name, fields)
                
                # Run constructor
                for constructor in class_decl.constructors:
                    if len(constructor.params) == len(expr.args):
                        self.push_env()
                        old_obj = self.current_object
                        self.current_object = obj
                        
                        for (param_type, param_name), arg in zip(constructor.params, expr.args):
                            self.set_var(param_name, self.eval_expr(arg))
                        
                        for stmt in constructor.body:
                            self.eval_stmt(stmt)
                        
                        self.current_object = old_obj
                        self.pop_env()
                        break
                
                return obj
        
        if isinstance(expr, MethodCall):
            args = [self.eval_expr(arg) for arg in expr.args]
            
            # Built-in methods
            if expr.method in ('println', 'print'):
                if args:
                    print(args[0], end='\n' if expr.method == 'println' else '')
                else:
                    print()
                return None
            
            # Math methods
            if expr.obj and isinstance(expr.obj, Variable) and expr.obj.name == 'Math':
                math_funcs = {
                    'abs': abs, 'sqrt': math.sqrt, 'pow': pow,
                    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                    'floor': math.floor, 'ceil': math.ceil,
                    'max': max, 'min': min,
                }
                if expr.method in math_funcs:
                    return math_funcs[expr.method](*args)
            
            # String methods
            if expr.obj:
                obj = self.eval_expr(expr.obj)
                if isinstance(obj, str):
                    string_methods = {
                        'length': lambda: len(obj),
                        'substring': lambda start, end=None: obj[start:end] if end else obj[start:],
                        'toUpperCase': lambda: obj.upper(),
                        'toLowerCase': lambda: obj.lower(),
                        'charAt': lambda i: obj[i],
                        'indexOf': lambda s: obj.find(s),
                        'replace': lambda old, new: obj.replace(old, new),
                    }
                    if expr.method in string_methods:
                        return string_methods[expr.method](*args)
                
                # Object methods
                if isinstance(obj, JavaObject):
                    class_decl = self.classes.get(obj.class_name)
                    for method in class_decl.methods:
                        if method.name == expr.method and len(method.params) == len(args):
                            self.push_env()
                            old_obj = self.current_object
                            self.current_object = obj
                            
                            for (param_type, param_name), arg_val in zip(method.params, args):
                                self.set_var(param_name, arg_val)
                            
                            try:
                                for stmt in method.body:
                                    self.eval_stmt(stmt)
                                result = None
                            except ReturnException as e:
                                result = e.value
                            
                            self.current_object = old_obj
                            self.pop_env()
                            return result
            
            # Global methods
            if expr.method in self.methods:
                method = self.methods[expr.method]
                if len(method.params) == len(args):
                    self.push_env()
                    
                    for (param_type, param_name), arg_val in zip(method.params, args):
                        self.set_var(param_name, arg_val)
                    
                    try:
                        for stmt in method.body:
                            self.eval_stmt(stmt)
                        result = None
                    except ReturnException as e:
                        result = e.value
                    
                    self.pop_env()
                    return result
        
        return None
    
    def error(self, msg: str):
        raise RuntimeError(msg)
    
    def eval_stmt(self, stmt: Stmt):
        if isinstance(stmt, VarDecl):
            value = self.eval_expr(stmt.value) if stmt.value else self.get_default_value(stmt.var_type)
            self.set_var(stmt.name, value)
        
        elif isinstance(stmt, Assign):
            value = self.eval_expr(stmt.value)
            self.set_var(stmt.target, value)
        
        elif isinstance(stmt, ArrayAssign):
            array = self.get_var(stmt.array)
            index = self.eval_expr(stmt.index)
            value = self.eval_expr(stmt.value)
            array[index] = value
        
        elif isinstance(stmt, FieldAssign):
            obj = self.eval_expr(stmt.obj)
            if isinstance(obj, JavaObject):
                obj.fields[stmt.field] = self.eval_expr(stmt.value)
        
        elif isinstance(stmt, If):
            if self.eval_expr(stmt.condition):
                for s in stmt.then_block:
                    self.eval_stmt(s)
            else:
                for s in stmt.else_block:
                    self.eval_stmt(s)
        
        elif isinstance(stmt, While):
            while self.eval_expr(stmt.condition):
                try:
                    for s in stmt.body:
                        self.eval_stmt(s)
                except BreakException:
                    break
                except ContinueException:
                    continue
        
        elif isinstance(stmt, DoWhile):
            while True:
                try:
                    for s in stmt.body:
                        self.eval_stmt(s)
                except BreakException:
                    break
                except ContinueException:
                    pass
                
                if not self.eval_expr(stmt.condition):
                    break
        
        elif isinstance(stmt, For):
            if stmt.init:
                self.eval_stmt(stmt.init)
            
            while True:
                if stmt.condition and not self.eval_expr(stmt.condition):
                    break
                
                try:
                    for s in stmt.body:
                        self.eval_stmt(s)
                except BreakException:
                    break
                except ContinueException:
                    pass
                
                if stmt.update:
                    self.eval_stmt(stmt.update)
        
        elif isinstance(stmt, ForEach):
            iterable = self.eval_expr(stmt.iterable)
            for item in iterable:
                self.set_var(stmt.var, item)
                try:
                    for s in stmt.body:
                        self.eval_stmt(s)
                except BreakException:
                    break
                except ContinueException:
                    continue
        
        elif isinstance(stmt, Switch):
            value = self.eval_expr(stmt.expr)
            matched = False
            
            for case_val, case_stmts in stmt.cases:
                case_result = self.eval_expr(case_val)
                if value == case_result or matched:
                    matched = True
                    try:
                        for s in case_stmts:
                            self.eval_stmt(s)
                    except BreakException:
                        break
            
            if not matched and stmt.default:
                for s in stmt.default:
                    self.eval_stmt(s)
        
        elif isinstance(stmt, Break):
            raise BreakException()
        
        elif isinstance(stmt, Continue):
            raise ContinueException()
        
        elif isinstance(stmt, Return):
            value = self.eval_expr(stmt.expr) if stmt.expr else None
            raise ReturnException(value)
        
        elif isinstance(stmt, ExprStmt):
            self.eval_expr(stmt.expr)
        
        elif isinstance(stmt, Try):
            try:
                for s in stmt.try_block:
                    self.eval_stmt(s)
            except Exception as e:
                for exception_type, var, catch_body in stmt.catch_blocks:
                    self.push_env()
                    self.set_var(var, str(e))
                    for s in catch_body:
                        self.eval_stmt(s)
                    self.pop_env()
                    break
            finally:
                if stmt.finally_block:
                    for s in stmt.finally_block:
                        self.eval_stmt(s)
    
    def get_default_value(self, type_str: str):
        if 'int' in type_str:
            return 0
        elif 'float' in type_str or 'double' in type_str:
            return 0.0
        elif 'boolean' in type_str:
            return False
        elif 'String' in type_str:
            return ''
        elif '[]' in type_str:
            return []
        return None
    
    def eval_program(self, classes: List[ClassDecl], stmts: List[Stmt]):
        # Register classes
        for class_decl in classes:
            self.classes[class_decl.name] = class_decl
            
            # Register static methods
            for method in class_decl.methods:
                if 'static' in method.modifiers:
                    self.methods[method.name] = method
        
        # Find and run main method
        for class_decl in classes:
            for method in class_decl.methods:
                if method.name == 'main' and 'static' in method.modifiers:
                    self.push_env()
                    try:
                        for stmt in method.body:
                            self.eval_stmt(stmt)
                    except ReturnException:
                        pass
                    self.pop_env()
                    return
        
        # No main found, execute statements directly
        for stmt in stmts:
            self.eval_stmt(stmt)

# ===========================
# MAIN
# ===========================

def interpret(code: str):
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        classes, stmts = parser.parse_program()
        
        evaluator = Evaluator()
        evaluator.eval_program(classes, stmts)
        
    except (SyntaxError, NameError, RuntimeError, IndexError, ZeroDivisionError) as e:
        print(f"Error: {e}")






def ast_to_dict(node, depth=0):
    """Convert AST node to dictionary for visualization"""
    if depth > 20:  # Prevent infinite recursion
        return {"type": "...", "children": []}
    
    result = {"type": type(node).__name__, "children": []}
    
    # Handle different node types
    if isinstance(node, IntLit):
        result["value"] = node.value
    elif isinstance(node, StringLit):
        result["value"] = node.value
    elif isinstance(node, Variable):
        result["name"] = node.name
    elif isinstance(node, BinOp):
        result["operator"] = node.op
        result["children"] = [
            ast_to_dict(node.left, depth+1),
            ast_to_dict(node.right, depth+1)
        ]
    elif isinstance(node, MethodCall):
        result["method"] = node.method
        if node.obj:
            result["children"].append(ast_to_dict(node.obj, depth+1))
        for arg in node.args:
            result["children"].append(ast_to_dict(arg, depth+1))
    elif isinstance(node, VarDecl):
        result["varType"] = node.var_type
        result["name"] = node.name
        if node.value:
            result["children"] = [ast_to_dict(node.value, depth+1)]
    elif isinstance(node, ClassDecl):
        result["name"] = node.name
        result["extends"] = node.extends if hasattr(node, 'extends') else None
        for field in node.fields:
            result["children"].append(ast_to_dict(field, depth+1))
        for method in node.methods:
            result["children"].append(ast_to_dict(method, depth+1))
    elif isinstance(node, MethodDecl):
        result["name"] = node.name
        result["returnType"] = node.return_type
        for stmt in node.body:
            result["children"].append(ast_to_dict(stmt, depth+1))
    elif isinstance(node, If):
        result["children"] = [
            {"type": "condition", "children": [ast_to_dict(node.condition, depth+1)]},
            {"type": "then", "children": [ast_to_dict(s, depth+1) for s in node.then_block]},
        ]
        if node.else_block:
            result["children"].append({"type": "else", "children": [ast_to_dict(s, depth+1) for s in node.else_block]})
    elif isinstance(node, While):
        result["children"] = [
            {"type": "condition", "children": [ast_to_dict(node.condition, depth+1)]},
            {"type": "body", "children": [ast_to_dict(s, depth+1) for s in node.body]}
        ]
    elif isinstance(node, For):
        result["children"] = []
        if node.init:
            result["children"].append({"type": "init", "children": [ast_to_dict(node.init, depth+1)]})
        if node.condition:
            result["children"].append({"type": "condition", "children": [ast_to_dict(node.condition, depth+1)]})
        if node.update:
            result["children"].append({"type": "update", "children": [ast_to_dict(node.update, depth+1)]})
        result["children"].append({"type": "body", "children": [ast_to_dict(s, depth+1) for s in node.body]})
    elif isinstance(node, Assign):
        result["target"] = node.target
        result["children"] = [ast_to_dict(node.value, depth+1)]
    elif isinstance(node, Return):
        if node.expr:
            result["children"] = [ast_to_dict(node.expr, depth+1)]
    elif isinstance(node, ExprStmt):
        result["children"] = [ast_to_dict(node.expr, depth+1)]
    elif isinstance(node, FieldDecl):
        result["fieldType"] = node.field_type
        result["name"] = node.name
        if node.value:
            result["children"] = [ast_to_dict(node.value, depth+1)]
    
    return result

def parse_to_ast_json(code: str):
    """Parse code and return AST as JSON"""
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        classes, stmts = parser.parse_program()
        
        # Build AST tree
        ast_tree = {
            "type": "Program",
            "children": []
        }
        
        for class_decl in classes:
            ast_tree["children"].append(ast_to_dict(class_decl))
        
        for stmt in stmts:
            ast_tree["children"].append(ast_to_dict(stmt))
        
        return json.dumps(ast_tree, indent=2)
        
    except Exception as e:
        return json.dumps({"type": "Error", "message": str(e), "children": []})


if __name__ == "__main__":
    import sys
    
    # Check if we want AST output
    if len(sys.argv) > 1 and sys.argv[1] == '--ast':
        # Read from stdin
        code = sys.stdin.read()
        ast_json = parse_to_ast_json(code)
        print(ast_json)
    else:
        # Normal execution
        code = sys.stdin.read()
        interpret(code)



    