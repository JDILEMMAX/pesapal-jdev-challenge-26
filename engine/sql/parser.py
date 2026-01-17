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
    
    def _consume_optional_semicolon(self):
        """Advance past a semicolon if present; do nothing if not."""
        if self._peek().type == TokenType.SYMBOL and self._peek().value == ";":
            self._advance()

    def parse(self) -> ASTNode:
        tok = self._peek()
        if tok.value.upper() == "CREATE":
            return self._parse_create()
        elif tok.value.upper() == "INSERT":
            return self._parse_insert()
        elif tok.value.upper() == "SELECT":
            return self._parse_select()
        elif tok.value.upper() == "SHOW":
            return self._parse_show_tables()
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
            # Parse column name
            col_name = self._expect(TokenType.IDENTIFIER).value

            # Optional type
            tok = self._peek()
            if tok.type == TokenType.IDENTIFIER:
                col_type = self._advance().value.upper()
            else:
                col_type = "TEXT"  # default type

            columns.append((col_name, col_type))

            tok = self._peek()
            if tok.value == ")":
                self._advance()  # consume closing parenthesis
                break
            self._expect(TokenType.SYMBOL, ",")

        # Optional semicolon
        self._consume_optional_semicolon()
        
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

        # Optional semicolon
        self._consume_optional_semicolon()

        return Insert(table=table_name, values=values)

    # --------------------------
    def _parse_select(self) -> Select:
        self._expect(TokenType.KEYWORD, "SELECT")
        columns = []

        while True:
            tok = self._advance()

            # Accept identifier or "*" for SELECT *
            if tok.type == TokenType.IDENTIFIER or tok.value == "*":
                columns.append(Column(tok.value))
            else:
                raise SyntaxError("Expected column name or '*' in SELECT")

            tok = self._peek()
            if tok.value.upper() == "FROM":
                break
            elif tok.value == ",":
                self._advance()
            else:
                raise SyntaxError("Expected ',' or 'FROM' in SELECT")

        self._expect(TokenType.KEYWORD, "FROM")
        table_name = self._expect(TokenType.IDENTIFIER).value

        # Optional WHERE clause
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

        # Optional semicolon (EOF allowed)
        self._consume_optional_semicolon()

        return Select(columns=columns, table=table_name, where=where_clause)

    # --------------------------
    def _parse_show_tables(self) -> 'ShowTables':
        self._expect(TokenType.KEYWORD, "SHOW")
        self._expect(TokenType.KEYWORD, "TABLES")
        self._consume_optional_semicolon()
        return ShowTables()
