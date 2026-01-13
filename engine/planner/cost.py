# engine/planner/cost.py


def estimate_cost(table, indexed=False):
    """
    Simple cost estimator:
    - Full table scan: cost proportional to number of rows
    - Indexed scan: fixed small cost for B+ Tree lookup (logarithmic ignored for simplicity)
    """
    if indexed:
        return 1  # Assume constant time for indexed lookup
    else:
        return len(table.rows())
