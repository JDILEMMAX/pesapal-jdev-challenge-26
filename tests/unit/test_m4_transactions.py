import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import threading
import time
from engine.transaction.transaction import Transaction
from engine.transaction.lock_manager import LockManager


# --- Mock table structure from Milestone 3 ---
class Table:
    def __init__(self, name):
        self.name = name
        self.rows = []
        self.lock = threading.Lock()  # internal lock for atomic row updates

    def insert(self, row):
        with self.lock:
            self.rows.append(row)
            print(f"[{self.name}] Inserted: {row}")

    def delete(self, row):
        with self.lock:
            self.rows.remove(row)
            print(f"[{self.name}] Deleted: {row}")

    def read_all(self):
        with self.lock:
            # Return a copy for safe concurrent reading
            return list(self.rows)

    def __str__(self):
        return f"Table({self.name}, rows={self.rows})"


# --- Initialize table ---
users_table = Table("users")


# --- Worker functions ---
def writer_worker(row):
    txn = Transaction()
    try:
        txn.insert(users_table, row)
        txn.commit()
    except Exception as e:
        print(f"Transaction {txn.txn_id} failed: {e}")
        txn.rollback()


def reader_worker(reader_id):
    # Simulate a read transaction
    for _ in range(3):  # read multiple times
        LockManager().acquire_read(users_table.name, f"reader-{reader_id}")
        rows = users_table.read_all()
        LockManager().release_read(users_table.name)
        print(f"[Reader-{reader_id}] Read {len(rows)} rows: {rows}")
        time.sleep(0.1)  # simulate processing time


# --- Start concurrent writers ---
num_writers = 10
writer_threads = []
for i in range(num_writers):
    row = {"id": i + 1, "name": f"User{i+1}", "age": 20 + i}
    t = threading.Thread(target=writer_worker, args=(row,))
    writer_threads.append(t)
    t.start()

# --- Start concurrent readers ---
num_readers = 3
reader_threads = []
for i in range(num_readers):
    t = threading.Thread(target=reader_worker, args=(i + 1,))
    reader_threads.append(t)
    t.start()

# Wait for all threads to complete
for t in writer_threads + reader_threads:
    t.join()

# --- Final table state ---
print("\nFinal table state:")
print(users_table)
