import duckdb
import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
DB_PATH = "uk_data.duckdb"

def load_boe(filename, value_col):
    df = pd.read_csv(RAW / filename)
    df.columns = ["date", value_col]
    df["month"] = (pd.to_datetime(df["date"], format="%d-%b-%y").dt.to_period("M").dt.to_timestamp())
    return df[["month", value_col]]

def load_ons(filename, value_col):
    df = pd.read_csv(RAW / filename)
    df = df[df["period"].str.match(r"^\d{4} [A-Z]{3}$", na=False)].copy()
    df["month"] = pd.to_datetime(df["period"].str.title(), format="%Y %b")
    df[value_col] = pd.to_numeric(df[value_col])
    return df[["month", value_col]]

def check_monthly(name, df):
    """Fail loudly unless the table is a clean monthly series."""
    problems = []
    if not (df["month"].dt.day == 1).all():
        problems.append("dates not on the 1st of the month")
    if df["month"].duplicated().any():
        problems.append("duplicate months")
    expected = pd.date_range(df["month"].min(), df["month"].max(), freq="MS")
    if df["month"].nunique() != len(expected):
        problems.append(f"{len(expected) - df['month'].nunique()} missing months")
    if df.isna().any().any():
        problems.append("null values")
    if problems:
        raise ValueError(f"{name}: " + "; ".join(problems))

tables = {
    "bank_rate": load_boe("bank_rate.csv", "bank_rate_pct"),
    "mortgage_approvals": load_boe("mortgage_approvals.csv", "approvals_count"),
    "cpi_inflation": load_ons("cpi_inflation.csv", "cpi_annual_rate_pct"),
}

con = duckdb.connect(DB_PATH)
for name, df in tables.items():
    check_monthly(name, df)
    con.register("tmp_df", df)
    con.execute(f"""
        CREATE OR REPLACE TABLE {name} AS
        SELECT CAST(month AS DATE) AS month, * EXCLUDE (month)
        FROM tmp_df ORDER BY month
    """)
    con.unregister("tmp_df")
    rows, first, last = con.execute(
        f"SELECT COUNT(*), MIN(month), MAX(month) FROM {name}").fetchone()
    print(f"{name}: {rows} rows, {first} to {last}")
con.close()