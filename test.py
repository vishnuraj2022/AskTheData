import duckdb

con = duckdb.connect("uk_data.duckdb", read_only=True)

print(con.sql("SHOW TABLES"))
for table in ["bank_rate", "mortgage_approvals", "cpi_inflation"]:
    print(f"\n=== {table} ===")
    print(con.sql(f"SUMMARIZE {table}"))                          # profile of every column
    print(con.sql(f"SELECT * FROM {table} ORDER BY month LIMIT 5"))  # first 5 rows

# Then type your own queries; type exit to stop
while True:
    query = input("\nSQL> ")
    if query.strip().lower() in ("exit", "quit"):
        break
    try:
        print(con.sql(query))
    except Exception as error:
        print("Error:", error)

con.close()