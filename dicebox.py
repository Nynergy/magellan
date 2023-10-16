"""
Library for parsing and evaluating dice notation strings
"""

import re

from functools import reduce
from random import randint

""" AST """

class Aexp():
    pass

class IntAexp(Aexp):
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return f'IntAexp({self.i})'

    def eval(self, env):
        return self.i

class BinopAexp(Aexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'BinopAexp({self.op}, {self.left}, {self.right})'

    def eval(self, env):
        left_value = self.left.eval(env)
        right_value = self.right.eval(env)

        if self.op in ['d', 'D']:
            value = 0
            for i in range(left_value):
                value += randint(1, right_value)
        elif self.op == '*':
            value = left_value * right_value
        elif self.op == '/':
            value = left_value // right_value
        elif self.op == '+':
            value = left_value + right_value
        elif self.op == '-':
            value = left_value - right_value
        else:
            raise RuntimeError(f'Unknown operator: {self.op}')
        return value

""" COMBINATORS """

class Result:
    def __init__(self, value, pos):
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f'Result({self.value}, {self.pos})'

class Parser:
    def __call__(self, tokens, pos):
        return None # Subclasses will override this

    def __add__(self, other):
        return Concat(self, other)

    def __mul__(self, other):
        return Exp(self, other)

    def __or__(self, other):
        return Alternate(self, other)

    def __xor__(self, function):
        return Process(self, function)

class Reserved(Parser):
    def __init__(self, value, tag):
        self.value = value
        self.tag = tag

    def __call__(self, tokens, pos):
        if pos < len(tokens) and tokens[pos][0] == self.value and tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None

class Tag(Parser):
    def __init__(self, tag):
        self.tag = tag

    def __call__(self, tokens, pos):
        if pos < len(tokens) and tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None

class Concat(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        left_result = self.left(tokens, pos)
        if left_result:
            right_result = self.right(tokens, left_result.pos)
            if right_result:
                combined_value = (left_result.value, right_result.value)
                return Result(combined_value, right_result.pos)
        return None

class Alternate(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        left_result = self.left(tokens, pos)
        if left_result:
            return left_result
        else:
            right_result = self.right(tokens, pos)
            return right_result

class Opt(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result:
            return result
        else:
            return Result(None, pos)

class Rep(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        results = []
        result = self.parser(tokens, pos)
        while result:
            results.append(result.value)
            pos = result.pos
            result = self.parser(tokens, pos)
        return Result(results, pos)

class Process(Parser):
    def __init__(self, parser, function):
        self.parser = parser
        self.function = function

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result:
            result.value = self.function(result.value)
            return result

class Lazy(Parser):
    def __init__(self, parser_func):
        self.parser = None
        self.parser_func = parser_func

    def __call__(self, tokens, pos):
        if not self.parser:
            self.parser = self.parser_func()
        return self.parser(tokens, pos)

class Phrase(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result and result.pos == len(tokens):
            return result
        else:
            return None

class Exp(Parser):
    def __init__(self, parser, separator):
        self.parser = parser
        self.separator = separator

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)

        def process_next(parsed):
            (sepfunc, right) = parsed
            return sepfunc(result.value, right)

        next_parser = self.separator + self.parser ^ process_next
        next_result = result

        while next_result:
            next_result = next_parser(tokens, result.pos)
            if next_result:
                result = next_result
        return result

""" PARSER """

RESERVED = 'RESERVED'
INT      = 'INT'

token_exprs = [
    (r'[ \n\t]+',   None),
    (r'\(',         RESERVED),
    (r'\)',         RESERVED),
    (r'\+',         RESERVED),
    (r'-',          RESERVED),
    (r'\*',         RESERVED),
    (r'/',          RESERVED),
    (r'(d|D)',      RESERVED),
    (r'[0-9]+',     INT),
]

def keyword(kw):
    return Reserved(kw, RESERVED)

num = Tag(INT) ^ (lambda i: int(i))

def aexp_value():
    return num ^ (lambda i: IntAexp(i))

def process_group(parsed):
    ((_, p), _) = parsed
    return p

def aexp_group():
    return keyword('(') + Lazy(aexp) + keyword(')') ^ process_group

def aexp_term():
    return aexp_value() | aexp_group()

def process_binop(op):
    return lambda l, r: BinopAexp(op, l, r)

def any_operator_in_list(ops):
    op_parsers = [ keyword(op) for op in ops ]
    parser = reduce(lambda l, r: l | r, op_parsers)
    return parser

aexp_precedence_levels = [
    ['d', 'D'],
    ['*', '/'],
    ['+', '-'],
]

def precedence(value_parser, precedence_levels, combine):
    def op_parser(precedence_level):
        return any_operator_in_list(precedence_level) ^ combine
    parser = value_parser * op_parser(precedence_levels[0])
    for precedence_level in precedence_levels[1:]:
        parser = parser * op_parser(precedence_level)
    return parser

def aexp():
    return precedence(aexp_term(), aexp_precedence_levels, process_binop)

def aexp_stmt():
    return aexp()

def stmt():
    return aexp_stmt()

def parser():
    return Phrase(stmt())

def parse_dice(tokens):
    ast = parser()(tokens, 0)
    return ast

""" LEXER """

def lex(string, token_exprs):
    pos = 0
    tokens = []
    
    while pos < len(string):
        match = None
        for expr in token_exprs:
            pattern, tag = expr
            regex = re.compile(pattern)
            match = regex.match(string, pos)

            if match:
                text = match.group(0)
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                break

        if not match:
            raise SyntaxError(f'Illegal character: {string[pos]}')
        else:
            pos = match.end(0)

    return tokens

def lex_dice(string):
    return lex(string, token_exprs)

""" PUBLIC API """

def roll(dice_string):
    tokens = lex_dice(dice_string)
    result = parse_dice(tokens)

    if not result:
        raise RuntimeError(f'Parse error on input: {dice_string}')

    ast = result.value
    value = ast.eval({})

    return value
