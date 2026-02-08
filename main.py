import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📋", layout="centered")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "resume_content" not in st.session_state:
    st.session_state.resume_content = None
if "jd_match_result" not in st.session_state:
    st.session_state.jd_match_result = None

st.title("AI Resume Analyzer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

job_role = st.text_input("Enter the job role you're targeting (optional)")

analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.getvalue()))
    return uploaded_file.read().decode("utf-8")

def build_export_text(include_chat=True):
    """Build plain text for export (analysis + optional chat transcript)."""
    lines = ["=== Resume Analysis ===\n", st.session_state.analysis_result]
    if include_chat and st.session_state.chat_messages:
        lines.append("\n\n=== Chat Transcript ===\n")
        for m in st.session_state.chat_messages:
            role = "You" if m["role"] == "user" else "Assistant"
            lines.append(f"{role}: {m['content']}\n")
    return "\n".join(lines)

def build_export_pdf():
    """Build PDF bytes for export (analysis + optional chat)."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    text = build_export_text(include_chat=True)
    for line in text.replace("\r", "").split("\n"):
        pdf.multi_cell(0, 6, line.encode("latin-1", errors="replace").decode("latin-1"))
    return pdf.output()

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File doesn't have any content...")
            st.stop()

        prompt = f"""Please analyze this resume and provide constructive feedback. Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}

        Resume content:
        {file_content}

        Please provide a score out of 100 for the resume
        Please provide your analysis in a clear, structured format with specific recommendations."""

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        analysis_text = response.choices[0].message.content
        st.session_state.resume_content = file_content
        st.session_state.analysis_result = analysis_text
        st.session_state.chat_messages = []
        st.session_state.jd_match_result = None

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Show analysis and chat when we have results
if st.session_state.analysis_result:
    st.markdown("### Analysis Results")
    st.markdown(st.session_state.analysis_result)

    # --- Export (TXT / PDF) ---
    st.markdown("#### Export")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download as TXT",
            data=build_export_text(include_chat=True),
            file_name="resume_analysis.txt",
            mime="text/plain",
        )
    with col2:
        try:
            pdf_bytes = build_export_pdf()
            st.download_button(
                label="Download as PDF",
                data=pdf_bytes,
                file_name="resume_analysis.pdf",
                mime="application/pdf",
            )
        except Exception:
            st.caption("PDF export may omit some special characters.")

    # --- Job description matching ---
    st.markdown("---")
    st.markdown("### Match with job description")
    st.caption("Paste a job description to see how well your resume fits and get tailored suggestions.")
    job_description = st.text_area(
        "Paste job description (optional)",
        height=120,
        placeholder="Paste the full job description here...",
        label_visibility="collapsed",
    )
    match_jd = st.button("Match resume with job description")

    if match_jd and job_description.strip():
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )
            match_prompt = f"""You are an expert recruiter. Compare this resume with the given job description and provide:

1. **Match score**: A score out of 100 with one sentence justification.
2. **Missing keywords/skills**: List important keywords or skills from the job description that are missing or weak in the resume.
3. **Tailored suggestions**: 3–5 concrete changes (bullet points) to align the resume better with this role.

Resume:
{st.session_state.resume_content}

Job description:
{job_description.strip()}

Format your response clearly with the headings above."""

            with st.spinner("Comparing resume with job description..."):
                response = client.chat.completions.create(
                    model=OPENROUTER_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert recruiter and resume advisor."},
                        {"role": "user", "content": match_prompt},
                    ],
                    temperature=0.5,
                    max_tokens=1200,
                )
            st.session_state.jd_match_result = response.choices[0].message.content
        except Exception as e:
            st.error(f"Job match failed: {str(e)}")

    if st.session_state.jd_match_result:
        st.markdown("#### Job match results")
        st.markdown(st.session_state.jd_match_result)

    st.markdown("---")
    st.markdown("### Chat with the agent")
    st.caption("Ask follow-up questions about your resume or the analysis above.")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask follow-up questions about your resume or analysis..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=OPENROUTER_API_KEY,
                )
                system_context = (
                    "You are an expert resume reviewer. You previously analyzed the user's resume. "
                    "Use the following context to answer their follow-up questions.\n\n"
                    f"Resume content:\n{st.session_state.resume_content}\n\n"
                    f"Your previous analysis:\n{st.session_state.analysis_result}"
                )
                messages_for_api = [
                    {"role": "system", "content": system_context},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages],
                ]
                response = client.chat.completions.create(
                    model=OPENROUTER_MODEL,
                    messages=messages_for_api,
                    temperature=0.7,
                    max_tokens=1000,
                )
                reply = response.choices[0].message.content
            st.markdown(reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})