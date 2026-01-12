## Project Overview

This project implements a **custom relational database engine in Python**, integrated with Django (without its ORM) and exposed through a React-based frontend.

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

* Start Django backend
* Start React frontend
* Access via browser

---

## Documentation Index

* api_spec.md
* architecture.md
* sql_subset.md
* storage_engine.md
* tradeoffs.md

---

## Limitations

This is not a production database. It is a learning-focused system.

---

## Credits

Developed as part of the Junior Dev Challenge RDBMS project.
