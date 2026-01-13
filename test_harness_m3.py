# test_harness_m3.py

import bisect
from engine.storage.table import Table  # Milestone 2 table
from engine.index.index_manager import IndexManager
from engine.planner import cost


def range_search(index_mgr, table, column, start_key, end_key):
    """
    Perform a range search on a single-column B+ Tree index.
    Returns all rows with start_key <= key <= end_key.
    """
    import bisect

    tree = index_mgr.indexes.get(table.name, {}).get((column,))
    if not tree:
        return []

    # Normalize start_key as tuple
    start_key_tuple = (start_key,)

    # Descend to first leaf node containing start_key
    node = tree.root
    while not node.is_leaf:
        i = bisect.bisect_left(node.keys, start_key_tuple)
        node = node.children[i]

    # Traverse leaf nodes and collect all rows in range
    results = []
    while node:
        for k, row in zip(node.keys, node.children):
            key_value = k[0] if isinstance(k, tuple) else k
            if start_key <= key_value <= end_key:
                results.append(row)
            elif key_value > end_key:
                return results
        node = node.next
    return results


def main():
    print("=== Milestone 3: Indexing & Performance Test ===")

    # Step 1: Create table
    users = Table("users", ["id", "name", "age"])
    users.insert_row({"id": 1, "name": "Alice", "age": 30})
    users.insert_row({"id": 2, "name": "Bob", "age": 25})
    users.insert_row({"id": 3, "name": "Charlie", "age": 30})
    users.insert_row({"id": 4, "name": "Diana", "age": 40})

    print(f"Table '{users.name}' rows:")
    for row in users.rows():
        print(row)

    # Step 2: Create IndexManager
    idx_mgr = IndexManager()

    # Single-column index
    idx_mgr.create_index(users, "age")
    print("\nCreated index on 'age'")

    # Composite index
    idx_mgr.create_index(users, ["age", "name"])
    print("Created composite index on ['age', 'name']")

    # Step 3: Search using single-column index
    key = 30
    results = idx_mgr.search(users, "age", key)
    print(f"\nSearch by age={key}:")
    print(results)

    # Step 4: Search using composite index
    composite_key = (30, "Charlie")
    results = idx_mgr.search(users, ["age", "name"], composite_key)
    print(f"\nSearch by age=30 AND name='Charlie':")
    print(results)

    # Step 5: Range query (age between 30 and 40)
    range_results = range_search(idx_mgr, users, "age", 30, 40)
    print("\nRange search: age between 30 and 40")
    for row in range_results:
        print(row)

    # Step 6: Compare cost
    full_scan_cost = cost.estimate_cost(users, indexed=False)
    index_scan_cost = cost.estimate_cost(users, indexed=True)
    print(f"\nEstimated full table scan cost: {full_scan_cost}")
    print(f"Estimated indexed scan cost: {index_scan_cost}")


if __name__ == "__main__":
    main()
