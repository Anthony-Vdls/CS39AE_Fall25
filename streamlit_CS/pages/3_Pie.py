# pages/3_Pie.py
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Pie Chart", page_icon="🥧", layout="centered")

# ---------- Paths & Data ----------
# pages/3_Pie.py lives one level below project root, so parent -> project root
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "pie_demo.csv"

@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Basic sanity checks
    required_cols = {"category", "value"}
    if not required_cols.issubset(df.columns.str.lower()):
        # Try to be forgiving with capitalization
        df.columns = [c.lower() for c in df.columns]
        if not required_cols.issubset(df.columns):
            raise ValueError(
                "CSV must have columns: 'category' and 'value' (case-insensitive)."
            )
    # Ensure types
    df["category"] = df["category"].astype(str)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    return df

st.title("Pie / Donut Chart")
st.caption("Reads `data/pie_demo.csv` with ≥ 5 rows. Tip: if you actually need to compare parts, a bar chart is clearer. 😉")

# ---------- Load ----------
try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Couldn't find the CSV at `{DATA_PATH}`. Create it first.")
    st.stop()
except Exception as e:
    st.error(f"Problem reading CSV: {e}")
    st.stop()

if len(df) < 5:
    st.warning("You have fewer than 5 rows — add more data to make the pie meaningful.")
    
st.subheader("Data preview")
st.dataframe(df, use_container_width=True)

# ---------- Controls ----------
st.sidebar.header("Controls")
sort_order = st.sidebar.radio("Sort by value", ["Descending", "Ascending", "None"], index=0)
top_n = st.sidebar.slider("Show top N categories (0 = all)", min_value=0, max_value=len(df), value=min(6, len(df)))
as_donut = st.sidebar.toggle("Donut (hole)", value=True)
show_labels = st.sidebar.toggle("Show labels on slices", value=True)
normalize = st.sidebar.toggle("Normalize to 100%", value=True)

# ---------- Transform ----------
work = df.copy()

# Sort
if sort_order != "None":
    ascending = sort_order == "Ascending"
    work = work.sort_values("value", ascending=ascending)

# Top N
if top_n and top_n > 0:
    if top_n < len(work):
        head = work.head(top_n)
        tail_sum = work["value"].iloc[top_n:].sum()
        if tail_sum > 0:
            # bucket the remainder into "Other"
            head = pd.concat([head, pd.DataFrame([{"category": "Other (bucketed)", "value": tail_sum}])], ignore_index=True)
        work = head

# Normalize
if normalize and work["value"].sum() > 0:
    work["value"] = work["value"] / work["value"].sum() * 100

# ---------- Chart ----------
hole = 0.45 if as_donut else 0.0
textinfo = "percent+label" if show_labels else "none"

fig = px.pie(
    work,
    names="category",
    values="value",
    hole=hole,
)
fig.update_traces(
    textinfo=textinfo,
    hovertemplate="<b>%{label}</b><br>Value: %{value:.2f}<br>Share: %{percent}",
)
fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    legend_title_text="Category",
)

st.subheader("Chart")
st.plotly_chart(fig, use_container_width=True)

# ---------- Footnotes ----------
with st.expander("Why pies are tricky (but sometimes fine)"):
    st.markdown(
        """
- Humans estimate lengths more accurately than angles/areas — bars > pies for precise comparisons.
- If you **must** use a pie, keep categories limited and labeled. Interactivity helps.  
- Niche fact 🧠: The earliest known pie chart is credited to **William Playfair** (1801), the same pioneer behind bar and line charts.
        """
    )

