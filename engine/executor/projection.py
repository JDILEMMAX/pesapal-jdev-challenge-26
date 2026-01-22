# engine/executors/projection.py
from .base import Executor

class Projection(Executor):
    def __init__(self, source: Executor, columns):
        self.source = source
        # If columns contains Column("*"), we'll expand it during execution
        self.columns_ast = columns  # store AST objects, not names yet

    def _extract_output_name(self, col_name):
        """Extract the output column name, handling aliases and function calls"""
        # Handle "COUNT(*) AS count" -> "count"
        if " AS " in col_name:
            parts = col_name.split(" AS ")
            return parts[1].lower().strip()
        # Handle "COUNT(*)" -> "count(*)"
        if "(" in col_name and ")" in col_name:
            return col_name.lower()
        # Handle "u.name" -> "name" (qualified names)
        if "." in col_name:
            return col_name.split(".")[1].lower()
        # Regular column name
        return col_name.lower()

    def _extract_source_name(self, col_name):
        """Extract the source column name to fetch from row"""
        # Handle "COUNT(*) AS count" -> "count(*)" (what GroupBy computed)
        if " AS " in col_name:
            func_part = col_name.split(" AS ")[0].strip()
            if "(" in func_part:
                return func_part.lower()
            return func_part.lower()
        # Handle "COUNT(*)" -> "count(*)"
        if "(" in col_name and ")" in col_name:
            return col_name.lower()
        # Handle "u.name" -> "name"
        if "." in col_name:
            return col_name.split(".")[1].lower()
        # Regular column
        return col_name.lower()

    def execute(self):
        rows = self.source.execute()
        if not rows:
            return []

        # Determine column names
        if len(self.columns_ast) == 1 and self.columns_ast[0].name == "*":
            # Expand '*' to all columns from the first row
            columns = list(rows[0].keys())
        else:
            columns = [c.name for c in self.columns_ast]

        # Build projected rows, handling aggregate functions and aliases
        result = []
        for row in rows:
            projected_row = {}
            for col in columns:
                output_name = self._extract_output_name(col)
                source_name = self._extract_source_name(col)
                
                # Get value from row using source name
                value = row.get(source_name)
                if value is None:
                    # Try without function wrapper for regular columns
                    value = row.get(output_name)
                
                projected_row[output_name] = value
            
            result.append(projected_row)
        
        return result
