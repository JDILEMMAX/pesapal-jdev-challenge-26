## Storage Model

The engine uses a **page-based storage model** backed by the filesystem.

---

## Tables and Schemas

* Each table has a schema definition
* Schemas are immutable after creation
* Columns have fixed types

---

## Rows

* Rows are stored as fixed-length records
* Variable-length types are stored via offsets

---

## Indexing

* Single-column primary key index
* Implemented as an in-memory B-tree
* Persisted on flush

Secondary indexes are excluded.

---

## Persistence Strategy

* Metadata persisted eagerly
* Table data persisted on transaction commit
* Crash recovery via write-ahead logging (minimal)

---

## In-Memory vs Disk

* Active tables cached in memory
* Cold data read on demand
