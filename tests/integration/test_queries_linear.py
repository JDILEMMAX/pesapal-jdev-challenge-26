# tests/integration/test_queries.py
"""
Enhanced API Integration Test: SQL Queries via API
- Supports GET and POST queries
- Automatically retries requests if backend is unreachable
- Provides meaningful messages for connection errors and bad requests
- Displays a summary of total, successful, and failed queries
"""

import requests
import json
import time

# Backend API endpoint
API_URL = "http://127.0.0.1:8000/api/query/"

# SQL queries to test
QUERIES = [
    ("GET", "SHOW TABLES;"),
    ("GET", "CREATE TABLE users (id INT, name TEXT, age INT);"),
    ("GET", "INSERT INTO users VALUES (1, 'Alice', 30);"),
    ("GET", "SELECT * FROM users;"),
    ("POST", "INSERT INTO users VALUES (2, 'Bob', 25);"),
    ("POST", "SELECT name, age FROM users;"),
    ("POST", "SELECT * FROM users WHERE age > 26;"),
    ("POST", "SELECT * FROM non_existing_table;"),
    ("POST", "INSERT INTO users VALUES (1);"),
]

# Retry configuration
RETRIES = 3        # Number of times to retry if backend is unreachable
RETRY_DELAY = 2    # Seconds to wait between retries

# Counters for summary
total_queries = len(QUERIES)
successful_requests = 0
failed_requests = 0

print("=== Enhanced API Integration Test: SQL Queries ===\n")

for method, sql in QUERIES:
    print(f"{method} SQL> {sql}")

    # Attempt request with retries
    for attempt in range(1, RETRIES + 1):
        try:
            if method.upper() == "GET":
                response = requests.get(API_URL, params={"q": sql}, timeout=5)
            elif method.upper() == "POST":
                response = requests.post(API_URL, json={"query": sql}, timeout=5)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Raise exception for HTTP errors (4xx/5xx)
            response.raise_for_status()

            # Successfully got a response
            print("Response:")
            try:
                # Pretty-print JSON if possible
                print(json.dumps(response.json(), indent=2))
            except json.JSONDecodeError:
                print(response.text)
            successful_requests += 1
            break  # Exit retry loop if successful

        except requests.exceptions.ConnectionError:
            if attempt < RETRIES:
                print(f"Cannot reach backend! Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Cannot reach backend! Make sure the server is running at {API_URL}")
                failed_requests += 1

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP {response.status_code} error: {http_err}")
            failed_requests += 1
            break

        except Exception as err:
            print(f"Unexpected error: {err}")
            failed_requests += 1
            break

    print()  # Add spacing between query outputs

# Summary block
print("=== Test Summary ===")
print(f"Total queries: {total_queries}")
print(f"Successful requests: {successful_requests}")
print(f"Failed requests: {failed_requests}")
print("=== API Integration Test Complete ===")
