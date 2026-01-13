class EngineError(Exception):
    """Base class for all engine-specific exceptions."""
    pass

class SchemaError(EngineError):
    """Raised for schema validation errors."""
    pass

class PageError(EngineError):
    """Raised for page-level errors (bounds, corruption, etc)."""
    pass

class TransactionError(EngineError):
    """Raised for transaction-related failures (BEGIN, COMMIT, ROLLBACK)."""
    pass

class ConstraintViolationError(EngineError):
    """Raised when a table or column constraint is violated."""
    pass

# Query-level errors
class QueryError(Exception):
    pass

class ParseError(QueryError):
    """Raised when SQL cannot be parsed."""
    pass

class ExecutionError(QueryError):
    """Raised when SQL executes but fails (e.g., type mismatch, undefined table)."""
    pass
