# engine/index/index_manager.py

from .btree import BPlusTree

class IndexManager:
    def __init__(self):
        # table_name -> {columns_tuple: BPlusTree}
        self.indexes = {}

    def create_index(self, table, columns):
        """Create a B+ Tree index on given columns."""
        tree = BPlusTree()
        for row in table.rows():  # Milestone 2 table API
            key = tuple(row[col] for col in columns) if isinstance(columns, (list, tuple)) else row[columns]
            tree.insert(key, row)
        self.indexes.setdefault(table.name, {})[tuple(columns) if isinstance(columns, (list, tuple)) else (columns,)] = tree

    def search(self, table, columns, key):
        """Search the index for a given key."""
        tree = self.indexes.get(table.name, {}).get(tuple(columns) if isinstance(columns, (list, tuple)) else (columns,))
        if tree:
            return tree.search(key)
        return None
