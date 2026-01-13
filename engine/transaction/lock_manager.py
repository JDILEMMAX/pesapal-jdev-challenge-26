import threading
from collections import defaultdict


class LockManager:
    def __init__(self):
        self.locks = defaultdict(lambda: {"readers": 0, "writer": None})
        self.condition = threading.Condition()

    def acquire_read(self, resource_id, txn_id):
        with self.condition:
            while self.locks[resource_id]["writer"] not in (None, txn_id):
                self.condition.wait()
            self.locks[resource_id]["readers"] += 1

    def release_read(self, resource_id):
        with self.condition:
            self.locks[resource_id]["readers"] -= 1
            if self.locks[resource_id]["readers"] == 0:
                self.condition.notify_all()

    def acquire_write(self, resource_id, txn_id):
        with self.condition:
            while (
                self.locks[resource_id]["writer"] not in (None, txn_id)
                or self.locks[resource_id]["readers"] > 0
            ):
                self.condition.wait()
            self.locks[resource_id]["writer"] = txn_id

    def release_write(self, resource_id):
        with self.condition:
            self.locks[resource_id]["writer"] = None
            self.condition.notify_all()
