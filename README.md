# Project Overview

This project implements a **custom relational database engine** and exposes it through a **Django-based HTTP service with a React-based frontend for the user interface**, deliberately avoiding Django’s ORM. The architecture is designed to keep the database engine framework-agnostic while allowing Django to act purely as a service and integration layer.

The focus is on **clarity of design, correctness, and architectural discipline**.

---

## Motivation

Most developers interact with databases as black boxes. This project explores what it means to *build one*, even at a limited scale.

---

## Architecture Summary

* Custom embedded RDBMS
* Django as application layer
* React as UI

---

## Features

* SQL parsing and execution
* Persistent storage
* Constraint enforcement
* Web-based query interface

---

## Running the System

### REPL

A standalone REPL is provided for direct database interaction.

### Web App

The system consists of **two independently running services**:

1. **Django backend** – exposes the database engine via HTTP
2. **React frontend** – provides a technical UI for issuing SQL queries

Both must be running for the full web experience.

---

# Database Engine Usage: Django & React Integration

This section explains how to:

* Create tables
* Insert data
* Retrieve data
* Run the Django integration layer
* Understand how the engine and Django interact

---

## 1. High-Level Architecture

```
HTTP Request
   ↓
Django View (API Layer)
   ↓
Session (app/db/session.py)
   ↓
Storage Engine (engine/)
   ↓
File-backed storage & in-memory structures
```

### Key Design Principles

* **No ORM usage**, all SQL is parsed and executed by the custom engine
* **Strong separation of concerns**:

  * `engine/` contains all database logic
  * `backend/` contains Django integration only
* **Engine is reusable** by both Django and standalone test harnesses

---

## 2. Engine Location & Imports

The `engine/` directory lives at the **project root**:

```
JDEV Challenge/
├── engine/
├── backend/
├── test_harness_mX.py
```

Django is configured to include the project root in `PYTHONPATH` via `manage.py`, allowing imports such as:

```python
from engine.storage_engine import StorageEngine
```

This ensures:

* Django can access the engine
* Test harnesses remain functional
* The engine stays framework-independent

---

## 3. Running the Django Service

### 3.1 Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3.2 Install Dependencies

```bash
pip install django
```

### 3.3 Start the Development Server

From the `backend/` directory:

```bash
python manage.py runserver
```

Server will start at:

```
http://127.0.0.1:8000/
```

---

## 4. Query API Endpoint (Updated)

The database engine is exposed via a single authenticated HTTP endpoint supporting both GET and POST requests:

```
GET /api/query/?q=<SQL_STATEMENT>
POST /api/query/  (JSON body: {"query": "<SQL_STATEMENT>"})
```

### Request Flow

1. HTTP request hits Django
2. `query_endpoint` validates input and authentication
3. SQL is extracted from either POST JSON body or GET query param
4. SQL is passed verbatim to the session layer
5. Session executes the query against the engine
6. Result is returned as JSON
7. Live logging prints query and result to console; errors are written to log file

### Example curl Requests

**GET:**

```bash
curl -X GET "http://127.0.0.1:8000/api/query/?q=SELECT%20*%20FROM%20users" -H "Authorization: Bearer <token>"
```

**POST:**

```bash
curl -X POST http://127.0.0.1:8000/api/query/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"query": "SELECT * FROM users"}'
```

---

## 5. React Frontend

This milestone introduces a **React-based, developer-oriented frontend** designed to interact directly with the custom database engine through the Django API layer.

The frontend prioritizes:

* Precision and clarity over visual noise
* Full visibility into query execution and results
* A consistent, high-contrast technical aesthetic
* Strict separation between UI and backend concerns

### Frontend Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── SqlEditor.jsx      # SQL input + execution controls
│   │   ├── ResultGrid.jsx     # Tabular query result display
│   │   ├── TableList.jsx      # Schema/navigation panel (UI-only for now)
│   ├── pages/
│   │   └── Dashboard.jsx     # Main application layout
│   ├── api/
│   │   └── dbClient.js       # HTTP client for query execution
│   └── styles/
│       └── theme.css         # Centralized application styling
```

* **Dashboard** defines the application layout
* **SqlEditor** captures and submits SQL queries
* **ResultGrid** renders query results and errors
* **TableList** (UI-only for now) represents schema visibility

### Layout Model

The UI follows a fixed, full-viewport layout:

* **Sidebar** – table/schema visibility
* **Main workspace** – SQL editor and query results

This structure is enforced via shared layout classes:

```css
.app-container
.sidebar
.main-content
```

All components inherit global styling from `theme.css` to ensure visual consistency.

---

### 5.1 SQL Editor

The SQL editor is a controlled component with:

* Multi-line SQL input
* Keyboard shortcut support (`Ctrl / Cmd + Enter`)
* Execution state awareness
* Minimal inline logic; styling is fully inherited from `theme.css`

Execution flow:

1. User submits SQL
2. Frontend sends request via `dbClient`
3. Django forwards SQL to the engine
4. Result or error is rendered in the ResultGrid

### 5.2 Result Grid

Query results are rendered dynamically based on response type:

* **Tabular output** for `SELECT` queries
* **Status-only responses** for `CREATE`, `INSERT`, etc.
* **Structured error output** when execution fails

The grid is scrollable, schema-driven, and styled for dense data inspection.

### 5.3 Table List (UI Stub)

`TableList` is currently a **presentation-only component**:

* No backend calls
* No mock data
* Acts as a visual contract for upcoming catalog APIs

Backend support (e.g. `SHOW TABLES`) will be introduced in a later milestone.

### Styling & Theming

All frontend styling is centralized in `theme.css`:

* CSS variables define color, typography, spacing, and accents
* Components avoid inline styles
* Accent colors are deliberately subdued to keep focus on data

This ensures consistency and prevents visual drift as the UI grows.

---

### Running the Frontend

From the `frontend/` directory:

```bash
npm install
npm run dev
```

The React app will start on its own development server and communicate with Django via the configured API base URL.

---

## 6. Creating Tables

### SQL Syntax

```sql
CREATE TABLE users (id, name, age);
```

### Example HTTP Request

**POST:**

```bash
curl -X POST http://127.0.0.1:8000/api/query/ \
     -H "Content-Type: application/json" \
     -d '{"query": "CREATE TABLE users (id, name, age)"}'
```

### Engine Behavior

* Registers table metadata
* Initializes in-memory row storage
* Errors if the table already exists

### Example Response

```json
{
  "status": "OK",
  "data": {"status": "OK"}
}
```

---

## 7. Inserting Data

### SQL Syntax

```sql
INSERT INTO users VALUES (1, 'Alice', 30);
```

### Example HTTP Request

**POST:**

```bash
curl -X POST http://127.0.0.1:8000/api/query/ \
     -H "Content-Type: application/json" \
     -d '{"query": "INSERT INTO users VALUES (1, 'Alice', 30)"}'
```

### Engine Behavior

* Validates table existence
* Validates column/value count
* Stores row as a dictionary internally

### Stored Row Representation

```python
{
  "id": 1,
  "name": "Alice",
  "age": 30
}
```

---

## 8. Retrieving Data

### SQL Syntax

```sql
SELECT * FROM users;
```

### Example HTTP Request

**POST:**

```bash
curl -X POST http://127.0.0.1:8000/api/query/ \
     -H "Content-Type: application/json" \
     -d '{"query": "SELECT * FROM users"}'
```

### Example Response

```json
{
  "status": "OK",
  "data": [
    {
      "id": 1,
      "name": "Alice",
      "age": 30
    }
  ]
}
```

### Notes

* Both GET and POST methods are supported
* Only `SELECT * FROM <table>` is supported at this stage
* Filtering, projections, and joins are planned for later milestones

---

## 9. Authentication Layer

All query requests are protected by a lightweight authentication decorator:

```python
@auth_required
def query_endpoint(request): ...
```

This ensures:

* Database access is not publicly exposed
* Security concerns remain isolated from the engine

---

## 10. Error Handling

Currently:

* Engine raises structured exceptions: `ParseError`, `SchemaError`, `ExecutionError`, `EngineError`
* Django maps these to HTTP 400 responses
* Unexpected exceptions result in HTTP 500 responses

### Example Error Responses

**Engine Error:**

```json
{
  "status": "ERROR",
  "error": {"type": "EngineError", "message": "Table users does not exist"}
}
```

**Invalid JSON or No Query:**

```json
{
  "status": "ERROR",
  "error": {"type": "InvalidRequest", "message": "No query provided"}
}
```

**Internal Server Error:**

```json
{
  "status": "ERROR",
  "error": {"type": "InternalError", "message": "An unexpected error occurred."}
}
```

*Live console logging shows query, success, and errors; all errors are also written to a rotating log file.*

---

## 11. Important Notes & Limitations

* This engine is **not transactional yet**
* Data persistence is minimal and evolving
* SQL parsing is intentionally simple
* Django migrations are unused (ORM disabled by design)

Warnings about unapplied Django migrations can be safely ignored for this project.

---

## 12. Summary

This milestone establishes a clean and extensible foundation:

* A standalone database engine
* A Django-based service layer
* Clear execution boundaries
* No framework lock-in

Future milestones will expand capabilities while preserving this separation.

---

## Documentation Index

* [Architecture](docs/architecture.md)
* [API Specification](docs/api_spec.md)
* [SQL Subset](docs/sql_subset.md)
* [Storage Engine](docs/storage_engine.md)
* [Design Tradeoffs](docs/tradeoffs.md)

---

## Credits

Developed as part of the Junior Dev Challenge RDBMS project.
