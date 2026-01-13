from .session import DBSession


def execute_query(sql: str):
    with DBSession() as engine:
        result = engine.execute(sql)
        return result  # Ensure result is JSON-serializable
