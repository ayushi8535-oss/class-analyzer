import streamlit as st
import anthropic

st.set_page_config(page_title="Class Analyzer")
st.title("Class Analyzer")

# ---- Password gate (protects your API credit and your data) ----
password = st.text_input("Password", type="password")
if password != st.secrets["APP_PASSWORD"]:
    st.info("Enter the password to continue.")
    st.stop()

# ---- Rubric (editable on screen, starts from rubric.txt) ----
default_rubric = open("rubric.txt", encoding="utf-8").read()
rubric = st.text_area("Rubric (you can edit it here)", default_rubric, height=300)

# ---- Transcript input ----
uploaded = st.file_uploader("Upload transcript (.txt)", type=["txt"])
pasted = st.text_area("...or paste the transcript here", height=250)

transcript = ""
if uploaded is not None:
    transcript = uploaded.read().decode("utf-8", errors="ignore")
elif pasted.strip():
    transcript = pasted

if st.button("Analyze"):
    if not transcript.strip():
        st.warning("Please upload or paste a transcript first.")
        st.stop()

    prompt = f"""You are an experienced classroom observer.
Score this lesson against the rubric below.

Rules:
- Base every score ONLY on evidence in the transcript.
- For each criterion give: the score, 1-3 short quotes (with timestamps if the
  transcript has them) as evidence, a one-line reason, and one practical suggestion.
- If there is not enough evidence for a criterion, write "Insufficient evidence"
  instead of guessing.
- Pick the level whose description best matches. Do not average between levels.
- End with a short overall summary.

RUBRIC:
{rubric}

TRANSCRIPT:
{transcript}
"""

    with st.spinner("Analyzing against your rubric..."):
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

    st.markdown(response.content[0].text)