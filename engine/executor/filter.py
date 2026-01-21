from .base import Executor
from engine.sql.ast import BinaryExpression


class Filter(Executor):
    def __init__(self, source: Executor, predicate: BinaryExpression):
        self.source = source
        self.predicate = predicate

    def execute(self):
        rows = self.source.execute()
        col_name = self.predicate.left.name
        op = self.predicate.operator
        literal = self.predicate.right.value
        result = []

        table = self.source.table  # now works

        for row in rows:
            if self._compare(row, col_name, op, literal, table):
                result.append(row)

        return result

    def _compare(self, row, col_name, op, literal, table):
        col_name_lc = col_name.lower()

        # Find the column schema (catalog is uppercase-safe)
        column_schema = next(
            (c for c in table.schema.columns if c.name.upper() == col_name.upper()), None
        )
        if column_schema is None:
            raise ValueError(f"Column {col_name} does not exist in table {table.name}")

        # Coerce literal to correct type
        literal_value = column_schema.dtype(literal)
        row_value = row[col_name_lc]

        # Perform comparison
        if op == "=":
            return row_value == literal_value
        elif op == "<":
            return row_value < literal_value
        elif op == ">":
            return row_value > literal_value
        elif op == "<=":
            return row_value <= literal_value
        elif op == ">=":
            return row_value >= literal_value
        elif op == "!=":
            return row_value != literal_value
        else:
            raise ValueError(f"Unsupported operator: {op}")
