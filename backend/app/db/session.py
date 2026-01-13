# app/db/session.py
from .connection import get_engine
from engine.exceptions import EngineError


class Session:
    def __init__(self):
        self.engine = get_engine()

    def execute(self, sql: str):
        """
        Execute a minimal subset of SQL against the StorageEngine.

        Supported:
        - CREATE TABLE table (col1, col2, ...)
        - INSERT INTO table VALUES (v1, v2, ...)
        - SELECT * FROM table
        """

        if not sql or not sql.strip():
            raise ValueError("Empty SQL statement")

        # --- Normalize SQL ---
        sql = sql.strip().rstrip(";")
        tokens = sql.split()
        command = tokens[0].upper()

        try:
            if command == "CREATE":
                # CREATE TABLE table_name (col1, col2)
                table_name = tokens[2]

                columns = (
                    sql.split("(", 1)[1]
                    .rsplit(")", 1)[0]
                    .replace(" ", "")
                    .split(",")
                )

                self.engine.create_table(table_name, columns)
                return {"status": "OK"}

            elif command == "INSERT":
                # INSERT INTO table_name VALUES (v1, v2)
                table_name = tokens[2]

                values_str = (
                    sql.split("VALUES", 1)[1]
                    .strip()
                    .lstrip("(")
                    .rstrip(")")
                )

                # NOTE: eval is acceptable here for milestone scope,
                # but should be replaced later with a real parser.
                values = [eval(v) for v in values_str.split(",")]

                self.engine.insert_row(table_name, values)
                return {"status": "OK"}

            elif command == "SELECT":
                # SELECT * FROM table_name
                table_name = tokens[3]
                return self.engine.get_rows(table_name)

            else:
                raise ValueError(f"Unsupported SQL command: {command}")

        except EngineError:
            # Re-raise engine errors unchanged (clean separation)
            raise

        except Exception as e:
            # Wrap unexpected issues as execution errors
            raise RuntimeError(f"SQL execution failed: {e}") from e


def get_session():
    """Factory function expected by Django views"""
    return Session()
