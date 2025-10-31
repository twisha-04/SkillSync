import streamlit as st
from pathlib import Path

# Import from your modular architecture
from utils.resume import extract_text_from_pdf
from models.ChatGroq import get_chatgroq
from chains.resume_analysis import analyze_resume
from chains.job_role_info_chain import job_role_info_chain

# Streamlit Configuration
st.set_page_config(page_title="SkillSync", page_icon="🧠", layout="centered")
st.title("SkillSync — Smart Interview Prep & Career Planning Assistant")

# ----------------------------
# Step 1: Upload Resume
# ----------------------------
st.header("Step 1: Upload Your Resume")

uploaded_resume = st.file_uploader("Upload your Resume", type=["pdf", "docx", "txt"])
resume_text = ""

if uploaded_resume:
    ext = uploaded_resume.name.split(".")[-1]
    temp_path = Path(f"temp_resume.{ext}")
    with open(temp_path, "wb") as f:
        f.write(uploaded_resume.getbuffer())

    try:
        resume_text = extract_text_from_pdf(str(temp_path))
        st.success("Resume uploaded and text extracted successfully!")
    except Exception as e:
        st.error(f"Error reading resume: {e}")

    st.subheader("Extracted Resume Text:")
    st.text_area("Resume Content", resume_text, height=250)

    if st.button("Analyze Resume"):
        if not resume_text.strip():
            st.warning("Please upload a valid resume first.")
        else:
            with st.spinner("Analyzing your resume..."):
                 result = analyze_resume(resume_text)
            st.markdown(result)

# ----------------------------
# Step 2: Job Role Exploration
# ----------------------------
st.header("Step 2: Explore Job Role Requirements")

job_role = st.text_input("Enter Job Role (e.g., Data Analyst, Web Developer):")

if st.button("Analyze Job Role"):
    if not job_role.strip():
        st.warning("Please enter a job role first.")
    else:
        with st.spinner("Gathering Wikipedia, Neo4j, and LinkedIn insights..."):
             info = job_role_info_chain(job_role)

        if "error" in info:
            st.error(info["error"])
        else:
            st.subheader(f"📘 {info['title']}")
            st.write(info["summary"])

            all_skills = []

            # Collect from different data sources if available
            if info.get("skills_found"):
                all_skills.extend(info["skills_found"])
            if info.get("neo4j_skills"):
                all_skills.extend(info["neo4j_skills"])
            if info.get("linkedin_skills"):
                all_skills.extend(info["linkedin_skills"])

            # Remove duplicates (case-insensitive)
            all_skills = sorted(set([s.strip().title() for s in all_skills if s.strip()]))

            # Display skills neatly
            if all_skills:
                st.markdown("### 🧩 Key Skills Extracted from All Sources")
                st.markdown("\n".join([f"• {skill}" for skill in all_skills]))
            else:
                st.warning("No specific skills found from any source.")

            # 🔗 Wikipedia link
            if info.get("wiki_url"):
                st.markdown(f"[🔗 View full article on Wikipedia]({info['wiki_url']})")

# ----------------------------
# Step 3: Start Quiz
# ----------------------------
st.header("Step 3: Start Your Quiz")

st.markdown(
    """
    <div style="text-align:center; margin-top: 20px;">
        <a href="http://localhost:3000/" target="_blank" style="
            text-decoration: none;
            background-color: #60a5fa;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        ">Click here to Start Quiz</a>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("SkillSync © 2025 — Powered by ChatGroq + LangChain + Neo4j + Wikipedia")
