import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Cat Pie Chart", page_icon="🐱")

st.title("🐱 Cat Breeds — Pie Chart")
st.caption(
    "Reads data from `data/pie_demo.csv` and guarantees **no more than 5 slices** "
    "by grouping smaller categories into **Other**."
)

@st.cache_data
def load_data() -> pd.DataFrame:
    # This page lives in pages/, so go up one level to reach repo root, then into data/
    csv_path = Path(__file__).parent.parent / "data" / "pie_demo.csv"
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]
    if not {"category", "value"}.issubset(df.columns):
        raise ValueError("CSV must have columns named 'category' and 'value'.")
    df = df[pd.to_numeric(df["value"], errors="coerce").notna()].copy()
    df["value"] = df["value"].astype(float).clip(lower=0)
    return df

def top_n_with_other(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Keep top n-1 rows and sum the rest into 'Other' to ensure <= n slices."""
    d = df.sort_values("value", ascending=False).reset_index(drop=True)
    if len(d) <= n:
        return d
    top = d.iloc[: n - 1].copy()
    other_sum = d.iloc[n - 1 :]["value"].sum()
    if other_sum > 0:
        top.loc[len(top)] = {"category": "Other", "value": other_sum}
    return top

df = load_data()

st.subheader("Input data")
st.dataframe(df, use_container_width=True)

pie_df = top_n_with_other(df, n=5)

st.subheader("Pie chart")
fig, ax = plt.subplots()
ax.pie(pie_df["value"], labels=pie_df["category"], autopct="%1.1f%%", startangle=90)
ax.axis("equal")  # Draw as a circle
st.pyplot(fig, clear_figure=True)

st.caption("Add as many rows as you want—extra categories are automatically grouped into 'Other'.")
