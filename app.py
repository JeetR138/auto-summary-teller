# app.py
import streamlit as st
from utils import get_summarizer, extract_text, chunk_text

st.set_page_config(page_title="🧠 Auto Summary Teller 2.0", layout="wide", page_icon="🧠")

with st.sidebar:
    st.title("⚙️ Settings")
    summary_len = st.slider("Target summary length (approx. sentences)", min_value=1, max_value=10, value=3)
    show_chunks = st.toggle("Preview chunk-by-chunk summaries", value=False)
    st.markdown("---")
    st.caption("Built by Jeet Rathod")

st.title("🧠 Auto Summary Teller")
st.write("Paste text **or** upload a file — PDF, DOCX, or plain text — and get a concise AI-generated summary.")

tab_paste, tab_upload = st.tabs(["🔤 Paste Text", "📂 Upload File"])

input_text = ""
uploaded_file = None

with tab_paste:
    input_text = st.text_area("Enter / paste your text here:", height=300)

with tab_upload:
    uploaded_file = st.file_uploader("Choose a PDF, DOCX, or TXT file:", type=["pdf", "docx", "txt"])

if st.button("🚀 Summarize"):
    raw_text = ""
    if uploaded_file is not None:
        raw_text = extract_text(uploaded_file.read(), uploaded_file.name)
    elif input_text.strip():
        raw_text = input_text
    else:
        st.warning("Please paste text or upload a file first.")
        st.stop()

    st.info(f"**Characters loaded:** {len(raw_text):,}")
    summarizer = get_summarizer()
    chunks = chunk_text(raw_text)
    all_summaries = []

    progress = st.progress(0, text="Summarizing…")
    for i, chunk in enumerate(chunks, start=1):
        part = summarizer(chunk, max_length=summary_len * 40, min_length=summary_len * 15, do_sample=False)[0]["summary_text"]
        all_summaries.append(part)
        progress.progress(i / len(chunks), text=f"Chunk {i}/{len(chunks)} done")

        if show_chunks:
            with st.expander(f"Chunk {i} summary"):
                st.write(part)

    progress.empty()

    final_summary = all_summaries[0] if len(all_summaries) == 1 else summarizer(" ".join(all_summaries),
                        max_length=summary_len * 40, min_length=summary_len * 15, do_sample=False)[0]["summary_text"]

    st.success("### 📝 Final Summary")
    st.write(final_summary)
    st.download_button("💾 Download summary as .txt", data=final_summary, file_name="summary.txt", mime="text/plain")