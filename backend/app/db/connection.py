from engine.engine import Engine

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        # Engine uses absolute path by default when db_path is None
        _engine = Engine()
    return _engine
