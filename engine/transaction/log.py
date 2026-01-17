import os
import json
from datetime import datetime


class WALog:
    def __init__(self, path="backend/logs/transaction.log"):
        self.path = path

        # Ensure log directory exists
        dir_name = os.path.dirname(self.path)
        if dir_name:  # Only create directory if not empty
            os.makedirs(dir_name, exist_ok=True)

    # def __init__(self, path="transaction.log"):
    #     self.path = path
    #     # no os.makedirs needed for current folder

    def log(self, txn_id, action, table, data):
        entry = {
            "timestamp": str(datetime.utcnow()),
            "txn_id": txn_id,
            "action": action,
            "table": table,
            "data": data,
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def recover(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r") as f:
            return [json.loads(line) for line in f.readlines()]
