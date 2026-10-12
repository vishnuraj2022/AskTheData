import duckdb
from llm import ask
from guardrails import make_safe

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

def answer(question, max_attempts=3):
    prompt = question
    for attempt in range(1,max_attempts+1):
        sql = clean_sql(ask(prompt, system=SYSTEM))
        if sql == "CANNOT_ANSWER":
            return sql, None
        try:
            safe_sql = make_safe(sql)
            return safe_sql, run_sql(safe_sql)
        except Exception as error:
            print(f"Attempt {attempt} failed: {error}")
            prompt = (f"{question}\n\nYour previous SQL:\n{sql}\n\n"
                      f"failed with this error:\n{error}\n\n"
                      "Write a corrected query.")
    raise RuntimeError("Could not produce a valid query.")

if __name__ == "__main__":
    question = input("Ask a question: ")
    sql = question_to_ask(question)
    print("\nSQL:\n",sql)
    if sql != "CANNOT_ANSWER":
        print(run_sql(sql))