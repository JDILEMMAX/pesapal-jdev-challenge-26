# Project Milestones

## Overview

This project is built in distinct milestones (A through E), each adding new functionality and capabilities to the database engine.

---

## Milestone A: SQL Surface Upgrade

**Status:** COMPLETE ✓  
**Focus:** Parser and AST enhancements

### What's Implemented
- DROP TABLE syntax parsing and AST generation
- DELETE FROM ... WHERE syntax
- UPDATE ... SET ... WHERE syntax
- Extended CREATE TABLE syntax:
  - NOT NULL constraints
  - PRIMARY KEY constraints
  - AUTO_INCREMENT support
  - VARCHAR(n) for variable-length strings
- Constraints are stored in ColumnDef and Column objects
- All existing SQL functionality remains unchanged

### Example Queries
```sql
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255)
);

UPDATE users SET name = 'John' WHERE id = 1;
DELETE FROM users WHERE id > 5;
DROP TABLE users;
```

---

## Milestone B: DML & DDL Execution Semantics

**Status:** COMPLETE ✓  
**Focus:** Executing DELETE, UPDATE, and DROP operations

### What's Implemented
- `Engine.delete_rows(table, predicate)` — DELETE execution
- `Engine.update_rows(table, assignments, predicate)` — UPDATE execution
- `Engine.drop_table(table)` — DROP TABLE execution
- Predicate evaluation reuses WHERE logic
- Storage, catalog, and persistence consistency maintained
- SELECT and INSERT continue working unchanged

### Key Features
- Rows matching predicate are removed/updated correctly
- Table schema is completely removed on DROP
- All data is cleaned up from storage
- Concurrent transactions are handled safely

---

## Milestone C: Column Constraints Enforcement

**Status:** COMPLETE ✓  
**Focus:** Enforcing NOT NULL and PRIMARY KEY constraints

### What's Implemented
- Column class stores constraint metadata
  - primary_key: boolean flag
  - auto_increment: boolean flag
  - constraints: list of constraint definitions
- NOT NULL enforcement in `Engine.insert_row()` with explicit error messages
- PRIMARY KEY uniqueness checked at insert time
- Auto-increment values generated automatically
- Existing tables load correctly with constraint metadata
- Errors are deterministic and explicit (no silent coercion)

### Constraint Behavior
```sql
-- This will fail with NOT NULL violation
INSERT INTO users (name) VALUES (NULL);

-- This will fail with PRIMARY KEY violation
INSERT INTO users (id, name) VALUES (1, 'John');
INSERT INTO users (id, name) VALUES (1, 'Jane'); -- Error: duplicate key

-- This will auto-generate ID
INSERT INTO users (name) VALUES ('John'); -- id is auto-incremented
```

---

## Milestone D: JOIN Support (Phase D1 - Read-Only INNER JOIN)

**Status:** COMPLETE ✓  
**Focus:** INNER JOIN queries for SELECT operations

### What's Implemented
- INNER JOIN parsing with ON column = column syntax
- Equi-join support (joining on column equality)
- SELECT-only INNER JOIN (no UPDATE/DELETE with JOINs)
- Nested-loop join executor (correctness-focused)
- No impact on non-JOIN queries
- Existing SELECT queries work unchanged

### Supported Queries
```sql
-- INNER JOIN two tables
SELECT users.name, orders.amount 
FROM users 
INNER JOIN orders ON users.id = orders.user_id;

-- With WHERE clause
SELECT * FROM users 
INNER JOIN orders ON users.id = orders.user_id 
WHERE orders.amount > 100;

-- Multiple columns in result
SELECT users.id, users.name, orders.id, orders.amount
FROM users INNER JOIN orders ON users.id = orders.user_id;
```

### Limitations
- Only INNER JOIN supported (no LEFT, RIGHT, FULL)
- Single join condition only (single ON clause)
- No UPDATE or DELETE with JOINs
- Cartesian product not supported yet

---

## Milestone E: Query Shaping

**Status:** COMPLETE ✓  
**Focus:** Sorting, pagination, and aggregation

### What's Implemented
- **ORDER BY:** column [ASC|DESC] for result sorting
- **LIMIT:** n to restrict result set size
- **OFFSET:** m to skip first m rows
- **GROUP BY:** columns for grouping results
- **COUNT(*):** aggregate function for row counting
- **HAVING:** condition for filtering groups
- Modifiers compose correctly with each other
- Queries without modifiers behave unchanged

### Supported Queries
```sql
-- Order by with direction
SELECT * FROM users ORDER BY name ASC;
SELECT * FROM orders ORDER BY amount DESC;

-- Pagination
SELECT * FROM users LIMIT 10;
SELECT * FROM users LIMIT 10 OFFSET 20;

-- Aggregation
SELECT COUNT(*) FROM users;
SELECT user_id, COUNT(*) FROM orders GROUP BY user_id;

-- Aggregation with filtering
SELECT user_id, COUNT(*) as order_count 
FROM orders 
GROUP BY user_id 
HAVING COUNT(*) > 5;

-- Combined
SELECT user_id, COUNT(*) 
FROM orders 
GROUP BY user_id 
HAVING COUNT(*) > 2
ORDER BY COUNT(*) DESC
LIMIT 5;
```

---

## Feature Dependency Chain

```
Milestone A (Parser)
    ↓
Milestone B (Execution)
    ↓
Milestone C (Constraints)
    ↓
Milestone D (JOINs)
    ↓
Milestone E (Query Shaping)
```

Each milestone builds on the previous one, adding new capabilities while maintaining backward compatibility.

---

## Testing

All milestones have comprehensive test coverage in `tests/unit/test_milestones.py`:

- `test_milestone_a_sql_surface()` — Parser and AST tests
- `test_milestone_b_dml_ddl_execution()` — Execution logic tests
- `test_milestone_c_constraints()` — Constraint validation tests
- `test_milestone_e_query_shaping()` — Sorting, grouping, aggregation tests
- `test_comprehensive_scenario()` — All features combined end-to-end test

Run all tests:
```bash
python -B tests/run_all_tests.py
```

Run milestone tests only:
```bash
python -B tests/unit/test_milestones.py
```

---

## See Also

- [README.md](../../README.md) — Project overview
- [docs/tests/reference.md](../tests/reference.md) — Testing guide
- [docs/architecture/overview.md](../architecture/overview.md) — System architecture
