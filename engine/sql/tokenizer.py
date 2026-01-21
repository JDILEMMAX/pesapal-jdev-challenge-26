from enum import Enum, auto
from typing import List, NamedTuple


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    SYMBOL = auto()
    LITERAL = auto()
    EOF = auto()


class Token(NamedTuple):
    type: TokenType
    value: str


KEYWORDS = {
    "CREATE", "TABLE", "DROP",
    "INSERT", "INTO", "VALUES",
    "SELECT", "FROM", "WHERE",
    "UPDATE", "SET", "DELETE",
    "JOIN", "ON",
    "GROUP", "BY", "HAVING",
    "ORDER", "ASC", "DESC",
    "LIMIT", "OFFSET",
    "PRIMARY", "KEY", "NOT", "NULL",
    "UNIQUE", "AUTO_INCREMENT",
    "REFERENCES",
    "INTEGER", "INT", "FLOAT",
    "VARCHAR", "BOOLEAN", "TEXT",
    "DATE", "TIMESTAMP",
    "SHOW", "TABLES",
    "INNER",
}
SYMBOLS = {"(", ")", ",", ";", "=", "<", ">", "*"}


class Tokenizer:
    def __init__(self, sql: str):
        self.sql = sql
        self.pos = 0
        self.length = len(sql)

    def _peek(self) -> str:
        return self.sql[self.pos] if self.pos < self.length else ""

    def _advance(self):
        self.pos += 1

    def _skip_whitespace(self):
        while self._peek().isspace():
            self._advance()

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.pos < self.length:
            self._skip_whitespace()
            current = self._peek()
            if not current:
                break
            elif current.isalpha() or current == "_":
                start = self.pos
                while self._peek().isalnum() or self._peek() == "_":
                    self._advance()
                word = self.sql[start : self.pos].upper()
                token_type = (
                    TokenType.KEYWORD if word in KEYWORDS else TokenType.IDENTIFIER
                )
                tokens.append(Token(token_type, word))
            elif current.isdigit() or current == "'":
                if current == "'":
                    self._advance()
                    start = self.pos
                    while self._peek() != "'" and self._peek():
                        self._advance()
                    if not self._peek():
                        raise SyntaxError("Unterminated string literal")
                    literal = self.sql[start : self.pos]
                    self._advance()
                    tokens.append(Token(TokenType.LITERAL, literal))
                else:
                    # Handle integers and floats
                    start = self.pos
                    while self._peek().isdigit():
                        self._advance()
                    # Check for decimal point
                    if self._peek() == "." and self.pos + 1 < self.length and self.sql[self.pos + 1].isdigit():
                        self._advance()  # consume '.'
                        while self._peek().isdigit():
                            self._advance()
                    tokens.append(Token(TokenType.LITERAL, self.sql[start : self.pos]))
            elif current in SYMBOLS:
                tokens.append(Token(TokenType.SYMBOL, current))
                self._advance()
            else:
                raise SyntaxError(f"Unexpected character: '{current}'")
        tokens.append(Token(TokenType.EOF, ""))
        return tokens
