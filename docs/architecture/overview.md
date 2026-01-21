## Overview

The system is composed of three major layers:

1. Custom Python RDBMS (core engine)
2. Django backend (application and API layer)
3. React frontend (presentation layer)

Each layer has strict boundaries and communicates through well-defined interfaces.

---

## Component Diagram (Conceptual)

```text
[ React UI ]
     |
 HTTP/JSON
     |
[ Django Backend ]
     |
 Python API calls
     |
[ Custom RDBMS Engine ]
     |
 Filesystem
```

---

## Custom RDBMS Engine

Responsibilities:

* SQL parsing
* Query planning
* Execution
* Constraint enforcement
* Storage management

Non-responsibilities:

* Authentication
* Authorization
* Networking
* Schema migrations

---

## Django Backend

Responsibilities:

* HTTP routing
* Authentication and authorization
* Input validation
* Transaction scoping
* Error translation

Django treats the database engine as a **library**, not a service.

---

## React Frontend

Responsibilities:

* User interaction
* Query submission
* Result visualization

No database logic exists in the frontend.

---

## Data Flow

1. User submits query or action
2. React sends request to Django
3. Django validates and forwards SQL to engine
4. Engine executes and returns `QueryResult`
5. Django serializes response
6. React renders results

---

## Separation of Concerns

* SQL semantics live only in the engine
* Business logic lives in Django
* Presentation logic lives in React
