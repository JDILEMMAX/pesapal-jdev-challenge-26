from typing import List
from .tokenizer import Token, TokenType
from .ast import *


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, token_type: TokenType, value: str = None) -> Token:
        tok = self._advance()
        if tok.type != token_type or (value and tok.value.upper() != value.upper()):
            raise SyntaxError(
                f"Expected {token_type} '{value}', got {tok.type} '{tok.value}'"
            )
        return tok

    def parse(self) -> ASTNode:
        tok = self._peek()
        if tok.value.upper() == "CREATE":
            return self._parse_create()
        elif tok.value.upper() == "INSERT":
            return self._parse_insert()
        elif tok.value.upper() == "SELECT":
            return self._parse_select()
        else:
            raise SyntaxError(f"Unsupported statement: {tok.value}")

    # --------------------------
    def _parse_create(self) -> CreateTable:
        self._expect(TokenType.KEYWORD, "CREATE")
        self._expect(TokenType.KEYWORD, "TABLE")
        table_name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.SYMBOL, "(")

        columns = []

        while True:
            col_name = self._expect(TokenType.IDENTIFIER).value
            col_type = self._expect(TokenType.IDENTIFIER).value
            columns.append((col_name, col_type.upper()))

            tok = self._peek()
            if tok.value == ")":
                self._advance()  # consume closing parenthesis
                break
            self._expect(TokenType.SYMBOL, ",")

        self._expect(TokenType.SYMBOL, ";")
        return CreateTable(name=table_name, columns=columns)

    # --------------------------
    def _parse_insert(self) -> Insert:
        self._expect(TokenType.KEYWORD, "INSERT")
        self._expect(TokenType.KEYWORD, "INTO")
        table_name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.KEYWORD, "VALUES")
        self._expect(TokenType.SYMBOL, "(")
        values = []

        while True:
            tok = self._advance()
            if tok.type != TokenType.LITERAL:
                raise SyntaxError("Expected literal in VALUES")
            values.append(Literal(tok.value))

            tok = self._peek()
            if tok.value == ")":
                self._advance()
                break
            self._expect(TokenType.SYMBOL, ",")

        self._expect(TokenType.SYMBOL, ";")
        return Insert(table=table_name, values=values)

    # --------------------------
    def _parse_select(self) -> Select:
        self._expect(TokenType.KEYWORD, "SELECT")
        columns = []

        while True:
            tok = self._advance()
            if tok.type != TokenType.IDENTIFIER:
                raise SyntaxError("Expected column name in SELECT")
            columns.append(Column(tok.value))

            tok = self._peek()
            if tok.value.upper() == "FROM":
                break
            elif tok.value == ",":
                self._advance()
            else:
                raise SyntaxError("Expected ',' or 'FROM' in SELECT")

        self._expect(TokenType.KEYWORD, "FROM")
        table_name = self._expect(TokenType.IDENTIFIER).value

        where_clause = None
        if self._peek().value.upper() == "WHERE":
            self._advance()
            left = Column(self._expect(TokenType.IDENTIFIER).value)
            op = self._expect(TokenType.SYMBOL).value
            right_tok = self._advance()
            if right_tok.type != TokenType.LITERAL:
                raise SyntaxError("Expected literal in WHERE")
            right = Literal(right_tok.value)
            where_clause = BinaryExpression(left, op, right)

        self._expect(TokenType.SYMBOL, ";")
        return Select(columns=columns, table=table_name, where=where_clause)
