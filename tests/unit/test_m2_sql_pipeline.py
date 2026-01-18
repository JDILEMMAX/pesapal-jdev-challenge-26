import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now you can import modules relative to project root
from engine.sql.tokenizer import Tokenizer
from engine.sql.parser import Parser
from engine.engine import Engine
from backend.app.db.query import build_plan, execute_plan
# query.py can be accessed while outside engine since project root was added to sys.path


def parse_sql(sql: str):
    tokenizer = Tokenizer(sql)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def main():
    print("=== Milestone 2 SQL Pipeline Test (Engine-backed) ===")

    engine = Engine()

    sql_statements = [
        "CREATE TABLE users (id INT, name TEXT, age INT);",
        "INSERT INTO users VALUES (1, 'Alice', 30);",
        "INSERT INTO users VALUES (2, 'Bob', 25);",
        "INSERT INTO users VALUES (3, 'Charlie', 35);",
        "SELECT id, name FROM users;",
        "SELECT name, age FROM users WHERE age > 28;",
    ]

    for sql in sql_statements:
        print(f"\nSQL: {sql}")
        try:
            ast = parse_sql(sql)
            plan = build_plan(ast)
            result = execute_plan(plan, engine)

            if result:
                print("Result:")
                for row in result:
                    print(row)
            else:
                print("Executed successfully (no output).")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
