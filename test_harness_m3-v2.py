# test_harness_m3.py
"""
Milestone 3 Test Harness: Indexing & Performance
Demonstrates:
- Single-column B+ Tree index search
- Composite B+ Tree index search
- Single-column range search
- Composite range search
"""

import bisect
from engine.storage.table import Table
from engine.index.index_manager import IndexManager
from engine.planner import cost


def range_search(index_mgr, table, column, start_key, end_key):
    """Single-column range search using B+ Tree linked leaves."""
    tree = index_mgr.indexes.get(table.name, {}).get((column,))
    if not tree:
        return []

    start_key_tuple = (start_key,)
    node = tree.root
    while not node.is_leaf:
        i = bisect.bisect_left(node.keys, start_key_tuple)
        node = node.children[i]

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


def composite_range_search(index_mgr, table, columns, start_key, end_key):
    """Composite range search on a B+ Tree index."""
    tree = index_mgr.indexes.get(table.name, {}).get(tuple(columns))
    if not tree:
        return []

    start_key = tuple(start_key)
    end_key = tuple(end_key)
    node = tree.root
    while not node.is_leaf:
        i = bisect.bisect_left(node.keys, start_key)
        node = node.children[i]

    results = []
    while node:
        for k, row in zip(node.keys, node.children):
            if start_key <= k <= end_key:
                results.append(row)
            elif k > end_key:
                return results
        node = node.next
    return results


def main():
    print("=== Milestone 3: Indexing & Performance Test ===")

    # Step 1: Create table and insert rows
    users = Table("users", ["id", "name", "age"])
    users.insert_row({"id": 1, "name": "Alice", "age": 30})
    users.insert_row({"id": 2, "name": "Bob", "age": 25})
    users.insert_row({"id": 3, "name": "Charlie", "age": 30})
    users.insert_row({"id": 4, "name": "Diana", "age": 40})

    print(f"\nTable '{users.name}' rows:")
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

    # Step 3: Search by single-column index
    results = idx_mgr.search(users, "age", 30)
    print("\nSearch by age=30:")
    print(results)

    # Step 4: Search by composite index
    results = idx_mgr.search(users, ["age", "name"], (30, "Charlie"))
    print("\nSearch by age=30 AND name='Charlie':")
    print(results)

    # Step 5: Single-column range search
    results = range_search(idx_mgr, users, "age", 30, 40)
    print("\nRange search: age between 30 and 40")
    for r in results:
        print(r)

    # Step 6: Composite range search
    results = composite_range_search(idx_mgr, users, ["age", "name"], (30, "A"), (30, "C"))
    print("\nComposite range search: age=30 AND name between A-C")
    for r in results:
        print(r)

    # Step 7: Cost estimates
    full_scan_cost = cost.estimate_cost(users, indexed=False)
    index_scan_cost = cost.estimate_cost(users, indexed=True)
    print(f"\nEstimated full table scan cost: {full_scan_cost}")
    print(f"Estimated indexed scan cost: {index_scan_cost}")


if __name__ == "__main__":
    main()
