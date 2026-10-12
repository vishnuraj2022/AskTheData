import io
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append("src")
from agent import run_agent

st.set_page_config(page_title="Ask the data")
st.title("Ask the Data")
st.caption("Plain-English questions about UK Bank Rate, Inflation and mortgage approvals. Data: Bank of England and ONS")

question = st.text_input("Your question")

if st.button("Ask") and question:
    with st.spinner("Working on it...."):
        answer, trace = run_agent(question, verbose=False)
    
    st.subheader("Answer")
    st.write(answer)

    #use last success query
    good = [t for t in trace if t["tool"] == "run_sql" and "error" not in t["output"]]

    if good:
        df = pd.read_csv(io.StringIO(good[-1]["output"]["rows_csv"]))
        numeric = df.select_dtypes("number").columns.tolist()
        if "month" in df.columns and numeric and lens(df) >1:
            st.plotly_chart(px.line(df,x="month", y=numeric))
        st.dataframe(df)

    with st.expander("How this answer was produced"):
        for i, step in enumerate(trace, start=1):
            st.markdown(f"**Step{i}: `{step['tool']}`**")
            if step["tool"] == "run_sql":
                st.code(step["input"]["query"], language="sql")
            else:
                st.json(step["input"])