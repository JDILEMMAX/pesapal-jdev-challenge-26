from .base import Executor
from engine.sql.ast import BinaryExpression

class Filter(Executor):
    def __init__(self, source: Executor, predicate: BinaryExpression):
        self.source = source
        self.predicate = predicate

    def execute(self):
        rows = self.source.execute()
        col = self.predicate.left.name
        op = self.predicate.operator
        val = self.predicate.right.value
        result = []
        for row in rows:
            if op == "=" and row[col] == val:
                result.append(row)
            elif op == "<" and row[col] < val:
                result.append(row)
            elif op == ">" and row[col] > val:
                result.append(row)
        return result
