# engine/transaction/transaction.py

import uuid
from engine.transaction.lock_manager import LockManager
from engine.transaction.log import WALog

# Global lock manager and WAL instance
lock_manager = LockManager()
wal = WALog()

class Transaction:
    def __init__(self):
        self.txn_id = str(uuid.uuid4())
        self.active = True
        self.actions = []

    def insert(self, table, row):
        if not self.active:
            raise Exception("Transaction is no longer active")

        # Acquire write lock for the table (single-writer)
        lock_manager.acquire_write(table.name, self.txn_id)

        try:
            # Log the action first (WAL) using table name (JSON serializable)
            wal.log(self.txn_id, "INSERT", table.name, row)
            
            # Perform the insert
            table.insert(row)

            # Track action for possible rollback
            self.actions.append(("INSERT", table, row))

        finally:
            # Release write lock
            lock_manager.release_write(table.name)

    def commit(self):
        # Transaction committed; WAL already persisted
        self.active = False
        print(f"Transaction {self.txn_id} committed.")

    def rollback(self):
        # Undo actions in reverse order
        for action, table, row in reversed(self.actions):
            if action == "INSERT":
                table.delete(row)
        self.active = False
        print(f"Transaction {self.txn_id} rolled back.")
