# tests/integration/test_queries.py
"""
Integration Test: SQL Queries via API
This script tests SQL query execution via the backend API.
Both GET and POST methods are tested to simulate realistic scenarios.
"""

import json
import time
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/query/"
RETRY_DELAY = 2  # seconds
MAX_RETRIES = 2


def send_get_query(sql: str):
    """
    Send a SQL query via GET request.
    Returns response JSON or None if the backend is unreachable.
    """
    params = {"q": sql}
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(API_BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            if attempt < MAX_RETRIES:
                print(f"Cannot reach backend! Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Cannot reach backend! Make sure the server is running at {API_BASE_URL}")
                return None
        except requests.HTTPError as e:
            print(f"HTTP GET error: {e}")
            return None


def send_post_query(sql: str):
    """
    Send a SQL query via POST request.
    Returns response JSON or None if the backend is unreachable.
    """
    payload = {"query": sql}
    headers = {"Content-Type": "application/json"}
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(API_BASE_URL, headers=headers, json=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            if attempt < MAX_RETRIES:
                print(f"Cannot reach backend! Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Cannot reach backend! Make sure the server is running at {API_BASE_URL}")
                return None
        except requests.HTTPError as e:
            print(f"HTTP POST error: {e}")
            return None


def run_queries():
    """
    Runs a series of SQL queries using both GET and POST requests.
    Prints the responses or errors in a readable format.
    """
    queries = [
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

    total_queries = len(queries)
    success_count = 0
    fail_count = 0

    print("=== Enhanced API Integration Test: SQL Queries ===\n")

    for method, sql in queries:
        print(f"{method} SQL> {sql}")
        response = send_get_query(sql) if method == "GET" else send_post_query(sql)

        if response is None:
            fail_count += 1
        else:
            success_count += 1
            print("Response:")
            print(json.dumps(response, indent=2))
        print()  # newline for readability

    print("=== Test Summary ===")
    print(f"Total queries: {total_queries}")
    print(f"Successful requests: {success_count}")
    print(f"Failed requests: {fail_count}")
    print("=== API Integration Test Complete ===\n")


if __name__ == "__main__":
    run_queries()
