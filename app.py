"""Flashcard Generator - Streamlit UI (PS22).
Run:  streamlit run app.py
"""
import streamlit as st

from llm import generate_flashcards

st.set_page_config(page_title="Flashcard Generator", page_icon="🗂️", layout="wide")
st.title("Flashcard Generator")
st.caption("Paste your notes → get Q&A flashcards → download as CSV.")

with st.sidebar:
    st.header("Settings")
    num_cards = st.slider("Number of flashcards", 3, 20, 8)
    difficulty = st.select_slider("Difficulty", ["easy", "medium", "hard"], value="medium")
    st.markdown("---")
    st.markdown("Powered by Groq (Llama 3.3).")

SAMPLE = (
    "Photosynthesis is the process by which green plants convert light energy into chemical energy. "
    "It occurs in chloroplasts, which contain chlorophyll. The overall equation is 6CO2 + 6H2O + light "
    "-> C6H12O6 + 6O2. The light reactions occur in the thylakoid membranes and produce ATP and NADPH. "
    "The Calvin cycle occurs in the stroma and uses ATP and NADPH to fix CO2 into glucose."
)

if "notes" not in st.session_state:
    st.session_state.notes = ""

if st.button("Load sample notes"):
    st.session_state.notes = SAMPLE

notes = st.text_area("Paste your notes here", key="notes", height=250,
                     placeholder="Paste lecture notes, a textbook paragraph, etc.")

if st.button("Generate flashcards", type="primary"):
    with st.spinner("Generating flashcards..."):
        try:
            st.session_state.df = generate_flashcards(notes, num_cards, difficulty)
        except Exception as e: 
            st.session_state.pop("df", None)
            st.error(f"Could not generate flashcards: {e}")

df = st.session_state.get("df")
if df is not None:
    st.success(f"Generated {len(df)} flashcards.")

    tab_cards, tab_table = st.tabs(["Cards", "Table"])

    with tab_cards:
        cols = st.columns(2)
        for i, row in df.iterrows():
            with cols[(i - 1) % 2]:
                with st.container(border=True):
                    st.markdown(f"**Q{i}. {row['Question']}**")
                    with st.expander("Show answer"):
                        st.write(row["Answer"])

    with tab_table:
        st.dataframe(df, use_container_width=True)

    csv_data = df.to_csv(index=False).encode("utf-8-sig")  # utf-8-sig so Excel opens it correctly
    st.download_button("⬇️ Download CSV", data=csv_data, file_name="flashcards.csv", mime="text/csv")