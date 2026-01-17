# app/db/session.py
from .connection import get_engine
from engine.exceptions import EngineError
from engine.sql.tokenizer import Tokenizer
from engine.sql.parser import Parser
from .query import build_plan, execute_plan
from engine.sql.ast import ShowTables


class Session:
    def __init__(self):
        self.engine = get_engine()

    def execute(self, sql: str):
        """
        Execute SQL using the real parser + executor.

        Supports:
        - CREATE TABLE with column types
        - INSERT INTO
        - SELECT with optional columns & WHERE
        - SHOW TABLES
        """

        if not sql or not sql.strip():
            raise ValueError("Empty SQL statement")

        sql = sql.strip()
        missing_semicolon = not sql.endswith(";")

        try:
            tokenizer = Tokenizer(sql)
            tokens = tokenizer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            # Execute
            if isinstance(ast, ShowTables):
                data = [
                    {"table_name": name}
                    for name in self.engine.catalog.list_tables()
                ]
            else:
                plan = build_plan(ast)
                data = execute_plan(plan, self.engine)

            # Always normalize here
            result = {"data": data}

            # Include warning if semicolon was missing
            if missing_semicolon:
                result["warning"] = "Consider ending your SQL with a semicolon (;)"

            return result

        except EngineError:
            raise
        except Exception as e:
            raise RuntimeError(f"SQL execution failed: {e}") from e

def get_session():
    """Factory for Django views"""
    return Session()
