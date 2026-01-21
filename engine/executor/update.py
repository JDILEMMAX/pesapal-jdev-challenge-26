from .base import Executor


class UpdateExecutor(Executor):
    def __init__(self, engine, table_name, assignments, predicate=None):
        self.engine = engine
        self.table_name = table_name
        self.assignments = assignments
        self.predicate = predicate

    def execute(self):
        # Convert assignments: Literal → raw value
        set_values = {
            col.lower(): lit.value
            for col, lit in self.assignments.items()
        }

        where_fn = None
        if self.predicate:
            where_fn = self._build_where_fn()

        return self.engine.update_rows(
            self.table_name,
            set_values=set_values,
            where_fn=where_fn,
        )

    def _build_where_fn(self):
        left = self.predicate.left.name.lower()
        op = self.predicate.operator
        literal = self.predicate.right.value
        # Coerce literal to column dtype when possible (parser may leave numbers as strings)
        try:
            table = self.engine.catalog.get_table(self.table_name.upper())
            schema = table.schema
            schema_names = schema.column_names()
            idx_col = schema_names.index(left.upper())
            dtype = schema.columns[idx_col].dtype
            literal = dtype(literal)
        except Exception:
            # If coercion fails, fall back to raw literal
            pass

        def where(row):
            val = row[left]
            if op == "=":
                return val == literal
            elif op == "<":
                return val < literal
            elif op == ">":
                return val > literal
            elif op == "<=":
                return val <= literal
            elif op == ">=":
                return val >= literal
            elif op == "!=":
                return val != literal
            return False

        return where
