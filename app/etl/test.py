from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

query_file = BASE_DIR / "queries" / "top_customers.sql"

with open(query_file, "r") as f:
    query = f.read()

print(query)
