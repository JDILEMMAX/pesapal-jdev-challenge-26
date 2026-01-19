## Philosophy

The supported SQL subset is **minimal, explicit, and deterministic**. The goal is correctness and clarity, not completeness.

---

## Supported Statements

### Data Definition

* `CREATE TABLE`
* `DROP TABLE`

### Data Manipulation

* `INSERT INTO`
* `SELECT`
* `DELETE`

### Metadata Inspection

* `SHOW TABLES`

Updates are intentionally excluded to reduce complexity.

---

## Grammar (Simplified)

```text
statement ::= select | insert | delete | create_table | drop_table

select ::= SELECT column_list FROM table_name [ WHERE condition ]
```

---

## Constraints

Supported constraints:

* PRIMARY KEY
* NOT NULL
* UNIQUE

Unsupported constraints:

* FOREIGN KEY
* CHECK

---

## Examples

```sql
CREATE TABLE users (id INT PRIMARY KEY, name TEXT NOT NULL);
SELECT id, name FROM users WHERE id = 1;
```

---

## Intentional Limitations

* No JOINs
* No subqueries
* No aggregation

These features are excluded to keep query planning simple and inspectable.
