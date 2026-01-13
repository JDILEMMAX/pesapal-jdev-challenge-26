from engine.storage_engine import StorageEngine

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = StorageEngine(db_path="data/dbfile")
    return _engine
