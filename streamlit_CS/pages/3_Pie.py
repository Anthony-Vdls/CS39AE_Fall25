import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="3_Pie (CSV Reader Only)", page_icon="📄")

st.title("CSV Reader — pie_demo.csv")
st.caption("Reads `data/pie_demo.csv` and displays it. No plotting.")

@st.cache_data
def load_data() -> pd.DataFrame:
    # This page is inside /pages, so go up one level → /data/pie_demo.csv
    csv_path = Path(__file__).parent.parent / "data" / "pie_demo.csv"
    df = pd.read_csv(csv_path)
    # normalize column names
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

# Basic validation: require 5 or more data points (rows)
row_count = len(df)
if row_count < 5:
    st.error(f"Expected ≥ 5 data points, but found {row_count}. Add more rows to `data/pie_demo.csv`.")
else:
    st.success(f"Loaded {row_count} data points from `data/pie_demo.csv`.")

st.subheader("Data preview")
st.dataframe(df, use_container_width=True)

st.caption("Tip: Keep the file named exactly `pie_demo.csv` inside the `data/` folder.")

