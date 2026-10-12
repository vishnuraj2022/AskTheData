import duckdb
from llm import ask

DB_PATH = "uk_data.duckdb"

with open("data_dictionary.yaml") as f:
    DICTIONARY = f.read()

SYSTEM = f"""You are a careful data analyst who writes DuckDB SQL
Use only the tables and columns described below.

{DICTIONARY}

Rules:
- Return ONLY the SQL query. No explanation and no markdown fences.
- Only write SELECT queries.
- Join tables on month.
- If the question cannot be answered from these tables, return exactly: CANNOT_ANSWER
 """

def question_to_ask(question):
    return ask(question, system=SYSTEM).strip()

def run_sql(sql):
    con = duckdb.connect(DB_PATH, read_only = True, config={"enable_external_access": False})
    try:
        return con.execute(sql).df()
    finally:
        con.close()

if __name__ == "__main__":
    question = input("Ask a question: ")
    sql = question_to_ask(question)
    print("\nSQL:\n",sql)
    if sql != "CANNOT_ANSWER":
        print(run_sql(sql))