# engine/index/btree.py

from .node import Node
import bisect

class BPlusTree:
    def __init__(self, order=4):
        self.root = Node(is_leaf=True)
        self.order = order

    def _normalize_key(self, key):
        """Ensure all keys are tuples for consistent comparison (single or composite)."""
        if not isinstance(key, tuple):
            key = (key,)
        return key

    def search(self, key):
        """
        Search for key in the B+ Tree.
        Returns a list of matching rows (for composite keys or duplicates) or None.
        """
        key = self._normalize_key(key)
        node = self.root
        while not node.is_leaf:
            # Descend to the correct child
            i = bisect.bisect_right(node.keys, key)
            node = node.children[i]

        # Scan leaf for all matches
        results = []
        for i, k in enumerate(node.keys):
            if k == key:
                results.append(node.children[i])
        return results if results else None

    def insert(self, key, value):
        key = self._normalize_key(key)
        root = self.root
        split_info = self._insert_recursive(root, key, value)
        if split_info:
            # Root split
            new_root = Node(is_leaf=False)
            new_root.keys = [split_info['key']]
            new_root.children = [root, split_info['new_node']]
            self.root = new_root

    def _insert_recursive(self, node, key, value):
        if node.is_leaf:
            # Insert key in sorted order in leaf
            i = bisect.bisect_left(node.keys, key)
            node.keys.insert(i, key)
            node.children.insert(i, value)
            if node.is_full(self.order):
                return self._split_leaf(node)
            return None
        else:
            # Internal node
            i = bisect.bisect_right(node.keys, key)  # descend to correct child
            split_info = self._insert_recursive(node.children[i], key, value)
            if split_info:
                # Insert new key and child reference
                insert_i = bisect.bisect_right(node.keys, split_info['key'])
                node.keys.insert(insert_i, split_info['key'])
                node.children.insert(insert_i + 1, split_info['new_node'])
                if node.is_full(self.order):
                    return self._split_internal(node)
            return None

    def _split_leaf(self, leaf):
        mid = len(leaf.keys) // 2
        new_leaf = Node(is_leaf=True)
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.children = leaf.children[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.children = leaf.children[:mid]

        # Link leaf nodes
        new_leaf.next = leaf.next
        leaf.next = new_leaf

        # Return first key of new leaf for parent
        return {'key': new_leaf.keys[0], 'new_node': new_leaf}

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        new_node = Node(is_leaf=False)
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]

        mid_key = node.keys[mid]

        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]

        return {'key': mid_key, 'new_node': new_node}
