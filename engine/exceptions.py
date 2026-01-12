class EngineError(Exception):
    """Base class for all engine-specific exceptions."""
    pass

class SchemaError(EngineError):
    """Raised for schema validation errors."""
    pass

class PageError(EngineError):
    """Raised for page-level errors (bounds, corruption, etc)."""
    pass

class QueryError(Exception):
    pass

class ParseError(QueryError):
    pass

class ExecutionError(QueryError):
    pass
