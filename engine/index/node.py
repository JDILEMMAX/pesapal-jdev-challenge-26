# engine/index/node.py

class Node:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []       # List of keys
        self.children = []   # Pointers to child nodes (internal) or records (leaf)
        self.next = None     # Next leaf node for range queries

    def is_full(self, order):
        return len(self.keys) >= order

    def __repr__(self):
        if self.is_leaf:
            return f"<LeafNode keys={self.keys}>"
        else:
            return f"<InternalNode keys={self.keys}>"
