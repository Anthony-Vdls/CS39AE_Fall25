import streamlit as st

st.title("👋 My Bio")

# ---------- TODO: Replace with your own info ----------
NAME = "Anthony Vidales"
PROGRAM = "Computer Science"
INTRO = (
    "I am a computer science, math, and philosophy enthusiast."
    "I enjoy these topics becuase the formal sciences applies to many real word scenarios."
    "Currently using learned theroy to build interactive machine learning models and cool visualizations on a web page!"
)
FUN_FACTS = [
    "I love growing plants both in and out doors.",
    "I’m learning and loving data analytics.",
    "I want to build a online tool that helps plant owners care for there plants."
]
PHOTO_PATH = "assets/your_photo.jpg"  # Put a file in repo root or set a URL

# ---------- Layout ----------
col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    try:
        st.image(PHOTO_PATH, caption=NAME, use_container_width=True)
    except Exception:
        st.info("Add a photo named `your_photo.jpg` to the repo root, or change PHOTO_PATH.")
with col2:
    st.subheader(NAME)
    st.write(PROGRAM)
    st.write(INTRO)

st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
    st.write(f"- {f}")

st.divider()
st.caption("Edit `pages/1_Bio.py` to customize this page.")
