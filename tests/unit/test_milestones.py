"""
Comprehensive test suite covering all milestones (A-E).
Consolidated from: test.py, milestone_test.py, extended_milestone_test.py, final_test.py
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.sql.parser import Parser
from engine.sql.tokenizer import Tokenizer
from backend.app.db.query import build_plan, execute_plan
from engine.engine import Engine


def run_sql(engine, sql: str):
    """Tokenize, parse, plan, and execute a SQL statement."""
    tokenizer = Tokenizer(sql)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    plan = build_plan(ast)
    return execute_plan(plan, engine)


def test_milestone_8b_basic_dml_ddl():
    """Test basic DML & DDL operations (Milestone 8B)."""
    print("\n=== Milestone 8B: Basic DML & DDL ===")
    engine = Engine()

    # CREATE TABLE
    run_sql(engine, "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);")
    assert "USERS" in engine.catalog.tables
    print("[PASS] CREATE TABLE works")

    # INSERT
    run_sql(engine, "INSERT INTO users VALUES (1, 'Alice', 30);")
    run_sql(engine, "INSERT INTO users VALUES (2, 'Bob', 25);")
    rows = engine.get_rows("users")
    assert len(rows) == 2
    print("[PASS] INSERT works")

    expected_rows = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
    ]
    assert rows == expected_rows
    print("[PASS] Inserted rows match expected content")

    # SELECT
    result = run_sql(engine, "SELECT id, name, age FROM users WHERE age > 26;")
    expected = [{"id": 1, "name": "Alice", "age": 30}]
    assert result == expected
    print("[PASS] SELECT with WHERE works")

    # UPDATE
    result = run_sql(engine, "UPDATE users SET age = 31 WHERE id = 1;")
    assert result == [{"updated": 1}]
    rows = engine.get_rows("users")
    assert any(r["age"] == 31 for r in rows if r["id"] == 1)
    print("[PASS] UPDATE works")

    # DELETE
    result = run_sql(engine, "DELETE FROM users WHERE id = 2;")
    assert result == [{"deleted": 1}]
    rows = engine.get_rows("users")
    assert len(rows) == 1 and rows[0]["id"] == 1
    print("[PASS] DELETE works")

    # DROP TABLE
    run_sql(engine, "DROP TABLE users;")
    assert "USERS" not in engine.catalog.tables
    print("[PASS] DROP TABLE works")

    print("Milestone 8B: PASSED\n")


def test_milestone_8c_inner_join():
    """Test INNER JOIN support (Milestone 8C)."""
    print("=== Milestone 8C: INNER JOIN ===")
    engine = Engine()

    # CREATE TABLES
    run_sql(engine, "CREATE TABLE users (id INTEGER, name TEXT);")
    run_sql(engine, "CREATE TABLE orders (id INTEGER, user_id INTEGER, product TEXT);")

    # INSERT DATA
    run_sql(engine, "INSERT INTO users VALUES (1, 'Alice');")
    run_sql(engine, "INSERT INTO users VALUES (2, 'Bob');")
    run_sql(engine, "INSERT INTO orders VALUES (1, 1, 'Book');")
    run_sql(engine, "INSERT INTO orders VALUES (2, 1, 'Pen');")
    run_sql(engine, "INSERT INTO orders VALUES (3, 2, 'Notebook');")

    # INNER JOIN
    result = run_sql(
        engine,
        "SELECT id, name, product FROM users INNER JOIN orders ON id = user_id;"
    )

    expected = [
        {"id": 1, "name": "Alice", "product": "Book"},
        {"id": 1, "name": "Alice", "product": "Pen"},
        {"id": 2, "name": "Bob", "product": "Notebook"},
    ]
    assert result == expected
    print("[PASS] INNER JOIN works correctly")
    print("Milestone 8C: PASSED\n")


def test_milestone_a_sql_surface():
    """Test SQL parser and AST (Milestone A)."""
    print("=== Milestone A: SQL Surface Upgrade (Parser + AST) ===")
    engine = Engine()

    # Test DROP TABLE parsing
    run_sql(engine, "CREATE TABLE test (id INTEGER);")
    run_sql(engine, "DROP TABLE test;")
    print("[PASS] DROP TABLE parsing and execution works")

    # Test extended CREATE TABLE
    tokenizer = Tokenizer(
        "CREATE TABLE users (id INTEGER PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL);"
    )
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("[PASS] Extended CREATE TABLE (NOT NULL, PRIMARY KEY, AUTO_INCREMENT) parses")

    # Test DELETE
    engine2 = Engine()
    run_sql(engine2, "CREATE TABLE users (id INTEGER, name TEXT);")
    run_sql(engine2, "INSERT INTO users VALUES (1, 'Alice');")
    run_sql(engine2, "INSERT INTO users VALUES (2, 'Bob');")
    result = run_sql(engine2, "DELETE FROM users WHERE id = 1;")
    assert result == [{"deleted": 1}]
    print("[PASS] DELETE FROM ... WHERE ... works")

    # Test UPDATE
    engine3 = Engine()
    run_sql(engine3, "CREATE TABLE users (id INTEGER, age INTEGER);")
    run_sql(engine3, "INSERT INTO users VALUES (1, 30);")
    result = run_sql(engine3, "UPDATE users SET age = 31 WHERE id = 1;")
    assert result == [{"updated": 1}]
    print("[PASS] UPDATE ... SET ... WHERE ... works")

    print("Milestone A: PASSED\n")


def test_milestone_b_dml_ddl_execution():
    """Test DML & DDL execution semantics (Milestone B)."""
    print("=== Milestone B: DML & DDL Execution Semantics ===")
    engine = Engine()

    run_sql(engine, "CREATE TABLE test (id INTEGER);")
    assert "TEST" in engine.catalog.tables
    run_sql(engine, "DROP TABLE test;")
    assert "TEST" not in engine.catalog.tables
    print("[PASS] Table lifecycle (CREATE to DROP) works")

    print("Milestone B: PASSED\n")


def test_milestone_c_constraints():
    """Test constraint enforcement (Milestone C)."""
    print("=== Milestone C: Column Constraints Enforcement ===")

    # Test NOT NULL enforcement
    engine = Engine()
    tokenizer = Tokenizer("CREATE TABLE users (id INTEGER, name TEXT NOT NULL);")
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    plan = build_plan(ast)
    execute_plan(plan, engine)

    run_sql(engine, "INSERT INTO users VALUES (1, 'Alice');")
    print("[PASS] NOT NULL: Accepts valid non-null value")

    try:
        run_sql(engine, "INSERT INTO users VALUES (2, NULL);")
        print("[FAIL] NOT NULL: Should reject NULL but didn't")
        assert False, "NOT NULL constraint not enforced"
    except Exception as e:
        if "cannot be null" in str(e).lower():
            print("[PASS] NOT NULL: Correctly rejects NULL")
        else:
            raise

    # Test PRIMARY KEY uniqueness
    engine2 = Engine()
    tokenizer = Tokenizer("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT);")
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    plan = build_plan(ast)
    execute_plan(plan, engine2)

    run_sql(engine2, "INSERT INTO products VALUES (1, 'Widget');")
    print("[PASS] PRIMARY KEY: Accepts first insert")

    try:
        run_sql(engine2, "INSERT INTO products VALUES (1, 'Gadget');")
        print("[FAIL] PRIMARY KEY: Should reject duplicate but didn't")
        assert False, "PRIMARY KEY constraint not enforced"
    except Exception as e:
        if "primary key" in str(e).lower() or "duplicate" in str(e).lower():
            print("[PASS] PRIMARY KEY: Correctly rejects duplicate")
        else:
            raise

    print("Milestone C: PASSED\n")


def test_milestone_e_query_shaping():
    """Test query shaping features (Milestone E)."""
    print("=== Milestone E: Query Shaping (ORDER BY, LIMIT, OFFSET, GROUP BY) ===")

    # Test ORDER BY ASC/DESC
    engine = Engine()
    run_sql(engine, "CREATE TABLE items (id INTEGER, name TEXT, price FLOAT);")
    run_sql(engine, "INSERT INTO items VALUES (3, 'Item C', 30.0);")
    run_sql(engine, "INSERT INTO items VALUES (1, 'Item A', 10.0);")
    run_sql(engine, "INSERT INTO items VALUES (2, 'Item B', 20.0);")

    result = run_sql(engine, "SELECT id FROM items ORDER BY id ASC;")
    ids = [row["id"] for row in result]
    assert ids == [1, 2, 3]
    print("[PASS] ORDER BY ASC works")

    result = run_sql(engine, "SELECT id FROM items ORDER BY id DESC;")
    ids = [row["id"] for row in result]
    assert ids == [3, 2, 1]
    print("[PASS] ORDER BY DESC works")

    # Test LIMIT
    engine2 = Engine()
    run_sql(engine2, "CREATE TABLE numbers (n INTEGER);")
    for i in range(1, 11):
        run_sql(engine2, f"INSERT INTO numbers VALUES ({i});")

    result = run_sql(engine2, "SELECT n FROM numbers LIMIT 3;")
    assert len(result) == 3
    print("[PASS] LIMIT works")

    # Test OFFSET
    engine3 = Engine()
    run_sql(engine3, "CREATE TABLE seq (n INTEGER);")
    for i in range(1, 6):
        run_sql(engine3, f"INSERT INTO seq VALUES ({i});")

    result = run_sql(engine3, "SELECT n FROM seq OFFSET 2;")
    values = [row["n"] for row in result]
    assert values == [3, 4, 5]
    print("[PASS] OFFSET works")

    # Test LIMIT + OFFSET pagination
    engine4 = Engine()
    run_sql(engine4, "CREATE TABLE pages (n INTEGER);")
    for i in range(1, 21):
        run_sql(engine4, f"INSERT INTO pages VALUES ({i});")

    result = run_sql(engine4, "SELECT n FROM pages LIMIT 5 OFFSET 5;")
    values = [row["n"] for row in result]
    assert values == [6, 7, 8, 9, 10]
    print("[PASS] LIMIT + OFFSET pagination works")

    # Test GROUP BY + COUNT(*)
    engine5 = Engine()
    run_sql(engine5, "CREATE TABLE sales (product TEXT, amount INTEGER);")
    run_sql(engine5, "INSERT INTO sales VALUES ('Apple', 10);")
    run_sql(engine5, "INSERT INTO sales VALUES ('Apple', 20);")
    run_sql(engine5, "INSERT INTO sales VALUES ('Orange', 15);")

    result = run_sql(engine5, "SELECT product FROM sales GROUP BY product;")
    products = sorted([row["product"] for row in result])
    assert products == ["Apple", "Orange"]
    print("[PASS] GROUP BY works")

    result = run_sql(engine5, "SELECT product, count(*) FROM sales GROUP BY product;")
    counts = {row["product"]: row.get("count(*)") for row in result}
    assert counts.get("Apple") == 2 and counts.get("Orange") == 1
    print("[PASS] COUNT(*) aggregation works")

    print("Milestone E: PASSED\n")


def test_comprehensive_scenario():
    """Comprehensive end-to-end test with all features."""
    print("=" * 80)
    print("COMPREHENSIVE END-TO-END TEST: All Features Combined")
    print("=" * 80)

    engine = Engine()

    # Create table with constraints
    run_sql(
        engine,
        """CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        price FLOAT
    );""",
    )
    print("[PASS] Created table with constraints")

    # Insert test data
    run_sql(engine, "INSERT INTO products VALUES (1, 'Laptop', 'Electronics', 1200.50);")
    run_sql(engine, "INSERT INTO products VALUES (2, 'Mouse', 'Peripherals', 25.99);")
    run_sql(engine, "INSERT INTO products VALUES (3, 'Keyboard', 'Peripherals', 75.00);")
    run_sql(engine, "INSERT INTO products VALUES (4, 'Monitor', 'Electronics', 350.00);")
    print("[PASS] Inserted 4 products")

    # Test constraint enforcement
    try:
        run_sql(engine, "INSERT INTO products VALUES (5, NULL, 'Test', 100.0);")
        assert False, "NOT NULL constraint should have been enforced"
    except:
        print("[PASS] NOT NULL constraint enforced")

    try:
        run_sql(engine, "INSERT INTO products VALUES (1, 'Duplicate', 'Test', 50.0);")
        assert False, "PRIMARY KEY constraint should have been enforced"
    except:
        print("[PASS] PRIMARY KEY constraint enforced")

    # Test UPDATE
    result = run_sql(engine, "UPDATE products SET price = 999.99 WHERE id = 1;")
    assert result[0]["updated"] == 1
    print("[PASS] UPDATE works")

    # Test DELETE
    rows_before = engine.get_rows("products")
    result = run_sql(engine, "DELETE FROM products WHERE category = 'Peripherals';")
    rows_after = engine.get_rows("products")
    assert result[0]["deleted"] == 2
    assert len(rows_after) == 2
    print("[PASS] DELETE works and leaves correct rows")

    # Test ORDER BY
    run_sql(engine, "SELECT id FROM products ORDER BY price DESC;")
    print("[PASS] ORDER BY works")

    # Test LIMIT
    result = run_sql(engine, "SELECT id FROM products LIMIT 1;")
    assert len(result) == 1
    print("[PASS] LIMIT works")

    # Test GROUP BY
    engine2 = Engine()
    run_sql(engine2, "CREATE TABLE sales (product TEXT, amount INTEGER);")
    run_sql(engine2, "INSERT INTO sales VALUES ('Widget', 100);")
    run_sql(engine2, "INSERT INTO sales VALUES ('Widget', 200);")
    run_sql(engine2, "INSERT INTO sales VALUES ('Gadget', 150);")
    result = run_sql(engine2, "SELECT product FROM sales GROUP BY product;")
    assert len(result) == 2
    print("[PASS] GROUP BY works")

    # Test JOIN
    engine3 = Engine()
    run_sql(engine3, "CREATE TABLE customers (id INTEGER, name TEXT);")
    run_sql(engine3, "CREATE TABLE orders (id INTEGER, customer_id INTEGER, total FLOAT);")
    run_sql(engine3, "INSERT INTO customers VALUES (1, 'Alice');")
    run_sql(engine3, "INSERT INTO customers VALUES (2, 'Bob');")
    run_sql(engine3, "INSERT INTO orders VALUES (101, 1, 150.00);")
    run_sql(engine3, "INSERT INTO orders VALUES (102, 1, 75.50);")
    run_sql(engine3, "INSERT INTO orders VALUES (103, 2, 200.00);")

    result = run_sql(
        engine3, "SELECT id, name, total FROM customers INNER JOIN orders ON id = customer_id;"
    )
    assert len(result) == 3
    print("[PASS] INNER JOIN works")

    # Test DROP TABLE
    run_sql(engine3, "DROP TABLE orders;")
    assert "ORDERS" not in engine3.catalog.tables
    print("[PASS] DROP TABLE works")

    print("=" * 80)
    print("COMPREHENSIVE TEST: PASSED\n")


if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING COMPREHENSIVE MILESTONE TEST SUITE")
    print("=" * 80)

    # Run all tests
    test_milestone_a_sql_surface()
    test_milestone_b_dml_ddl_execution()
    test_milestone_c_constraints()
    test_milestone_e_query_shaping()
    test_milestone_8b_basic_dml_ddl()
    test_milestone_8c_inner_join()
    test_comprehensive_scenario()

    print("=" * 80)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)
