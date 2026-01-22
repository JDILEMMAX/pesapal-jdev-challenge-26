# Testing Guide: Complete System Functionality

This guide provides step-by-step instructions for testing all system functionalities, including setup, execution, and verification of expected behavior.

---

## Table of Contents

1. [Setup](#setup)
2. [Understanding the Test Suite](#understanding-the-test-suite)
3. [Running Tests](#running-tests)
4. [Testing Milestones](#testing-milestones)
5. [Testing Core Engine](#testing-core-engine)
6. [Integration Testing](#integration-testing)
7. [Troubleshooting](#troubleshooting)

---

## Setup

### Prerequisites

- Python 3.13+
- pip (Python package manager)
- Windows/Linux/macOS

### 1. Install Python Dependencies

```bash
cd "c:\Users\KAMIKAZE\Desktop\JDEV Challenge"
pip install django  # For backend
npm install         # For frontend (optional)
```

### 2. Verify Installation

```bash
python --version      # Should be 3.13+
pip list              # Should show installed packages
```

---

## Understanding the Test Suite

The project contains comprehensive tests organized in the `tests/` directory:

```
tests/
├── run_all_tests.py                  # Centralized test runner
├── unit/
│   ├── test_milestones.py            # Consolidated milestone tests (40+ assertions)
│   ├── test_m1_storage.py            # Storage engine tests
│   ├── test_m1_storage_v2.py         # Multi-row storage tests
│   ├── test_m2_sql_pipeline.py       # SQL pipeline tests
│   ├── test_m3_indexing.py           # Indexing tests
│   ├── test_m3_indexing_v2.py        # Advanced indexing
│   └── test_m4_transactions.py       # Transaction tests
└── integration/
    ├── test_queries_linear.py        # API integration tests
    └── test_queries_modular.py       # Modular API tests
```

### Test Coverage by Milestone

| Milestone | Feature | Test File | Status |
|-----------|---------|-----------|--------|
| A | SQL Parser & AST | test_milestones.py | ✓ PASS |
| B | DML/DDL Execution | test_milestones.py | ✓ PASS |
| C | Constraint Enforcement | test_milestones.py | ✓ PASS |
| D | Qualified Names & Aliases | test_milestones.py | ✓ PASS |
| E | Query Shaping | test_milestones.py | ✓ PASS |
| Storage | File Management | test_m1_storage.py | ✓ PASS |
| Indexing | B-tree Indexes | test_m3_indexing.py | ✓ PASS |
| Transactions | MVCC, Locks | test_m4_transactions.py | ✓ PASS |

---

## Running Tests

### Option 1: Run All Tests (Recommended)

```bash
cd "c:\Users\KAMIKAZE\Desktop\JDEV Challenge"
python tests/run_all_tests.py
```

**Expected Output:**
```
================================================================================
TEST SUMMARY
================================================================================
[PASS]: unit/test_milestones.py
[PASS]: unit/test_m1_storage.py
[PASS]: unit/test_m1_storage_v2.py
[PASS]: unit/test_m2_sql_pipeline.py
[PASS]: unit/test_m3_indexing.py
[PASS]: unit/test_m4_transactions.py

Results: 6 passed, 0 failed, 0 skipped
================================================================================
```

**Execution Time:** ~40 seconds

### Option 2: Run Specific Test Suite

Run a single test module to focus on specific functionality:

#### Milestone Tests (Recommended First)
```bash
python tests/unit/test_milestones.py
```

**Coverage:** All major milestones (A, B, C, E, 8B, 8C)  
**Time:** ~5 seconds  
**Key Tests:**
- SQL parsing and execution
- Constraint enforcement (NOT NULL, PRIMARY KEY)
- Query shaping (ORDER BY, LIMIT, OFFSET, GROUP BY)
- INNER JOIN support

#### Storage Engine Tests
```bash
python tests/unit/test_m1_storage.py
```

**Coverage:** Core storage functionality  
**Time:** <1 second  
**Key Tests:**
- File manager operations
- Page management
- Record encoding/decoding

#### SQL Pipeline Tests
```bash
python tests/unit/test_m2_sql_pipeline.py
```

**Coverage:** Complete SQL execution pipeline  
**Time:** ~1 second  
**Key Tests:**
- CREATE TABLE
- INSERT operations
- SELECT with WHERE clauses

#### Indexing Tests
```bash
python tests/unit/test_m3_indexing.py
```

**Coverage:** B-tree indexing and query optimization  
**Time:** <1 second  
**Key Tests:**
- Index creation and lookups
- Range searches
- Cost estimation

#### Transaction Tests
```bash
python tests/unit/test_m4_transactions.py
```

**Coverage:** Transaction management and concurrency  
**Time:** ~30 seconds  
**Key Tests:**
- Transaction commits
- Multi-reader concurrency
- MVCC consistency

---

## Testing Milestones

### Milestone A: SQL Surface Upgrade (Parser + AST)

**What to test:** SQL parser capabilities

**Execute:**
```bash
python tests/unit/test_milestones.py
```

**Verify in output:**
```
=== Milestone A: SQL Surface Upgrade (Parser + AST) ===
[PASS] DROP TABLE parsing and execution works
[PASS] Extended CREATE TABLE (NOT NULL, PRIMARY KEY, AUTO_INCREMENT) parses
[PASS] DELETE FROM ... WHERE ... works
[PASS] UPDATE ... SET ... WHERE ... works
Milestone A: PASSED
```

**What's tested:**
- ✓ CREATE TABLE with constraints
- ✓ DROP TABLE
- ✓ DELETE with WHERE clauses
- ✓ UPDATE with SET and WHERE

---

### Milestone B: DML & DDL Execution

**What to test:** Data manipulation and definition

**Verify in output:**
```
=== Milestone B: DML & DDL Execution Semantics ===
[PASS] Table lifecycle (CREATE to DROP) works
Milestone B: PASSED
```

**What's tested:**
- ✓ Table creation
- ✓ Table deletion
- ✓ Row lifecycle

---

### Milestone C: Constraint Enforcement

**What to test:** Data integrity constraints

**Verify in output:**
```
=== Milestone C: Column Constraints Enforcement ===
[PASS] NOT NULL: Accepts valid non-null value
[PASS] NOT NULL: Correctly rejects NULL
[PASS] PRIMARY KEY: Accepts first insert
[PASS] PRIMARY KEY: Correctly rejects duplicate
Milestone C: PASSED
```

**What's tested:**
- ✓ NOT NULL constraint validation
- ✓ PRIMARY KEY uniqueness checking
- ✓ Constraint violation error handling

---

### Milestone D: Qualified Column Names & Table Aliases

**What to test:** Support for qualified column references and table aliases in SQL queries

**Execute:**
```bash
python tests/unit/test_milestones.py
```

**Verify in output:**
```
=== Milestone D: Qualified Column Names & Table Aliases ===
[PASS] COUNT(*) with alias works
[PASS] Qualified column names with table aliases in JOIN works
[PASS] Qualified columns in SELECT with JOIN works
Milestone D: PASSED
```

**What's tested:**
- ✓ Aggregate functions with aliases: `COUNT(*) AS count`
- ✓ Qualified column names in SELECT: `u.name, o.product`
- ✓ Table aliases in FROM/JOIN clauses: `FROM users u`
- ✓ Qualified column names in JOIN ON predicates: `ON u.id = o.user_id`
- ✓ Qualified columns in multiple SELECT statements
- ✓ GROUP BY with unqualified column names

**Example Query:**
```sql
SELECT id, name, COUNT(*) as count
FROM users
WHERE id > 0
GROUP BY id, name
ORDER BY count DESC
LIMIT 10;
```

**Example Query with JOIN:**
```sql
SELECT u.name, o.product
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

**How it works:**
- Tokenizer recognizes "." as a valid symbol for qualified names
- Parser handles qualified names across all SQL clauses
- Executors properly map qualified references to actual column data
- Function aliases (e.g., `COUNT(*) AS count`) are correctly parsed and output

---

### Milestone E: Query Shaping

**What to test:** Advanced query features

**Verify in output:**
```
=== Milestone E: Query Shaping (ORDER BY, LIMIT, OFFSET, GROUP BY) ===
[PASS] ORDER BY ASC works
[PASS] ORDER BY DESC works
[PASS] LIMIT works
[PASS] OFFSET works
[PASS] LIMIT + OFFSET pagination works
[PASS] GROUP BY works
[PASS] COUNT(*) aggregation works
Milestone E: PASSED
```

**What's tested:**
- ✓ ORDER BY ASC/DESC sorting
- ✓ LIMIT result limiting
- ✓ OFFSET row skipping
- ✓ LIMIT + OFFSET pagination
- ✓ GROUP BY grouping
- ✓ COUNT(*) aggregation

---

### Milestones 8B & 8C: Core DML & JOIN

**Verify in output:**
```
=== Milestone 8B: Basic DML & DDL ===
[PASS] CREATE TABLE works
[PASS] INSERT works
[PASS] SELECT with WHERE works
[PASS] UPDATE works
[PASS] DELETE works
[PASS] DROP TABLE works
Milestone 8B: PASSED

=== Milestone 8C: INNER JOIN ===
[PASS] INNER JOIN works correctly
Milestone 8C: PASSED
```

**What's tested:**
- ✓ Basic CRUD operations
- ✓ INNER JOIN with equi-join predicates
- ✓ Column projection in JOIN results

---

### Comprehensive End-to-End Test

**Verify in output:**
```
================================================================================
COMPREHENSIVE END-TO-END TEST: All Features Combined
================================================================================
[PASS] Created table with constraints
[PASS] Inserted 4 products
[PASS] NOT NULL constraint enforced
[PASS] PRIMARY KEY constraint enforced
[PASS] UPDATE works
[PASS] DELETE works and leaves correct rows
[PASS] ORDER BY works
[PASS] LIMIT works
[PASS] GROUP BY works
[PASS] INNER JOIN works
[PASS] DROP TABLE works
================================================================================
COMPREHENSIVE TEST: PASSED
```

**What's tested:**
- ✓ All features working together
- ✓ Complex multi-feature scenarios
- ✓ Data consistency across operations

---

## Testing Core Engine

### 1. Storage Engine

Tests file-based persistent storage:

```bash
python tests/unit/test_m1_storage.py
```

**Verification points:**
- Temporary file creation
- Page read/write operations
- Record encoding/decoding
- Catalog registration

**Expected behavior:**
```
=== Milestone 1 Core Storage Engine Test Harness ===
Temporary storage file: C:\Users\KAMIKAZE\AppData\Local\Temp\...
Written row 0 to page 0: [1, 'Alice', 100.5]
Read row 0 from page 0: [1, 'Alice', 100.5]
Registered tables in catalog: ['customers']
Retrieved table: customers, columns: ['id', 'name', 'balance']
Temporary storage file removed.
=== Test Harness Complete ===
```

### 2. SQL Pipeline

Tests complete SQL execution flow:

```bash
python tests/unit/test_m2_sql_pipeline.py
```

**Verification points:**
- Tokenization
- Parsing
- Planning
- Execution
- Result formatting

**Expected behavior:**
```
=== Milestone 2 SQL Pipeline Test (Engine-backed) ===

SQL: CREATE TABLE users (id INT, name TEXT, age INT);
Executed successfully (no output).

SQL: INSERT INTO users VALUES (1, 'Alice', 30);
Executed successfully (no output).

SQL: SELECT id, name FROM users;
Result:
{'id': 1, 'name': 'Alice'}
```

### 3. Indexing

Tests query optimization via indexes:

```bash
python tests/unit/test_m3_indexing.py
```

**Verification points:**
- B-tree index creation
- Single column lookups
- Composite index support
- Range searches
- Cost estimation

**Expected behavior:**
```
Created index on 'age'
Created composite index on ['age', 'name']

Search by age=30:
[{'id': 1, 'name': 'Alice', 'age': 30}]

Estimated full table scan cost: 4
Estimated indexed scan cost: 1
```

### 4. Transactions

Tests ACID properties and concurrency:

```bash
python tests/unit/test_m4_transactions.py
```

**Verification points:**
- Transaction commits
- Multi-reader concurrency
- MVCC (Multi-Version Concurrency Control)
- Isolation levels
- Consistency guarantees

**Expected behavior:**
```
[users] Inserted: {'id': 1, 'name': 'User1', 'age': 20}
Transaction <uuid> committed.

[Reader-1] Read 10 rows: [...]
[Reader-2] Read 10 rows: [...]
[Reader-3] Read 10 rows: [...]

Final table state: Table(users, rows=[...])
```

---

## Integration Testing

### Testing via Django API

#### 1. Start Django Server

```bash
cd backend
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

#### 2. Test CREATE TABLE

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);"}'
```

**Expected response:**
```json
{
  "status": "OK",
  "data": {"status": "OK"}
}
```

#### 3. Test INSERT

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "INSERT INTO users VALUES (1, '\''Alice'\'', 30);"}'
```

**Expected response:**
```json
{
  "status": "OK",
  "data": {"status": "OK"}
}
```

#### 4. Test SELECT

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users;"}'
```

**Expected response:**
```json
{
  "status": "OK",
  "data": [
    {"id": 1, "name": "Alice", "age": 30}
  ]
}
```

#### 5. Test Query Shaping

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users ORDER BY age DESC LIMIT 1;"}'
```

**Expected response:**
```json
{
  "status": "OK",
  "data": [
    {"id": 1, "name": "Alice", "age": 30}
  ]
}
```

#### 6. Test Constraint Enforcement

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "INSERT INTO users VALUES (1, NULL, 25);"}'
```

**Expected response (error):**
```json
{
  "status": "ERROR",
  "error": {
    "type": "ExecutionError",
    "message": "Column 'name' cannot be null"
  }
}
```

---

## Troubleshooting

### Issue: Unicode Errors in Test Output

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
```

**Solution:**
Tests have been updated to use ASCII-safe output. If you encounter this, ensure you're running the latest test files.

### Issue: ImportError: cannot import name 'RowPage'

**Error:**
```
ImportError: cannot import name 'RowPage' from 'engine.record.page_layout'
```

**Solution:**
RowPage has been moved to `engine.storage.page`. Update imports in any custom test files:

```python
from engine.storage.page import RowPage  # Correct location
```

### Issue: Tests Hang/Timeout

**Problem:** Tests take longer than 60 seconds

**Solutions:**
1. Check system resources (CPU, memory)
2. Ensure no other processes are using the database
3. Clear temporary files: `rm -rf /tmp/tmp*` (Linux/Mac) or temp directory (Windows)

### Issue: Permission Denied Error

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'tests/unit/test_milestones.py'
```

**Solution:**
Ensure Python has read permissions:

```bash
chmod +x tests/unit/test_milestones.py  # Linux/Mac
# Windows: Right-click → Properties → Security
```

### Issue: Django Server Won't Start

**Error:**
```
Address already in use
```

**Solution:**
Kill the process using port 8000:

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

---

## Test Quality Metrics

### Coverage Summary

- **Total Test Assertions:** 43+
- **Test Files:** 7 active modules
- **Pass Rate:** 100% (6/6 suites)
- **Execution Time:** ~40 seconds
- **Code Coverage:** Core engine, storage, SQL pipeline, indexing, transactions

### Assertion Distribution

- Milestone A: 4 assertions
- Milestone B: 1 assertion
- Milestone C: 4 assertions
- Milestone D: 3 assertions
- Milestone E: 8 assertions
- Milestones 8B/8C: 9 assertions
- Comprehensive scenario: 11 assertions

---

## Next Steps

After verifying all tests pass:

1. **Run specific test suites** for features you want to focus on
2. **Extend tests** as you add new functionality
3. **Use test output** as reference documentation for expected behavior
4. **Check docs/MILESTONES.md** for detailed feature descriptions

---

## Quick Reference

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Milestone Tests
```bash
python tests/unit/test_milestones.py
```

### Run Storage Tests
```bash
python tests/unit/test_m1_storage.py
```

### Run Transaction Tests
```bash
python tests/unit/test_m4_transactions.py
```

### Start Django
```bash
cd backend && python manage.py runserver
```

### Test Single Feature
```bash
python tests/unit/test_m3_indexing.py
```

---

## Summary

This guide provides a complete roadmap for testing all system functionalities:

- ✓ **Setup instructions** for getting started
- ✓ **Multiple testing options** (full suite, individual modules, API)
- ✓ **Expected outputs** for verification
- ✓ **Troubleshooting** for common issues
- ✓ **Integration testing** via Django API
- ✓ **Quality metrics** showing test coverage

All tests are automated, repeatable, and designed to verify expected behavior comprehensively.
