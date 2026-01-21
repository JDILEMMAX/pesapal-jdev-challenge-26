from .base import Executor
from collections import defaultdict


class GroupBy(Executor):
    def __init__(self, source: Executor, group_by_columns, having=None):
        self.source = source
        self.group_by_columns = group_by_columns  # List of Column objects
        self.having = having  # Optional BinaryExpression for filtering post-aggregation

    def execute(self):
        rows = self.source.execute()
        if not rows:
            return rows

        # Group by specified columns
        groups = defaultdict(list)
        for row in rows:
            # Build group key from specified columns
            key_parts = []
            for col in self.group_by_columns:
                col_name = col.name.lower()
                key_parts.append(str(row.get(col_name)))
            group_key = tuple(key_parts)
            groups[group_key].append(row)

        # Aggregate each group
        result = []
        for group_key, group_rows in groups.items():
            # Create aggregated row: include grouping columns + counts
            agg_row = {}
            
            # Add grouping column values
            for i, col in enumerate(self.group_by_columns):
                col_name = col.name.lower()
                agg_row[col_name] = group_rows[0].get(col_name)
            
            # Add count aggregate
            agg_row["count(*)"] = len(group_rows)
            
            # TODO: Support other aggregates (SUM, AVG, MIN, MAX) when needed
            
            result.append(agg_row)

        return result
