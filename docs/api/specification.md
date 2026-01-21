## Purpose

This document defines the **public API** of the custom Python RDBMS engine. It describes the exposed classes, methods, inputs, outputs, and error contracts. This API is the *only* supported interface between the database engine and the Django backend.

The engine is designed as an **embedded database**, not a networked service. Django loads and interacts with it in-process.

---

## Design Principles

* Explicit APIs over magic or reflection
* Deterministic behavior, no hidden side effects
* SQL parsing and execution fully owned by the engine
* Django is treated as a client, not a controller of database internals
* Errors are explicit, typed, and never silently swallowed

---

## High-Level Interaction Model

* Django receives HTTP requests
* Django validates/authenticates the request
* Django calls the database engine API
* The engine parses SQL, executes it, and returns structured results
* Django serializes results for the API or UI layer

Django **never** accesses storage files, indexes, or memory structures directly.

---

## Core Public Classes

### `Database`

Represents a single logical database instance.

#### Constructor

```text
Database(path: str, *, read_only: bool = False)
```

**Parameters**

* `path`: Filesystem path used for persistent storage
* `read_only`: Prevents mutating operations when set

**Behavior**

* Loads metadata and table definitions on initialization
* Does not eagerly load table data unless required

---

### `Database.execute()`

Executes a SQL statement.

```text
execute(sql: str, *, parameters: dict | None = None) -> QueryResult
```

**Inputs**

* `sql`: SQL-like statement as a string
* `parameters`: Optional named parameters for prepared execution

**Outputs**

* `QueryResult` object

**Notes**

* Multiple statements per call are intentionally unsupported
* Parameter binding is explicit and positional binding is disallowed

---

### `QueryResult`

Represents the outcome of a SQL execution.

**Attributes**

* `columns: list[str] | None`
* `rows: list[tuple] | None`
* `row_count: int`
* `status: Literal["OK", "ERROR"]`
* `message: str | None`

---

## Error Handling

All database errors raise subclasses of `DatabaseError`.

### Error Hierarchy

* `DatabaseError`

  * `SyntaxError`
  * `ExecutionError`
  * `ConstraintViolation`
  * `TransactionError`
  * `StorageError`

Errors are **never** returned as strings. Django must catch and map them to HTTP responses.

---

## Django Integration Contract

* Django loads a singleton `Database` instance at startup
* Database access is centralized in a service layer
* No Django models, migrations, or ORM features are used
* Transactions are scoped per request

---

## Explicit Non-Goals

* No Django-style query builder
* No implicit schema generation
* No background threads or async execution
