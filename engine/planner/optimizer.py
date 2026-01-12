from .logical import *

class Optimizer:
    """Minimal rule-based optimizer (currently only predicate pushdown)"""
    @staticmethod
    def optimize(plan: LogicalPlanNode) -> LogicalPlanNode:
        # Push filter below projection if possible
        if isinstance(plan, LogicalProjection) and isinstance(plan.source, LogicalFilter):
            filter_node = plan.source
            plan.source = filter_node.source
            filter_node.source = plan
            return filter_node
        return plan
