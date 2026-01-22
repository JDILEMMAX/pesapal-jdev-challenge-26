from typing import List, Optional
from .tokenizer import Token, TokenType
from .ast import *


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # =========================
    # Core helpers
    # =========================

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
        if self._peek().type == TokenType.SYMBOL and self._peek().value == ";":
            self._advance()

    # =========================
    # Entry point
    # =========================

    def parse(self) -> ASTNode:
        tok = self._peek()

        if tok.value.upper() == "CREATE":
            return self._parse_create()
        elif tok.value.upper() == "DROP":
            return self._parse_drop()
        elif tok.value.upper() == "INSERT":
            return self._parse_insert()
        elif tok.value.upper() == "UPDATE":
            return self._parse_update()
        elif tok.value.upper() == "DELETE":
            return self._parse_delete()
        elif tok.value.upper() == "SELECT":
            return self._parse_select()
        elif tok.value.upper() == "SHOW":
            return self._parse_show_tables()
        else:
            raise SyntaxError(f"Unsupported statement: {tok.value}")

    # =========================
    # CREATE TABLE
    # =========================

    def _parse_create(self) -> CreateTable:
        self._expect(TokenType.KEYWORD, "CREATE")
        self._expect(TokenType.KEYWORD, "TABLE")
        table_name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.SYMBOL, "(")

        columns = []

        while True:
            columns.append(self._parse_column_def())
            if self._peek().value == ")":
                self._advance()
                break
            self._expect(TokenType.SYMBOL, ",")

        self._consume_optional_semicolon()
        return CreateTable(name=table_name, columns=columns)

    def _parse_column_def(self) -> ColumnDef:
        name = self._expect(TokenType.IDENTIFIER).value

        # ---- Data type ----
        type_tok = self._advance()
        dtype_name = type_tok.value.upper()
        args = None

        if dtype_name == "VARCHAR":
            self._expect(TokenType.SYMBOL, "(")
            size = int(self._expect(TokenType.LITERAL).value)
            self._expect(TokenType.SYMBOL, ")")
            args = [size]

        dtype = DataType(dtype_name, args)

        # ---- Constraints (parsed only) ----
        constraints = []
        while self._peek().type == TokenType.KEYWORD:
            kw = self._peek().value.upper()

            if kw == "PRIMARY":
                self._advance()
                self._expect(TokenType.KEYWORD, "KEY")
                constraints.append(ColumnConstraint("PRIMARY_KEY"))

            elif kw == "NOT":
                self._advance()
                self._expect(TokenType.KEYWORD, "NULL")
                constraints.append(ColumnConstraint("NOT_NULL"))

            elif kw == "UNIQUE":
                self._advance()
                constraints.append(ColumnConstraint("UNIQUE"))

            elif kw == "AUTO_INCREMENT":
                self._advance()
                constraints.append(ColumnConstraint("AUTO_INCREMENT"))

            elif kw == "REFERENCES":
                self._advance()
                ref_table = self._expect(TokenType.IDENTIFIER).value
                self._expect(TokenType.SYMBOL, "(")
                ref_col = self._expect(TokenType.IDENTIFIER).value
                self._expect(TokenType.SYMBOL, ")")
                constraints.append(
                    ColumnConstraint("FOREIGN_KEY", ref_table, ref_col)
                )
            else:
                break

        return ColumnDef(name, dtype, constraints)

    # =========================
    # DROP TABLE
    # =========================

    def _parse_drop(self) -> DropTable:
        self._expect(TokenType.KEYWORD, "DROP")
        self._expect(TokenType.KEYWORD, "TABLE")
        name = self._expect(TokenType.IDENTIFIER).value
        self._consume_optional_semicolon()
        return DropTable(name)

    # =========================
    # INSERT
    # =========================

    def _parse_insert(self) -> Insert:
        self._expect(TokenType.KEYWORD, "INSERT")
        self._expect(TokenType.KEYWORD, "INTO")
        table_name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.KEYWORD, "VALUES")
        self._expect(TokenType.SYMBOL, "(")

        values = []
        while True:
            tok = self._peek()
            if tok.value.upper() == "NULL":
                self._advance()
                values.append(Literal(None))
            else:
                tok = self._advance()
                if tok.type != TokenType.LITERAL:
                    raise SyntaxError("Expected literal or NULL in VALUES")
                values.append(Literal(tok.value))

            if self._peek().value == ")":
                self._advance()
                break
            self._expect(TokenType.SYMBOL, ",")

        self._consume_optional_semicolon()
        return Insert(table=table_name, values=values)

    # =========================
    # UPDATE
    # =========================

    def _parse_update(self) -> Update:
        self._expect(TokenType.KEYWORD, "UPDATE")
        table = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.KEYWORD, "SET")

        assignments = {}
        while True:
            col = self._expect(TokenType.IDENTIFIER).value
            self._expect(TokenType.SYMBOL, "=")
            val = Literal(self._expect(TokenType.LITERAL).value)
            assignments[col] = val

            if self._peek().value != ",":
                break
            self._advance()

        where = None
        if self._peek().value.upper() == "WHERE":
            self._advance()
            where = self._parse_binary_expression()

        self._consume_optional_semicolon()
        return Update(table, assignments, where)

    # =========================
    # DELETE
    # =========================

    def _parse_delete(self) -> Delete:
        self._expect(TokenType.KEYWORD, "DELETE")
        self._expect(TokenType.KEYWORD, "FROM")
        table = self._expect(TokenType.IDENTIFIER).value

        where = None
        if self._peek().value.upper() == "WHERE":
            self._advance()
            where = self._parse_binary_expression()

        self._consume_optional_semicolon()
        return Delete(table, where)

    # =========================
    # SELECT
    # =========================

    def _parse_select(self) -> Select:
        self._expect(TokenType.KEYWORD, "SELECT")
        columns = []

        while True:
            tok = self._advance()
            if tok.type == TokenType.IDENTIFIER or tok.value == "*":
                col_name = tok.value
                
                # Check for qualified column name (table.column)
                if self._peek().value == ".":
                    self._advance()  # consume .
                    next_tok = self._expect(TokenType.IDENTIFIER)
                    col_name = f"{tok.value}.{next_tok.value}"
                
                # Check for function call like COUNT(*)
                if self._peek().value == "(":
                    self._advance()  # consume (
                    inner_tok = self._advance()  # get * or column name
                    self._expect(TokenType.SYMBOL, ")")
                    # Store as "FUNCTION(arg)" name
                    col_name = f"{col_name}({inner_tok.value})"
                
                # Check for alias (AS alias_name)
                if self._peek().value.upper() == "AS":
                    self._advance()  # consume AS
                    alias_tok = self._expect(TokenType.IDENTIFIER)
                    col_name = f"{col_name} AS {alias_tok.value}"
                
                columns.append(Column(col_name))
            else:
                raise SyntaxError("Expected column name or '*' in SELECT")

            if self._peek().value.upper() == "FROM":
                break
            elif self._peek().value == ",":
                self._advance()
            else:
                raise SyntaxError("Expected ',' or 'FROM' in SELECT")

        self._expect(TokenType.KEYWORD, "FROM")
        table_name = self._expect(TokenType.IDENTIFIER).value

        # Handle table alias
        table_alias = None
        if self._peek().type == TokenType.IDENTIFIER:
            table_alias = self._advance().value
        
        join_node = None
        if self._peek().value.upper() == "INNER":
            self._advance()  # consume INNER
            self._expect(TokenType.KEYWORD, "JOIN")
            right_table = self._expect(TokenType.IDENTIFIER).value
            
            # Handle right table alias
            right_alias = None
            if self._peek().type == TokenType.IDENTIFIER:
                right_alias = self._advance().value
            
            self._expect(TokenType.KEYWORD, "ON")
            
            # Parse left side of ON clause (may include table alias)
            left_col = self._expect(TokenType.IDENTIFIER).value
            if self._peek().value == ".":
                self._advance()  # consume .
                left_col_name = self._expect(TokenType.IDENTIFIER).value
                left_col = f"{left_col}.{left_col_name}"
            
            self._expect(TokenType.SYMBOL, "=")
            
            # Parse right side of ON clause (may include table alias)
            right_col = self._expect(TokenType.IDENTIFIER).value
            if self._peek().value == ".":
                self._advance()  # consume .
                right_col_name = self._expect(TokenType.IDENTIFIER).value
                right_col = f"{right_col}.{right_col_name}"

            join_node = Join(
                left_table=table_name,
                right_table=right_table,
                left_column=left_col,
                right_column=right_col,
            )

        where = None
        if self._peek().value.upper() == "WHERE":
            self._advance()
            where = self._parse_binary_expression()

        group_by = None
        if self._peek().value.upper() == "GROUP":
            self._advance()  # consume GROUP
            self._expect(TokenType.KEYWORD, "BY")
            group_by = []
            while True:
                col_name = self._expect(TokenType.IDENTIFIER).value
                # Handle qualified column names in GROUP BY
                if self._peek().value == ".":
                    self._advance()  # consume .
                    col_name = f"{col_name}.{self._expect(TokenType.IDENTIFIER).value}"
                group_by.append(Column(col_name))
                if self._peek().value != ",":
                    break
                self._advance()

        having = None
        if self._peek().value.upper() == "HAVING":
            self._advance()
            having = self._parse_binary_expression()

        order_by = None
        if self._peek().value.upper() == "ORDER":
            self._advance()  # consume ORDER
            self._expect(TokenType.KEYWORD, "BY")
            order_by = []
            while True:
                col_name = self._expect(TokenType.IDENTIFIER).value
                # Handle qualified column names in ORDER BY
                if self._peek().value == ".":
                    self._advance()  # consume .
                    col_name = f"{col_name}.{self._expect(TokenType.IDENTIFIER).value}"
                direction = "ASC"
                if self._peek().value.upper() in ["ASC", "DESC"]:
                    direction = self._advance().value.upper()
                order_by.append((col_name.lower(), direction))
                if self._peek().value != ",":
                    break
                self._advance()

        limit = None
        if self._peek().value.upper() == "LIMIT":
            self._advance()
            limit = int(self._expect(TokenType.LITERAL).value)

        offset = None
        if self._peek().value.upper() == "OFFSET":
            self._advance()
            offset = int(self._expect(TokenType.LITERAL).value)

        self._consume_optional_semicolon()
        table_field = join_node if join_node is not None else table_name
        return Select(
            columns=columns,
            table=table_field,
            where=where,
            order_by=order_by,
            limit=limit,
            offset=offset,
            group_by=group_by,
            having=having
        )

    # =========================
    # WHERE helper
    # =========================

    def _parse_binary_expression(self) -> BinaryExpression:
        left_col = self._expect(TokenType.IDENTIFIER).value
        # Handle qualified column names in WHERE clause
        if self._peek().value == ".":
            self._advance()  # consume .
            left_col = f"{left_col}.{self._expect(TokenType.IDENTIFIER).value}"
        left = Column(left_col)
        op = self._expect(TokenType.SYMBOL).value
        right_tok = self._expect(TokenType.LITERAL)
        return BinaryExpression(left, op, Literal(right_tok.value))

    # =========================
    # SHOW TABLES
    # =========================

    def _parse_show_tables(self) -> ShowTables:
        self._expect(TokenType.KEYWORD, "SHOW")
        self._expect(TokenType.KEYWORD, "TABLES")
        self._consume_optional_semicolon()
        return ShowTables()
