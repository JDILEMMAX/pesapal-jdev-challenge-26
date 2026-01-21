## Design Tradeoffs

### Simplicity vs Completeness

The system favors a small, understandable core over feature richness.

---

### No ORM

Rejected because:

* Obscures SQL execution
* Conflicts with learning goals

---

### No Network Protocol

Embedding simplifies deployment and debugging.

---

## Known Limitations

* Single-process only
* No concurrent writers
* Limited SQL subset

---

## Future Improvements

* MVCC
* Secondary indexes
* Query optimizer
