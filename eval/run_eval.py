import sys
import time
import pandas as pd

sys.path.append("src")
from agent import run_agent, connect, client

JUDGE_MODEL = "claude-sonnet-5-5"

REFUSAL_WORDS = ["cannot", "can't", "not available", "don't have", "unable", "no data", "not in the data", "does not contain",
                 "doesn't contain", "does not include", "doesn't include"]



def column_values(series):
    """One column as sorted strings, with numbers rounded to 2 decimal points"""

    if pd.api.types.is_numeric_dtype(series):
        series = series.round(2)
    return sorted(series.astype(str))

def results_match(agent_df, gold_df):
    """Correct if row counts match and every gold column appears in the agent's result. Extra columns from the agent (e.g. month) are fine."""

    if len(agent_df) != len(gold_df):
        return False
    agent_columns = [column_values(agent_df[c]) for c in agent_df.columns]
    return all(column_values(gold_df[c]) in agent_columns for c in gold_df.columns)

JUDGE_SYSTEM = """You grade answers from a data analyst agent.
You get a question, the correct result from a trusted query (CSV), and the agent's written answer. 
Reply CORRECT if the answer states the same values as the correct result, ignoring formatting, units, 
rounding to 2 decimal places and extra context. Reply INCORRECT if any value is missing or different.
Reply with one word only: CORRECT or INCORRECT."""

def judge(question, gold_df, answer):
    """LLM-as-judge: does the written answer match the gold result?"""
    prompt = (f"Question: {question}\n\nCorrect result:\n"
              f"{gold_df.to_csv(index=False)}\nAgent's answer:\n{answer}")
    reply = client.messages.create(
        model=JUDGE_MODEL, max_tokens=1024, system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": prompt}])
    verdict = "".join(b.text for b in reply.content if b.type == "text")
    return verdict.strip().upper().startswith("CORRECT")

gold = pd.read_csv("eval/gold_questions.csv")
con = connect()
rows = []

for q in gold.itertuples():
    start = time.time()
    answer, trace = run_agent(q.question, verbose=False)
    seconds = round(time.time() - start, 1)
    good = [t for t in trace if t["tool"] == "run_sql" and "error" not in t["output"]]

    sql_match = None
    if q.answerable == "yes":
        gold_df = con.execute(q.gold_sql).df()
        if good:
            agent_df = con.execute(good[-1]["output"]["sql_executed"]).df()
            sql_match = results_match(agent_df, gold_df)
        correct = judge(q.question, gold_df, answer)

    else:
        correct = any(word in answer.lower() for word in REFUSAL_WORDS)
    
    rows.append({"id": q.id, "category": q.category, "correct": correct, "final_sql_match": sql_match, "steps": len(trace), 
                 "seconds": seconds, "answer": answer})
    print(f"{q.id}: {'PASS' if correct else 'FAIL'}")

con.close()
results = pd.DataFrame(rows)
results.to_csv("eval/results.csv", index=False)
print(results.groupby("category")["correct"].mean().round(2))
print("Overall Accuracy:", round(results["correct"].mean(),2))
strict = results["final_sql_match"].dropna().astype(bool)
print("Final query matched gold:", round(strict.mean(), 2))