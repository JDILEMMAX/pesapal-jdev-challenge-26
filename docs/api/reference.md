# Integration Guide: Django REST API

This guide explains how to integrate with the custom database engine through the Django REST API layer.

---

## Overview

The Django backend provides a RESTful interface to the custom RDBMS engine. This guide covers:

1. API endpoints and their usage
2. Request/response formats
3. Authentication
4. Error handling
5. Real-world examples

---

## Architecture

```
HTTP Client (curl, React, etc.)
    ↓
Django URL Router
    ↓
View Function (authentication decorator)
    ↓
Session Manager (database connection)
    ↓
Query Executor (planning and execution)
    ↓
Storage Engine (physical operations)
```

---

## Getting Started

### Prerequisites

1. **Python 3.13+** installed
2. **Django installed**: `pip install django`
3. **Backend running**: `cd backend && python manage.py runserver`

### Server Startup

```bash
cd "c:\Users\KAMIKAZE\Desktop\JDEV Challenge\backend"
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
Django version 4.2.x, using settings 'backend.settings'
```

Server will run at `http://127.0.0.1:8000/`

---

## API Endpoints

### 1. Execute Query

**Endpoint:** `POST /api/query/execute/`

**Purpose:** Execute arbitrary SQL statements

**Request Format:**
```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users;"}'
```

**Request Body:**
```json
{
  "query": "SQL_STATEMENT_HERE"
}
```

**Success Response (200):**
```json
{
  "status": "OK",
  "data": [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 25}
  ]
}
```

**Error Response (400):**
```json
{
  "status": "ERROR",
  "error": {
    "type": "ExecutionError",
    "message": "Table 'users' does not exist"
  }
}
```

**Supported SQL:**
- SELECT with WHERE, ORDER BY, LIMIT, OFFSET, GROUP BY
- INSERT INTO ... VALUES
- UPDATE ... SET ... WHERE
- DELETE FROM ... WHERE
- CREATE TABLE ... 
- DROP TABLE ...
- INNER JOIN

---

### 2. Health Check

**Endpoint:** `GET /api/health/`

**Purpose:** Check server and engine status

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/health/
```

**Success Response (200):**
```json
{
  "status": "OK",
  "message": "Server is running",
  "timestamp": "2026-01-20T10:30:00Z"
}
```

---

### 3. Database Statistics

**Endpoint:** `GET /api/stats/`

**Purpose:** Get database usage statistics

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/stats/
```

**Success Response (200):**
```json
{
  "status": "OK",
  "data": {
    "tables_count": 3,
    "total_rows": 150,
    "storage_size_bytes": 65536
  }
}
```

---

### 4. List Tables

**Endpoint:** `GET /api/tables/`

**Purpose:** Get all tables with row counts

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/tables/
```

**Success Response (200):**
```json
{
  "status": "OK",
  "data": [
    {"name": "users", "rows": 5},
    {"name": "orders", "rows": 12},
    {"name": "products", "rows": 8}
  ]
}
```

---

### 5. Get Table Schema

**Endpoint:** `GET /api/tables/{table_name}/`

**Purpose:** Get table structure and column information

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/tables/users/
```

**Success Response (200):**
```json
{
  "status": "OK",
  "data": {
    "name": "users",
    "columns": [
      {"name": "id", "type": "INTEGER", "nullable": false},
      {"name": "name", "type": "TEXT", "nullable": false},
      {"name": "age", "type": "INTEGER", "nullable": true}
    ]
  }
}
```

---

### 6. Get Table Rows

**Endpoint:** `GET /api/tables/{table_name}/rows/`

**Purpose:** Retrieve all rows from a table

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/tables/users/rows/
```

**Success Response (200):**
```json
{
  "status": "OK",
  "data": [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 25}
  ]
}
```

---

### 7. Insert Row

**Endpoint:** `POST /api/tables/{table_name}/rows/new/`

**Purpose:** Insert a new row into a table

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/tables/users/rows/new/ \
  -H "Content-Type: application/json" \
  -d '{"id": 3, "name": "Charlie", "age": 35}'
```

**Request Body:**
```json
{
  "id": 3,
  "name": "Charlie",
  "age": 35
}
```

**Success Response (201):**
```json
{
  "status": "OK",
  "data": {"inserted": 1}
}
```

**Error Response (400):**
```json
{
  "status": "ERROR",
  "error": {
    "type": "ExecutionError",
    "message": "Duplicate primary key value: id=3"
  }
}
```

---

### 8. Delete Row

**Endpoint:** `DELETE /api/tables/{table_name}/rows/{row_id}/`

**Purpose:** Delete a specific row from a table

**Request:**
```bash
curl -X DELETE http://127.0.0.1:8000/api/tables/users/rows/1/
```

**Success Response (200):**
```json
{
  "status": "OK",
  "data": {"deleted": 1}
}
```

---

### 9. Reset Database

**Endpoint:** `POST /api/reset/`

**Purpose:** Drop all tables and reset database to empty state

**Warning:** This operation is destructive and cannot be undone.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/reset/
```

**Success Response (200):**
```json
{
  "status": "OK",
  "data": {"tables_dropped": 3}
}
```

---

## Complete Workflow Example

Here's a complete example demonstrating all major operations:

### Step 1: Create Table

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price FLOAT);"
  }'
```

**Response:**
```json
{"status": "OK", "data": {"status": "OK"}}
```

### Step 2: Insert Data

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "INSERT INTO products VALUES (1, '\''Laptop'\'', 999.99);"
  }'
```

### Step 3: Query with Filtering

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM products WHERE price > 500 ORDER BY price DESC LIMIT 5;"
  }'
```

### Step 4: Update Data

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "UPDATE products SET price = 899.99 WHERE id = 1;"
  }'
```

### Step 5: Delete Data

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "DELETE FROM products WHERE price < 100;"
  }'
```

### Step 6: Verify Results

```bash
curl -X GET http://127.0.0.1:8000/api/tables/products/
```

---

## Authentication

### Current Implementation

The API uses lightweight token-based authentication via the `@auth_required` decorator.

### Adding Authorization Header

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{"query": "SELECT * FROM users;"}'
```

### Disabling Authentication (Development)

For local development, authentication can be disabled by commenting out the decorator in `backend/app/views.py`.

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "status": "ERROR",
  "error": {
    "type": "ERROR_TYPE",
    "message": "Human-readable error message"
  }
}
```

### Common Error Types

| Type | HTTP Status | Cause |
|------|------------|-------|
| InvalidRequest | 400 | Missing or malformed query |
| ParseError | 400 | SQL syntax error |
| ExecutionError | 400 | Runtime error (table not found, constraint violation, etc.) |
| AuthenticationError | 401 | Missing or invalid authentication token |
| InternalError | 500 | Unexpected server error |

### Example Errors

**Table not found:**
```json
{
  "status": "ERROR",
  "error": {
    "type": "ExecutionError",
    "message": "Table 'nonexistent' does not exist"
  }
}
```

**Constraint violation:**
```json
{
  "status": "ERROR",
  "error": {
    "type": "ExecutionError",
    "message": "Column 'name' cannot be null"
  }
}
```

**Syntax error:**
```json
{
  "status": "ERROR",
  "error": {
    "type": "ParseError",
    "message": "Unexpected token 'INVALID' at position 15"
  }
}
```

---

## Advanced Queries

### Complex SELECT with Multiple Conditions

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT id, name, COUNT(*) as count FROM orders WHERE date > 2025-01-01 GROUP BY id, name ORDER BY count DESC LIMIT 10;"
  }'
```

### JOIN Query

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT u.name, o.product FROM users u INNER JOIN orders o ON u.id = o.user_id;"
  }'
```

### Pagination

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM users LIMIT 20 OFFSET 40;"
  }'
```

---

## Using with Programming Languages

### Python (requests library)

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"

# Execute query
response = requests.post(
    f"{BASE_URL}/query/execute/",
    json={"query": "SELECT * FROM users;"}
)

print(response.json())
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://127.0.0.1:8000/api/query/execute/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'SELECT * FROM users;'})
});

const data = await response.json();
console.log(data);
```

### cURL Bash Script

```bash
#!/bin/bash

API_URL="http://127.0.0.1:8000/api"

execute_sql() {
  local sql=$1
  curl -s -X POST "$API_URL/query/execute/" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$sql\"}"
}

# Example
execute_sql "SELECT * FROM users WHERE age > 25;"
```

---

## Performance Tips

### 1. Use Indexes

For large tables, create indexes on frequently queried columns:

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE INDEX idx_age ON users(age);"}'
```

### 2. Limit Result Sets

Always use LIMIT for large queries:

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users LIMIT 1000;"}'
```

### 3. Use Specific Columns

Avoid SELECT * when possible:

```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT id, name FROM users WHERE active = 1;"}'
```

---

## Troubleshooting

### Connection Refused

**Error:** `Connection refused`

**Solution:** Ensure Django server is running:
```bash
cd backend && python manage.py runserver
```

### Invalid JSON

**Error:** `Bad Request: Invalid JSON body`

**Solution:** Validate JSON syntax:
```bash
# Use jq to validate
echo '{"query": "SELECT * FROM users;"}' | jq .
```

### Table Not Found

**Error:** `Table 'table_name' does not exist`

**Solution:** Create the table first or check spelling:
```bash
curl -X POST http://127.0.0.1:8000/api/query/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE TABLE table_name (id INTEGER);"}'
```

### CORS Issues (Frontend)

If accessing from a different origin, enable CORS:

Add to `backend/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

---

## Summary

The Django API provides:

- ✓ **Complete SQL execution** - All DML/DDL operations
- ✓ **Schema introspection** - List tables and columns
- ✓ **Data management** - CRUD operations
- ✓ **Error handling** - Structured error responses
- ✓ **Performance** - Index-based optimization
- ✓ **Extensibility** - Easy to add new endpoints

---

## Next Steps

1. Start the Django server
2. Test endpoints using curl or your preferred HTTP client
3. Integrate with your frontend or application
4. Refer to MILESTONES.md for SQL capabilities
5. Check TESTING_GUIDE.md for comprehensive testing

---

## Additional Resources

- [Milestones & Capabilities](../milestones/overview.md) - Feature overview
- [Testing Guide](../tests/reference.md) - Test execution instructions
- [Architecture Overview](../architecture/overview.md) - System design
- [SQL Subset](../sql/subset.md) - Supported SQL syntax
