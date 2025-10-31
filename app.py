import streamlit as st
from pathlib import Path

# Import from modular architecture
from utils.resume import extract_text_from_pdf
from models.ChatGroq import get_chatgroq
from chains.resume_analysis import analyze_resume
from chains.job_role_info_chain import job_role_info_chain
from chains.suggestion_chain import generate_suggestions

# ----------------------------
# Streamlit Page Configuration
# ----------------------------
st.set_page_config(page_title="SkillSync", layout="centered")
st.title("SkillSync — Smart Interview Prep & Career Planning Assistant")

# ----------------------------
# Initialize Session State
# ----------------------------
if "resume_done" not in st.session_state:
    st.session_state.resume_done = False
if "jobrole_done" not in st.session_state:
    st.session_state.jobrole_done = False
if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []
if "required_skills" not in st.session_state:
    st.session_state.required_skills = []

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
            with st.spinner("🔍 Analyzing your resume for key skills..."):
                result = analyze_resume(resume_text)
            st.markdown(result)

            # 🔹 Extract skills from result (if available)
            if isinstance(result, dict) and "skills" in result:
                resume_skills = result["skills"]
                st.success(f"Extracted {len(resume_skills)} skills from your resume:")
                st.markdown("\n".join([f"• {s}" for s in resume_skills]))
            else:
                resume_skills = []
                st.info("Could not detect specific skills. You can manually input them if needed.")

            # Mark step complete
            st.session_state.resume_done = True
            st.session_state.resume_skills = resume_skills

# ----------------------------
# Step 2: Job Role Exploration
# ----------------------------
st.header("Step 2: Explore Job Role Requirements")

job_role = st.text_input("Enter Job Role (e.g., Data Analyst, Web Developer):")

if st.button("Analyze Job Role"):
    if not job_role.strip():
        st.warning("Please enter a job role first.")
    else:
        with st.spinner("Gathering job insights from Wikipedia, Neo4j, and LinkedIn..."):
            info = job_role_info_chain(job_role)

        if "error" in info:
            st.error(info["error"])
        else:
            st.subheader(f"📘 {info['title']}")
            st.write(info["summary"])

            all_skills = []

            # Collect from various sources
            if info.get("skills_found"):
                all_skills.extend(info["skills_found"])
            if info.get("neo4j_skills"):
                all_skills.extend(info["neo4j_skills"])
            if info.get("linkedin_skills"):
                all_skills.extend(info["linkedin_skills"])

            # Remove duplicates and normalize names
            required_skills = sorted(set([s.strip().title() for s in all_skills if s.strip()]))

            if required_skills:
                st.markdown("### Key Skills Required for this Role")
                st.markdown("\n".join([f"• {s}" for s in required_skills]))
            else:
                st.warning("No specific skills found from any source.")

            if info.get("wiki_url"):
                st.markdown(f"[🔗 View full article on Wikipedia]({info['wiki_url']})")

            #  Mark step complete
            st.session_state.jobrole_done = True
            st.session_state.required_skills = required_skills

# ----------------------------
# Step 3: Personalized Suggestions
# ----------------------------
st.header("Step 3: Personalized Resume Suggestions")

if st.session_state.resume_done and st.session_state.jobrole_done:
    resume_skills = st.session_state.resume_skills
    required_skills = st.session_state.required_skills
    job_role = job_role or "Your Selected Role"

    # 🔹 Calculate missing skills
    missing_skills = [s for s in required_skills if s not in [r.title() for r in resume_skills]]
    match_score = 1 - (len(missing_skills) / len(required_skills)) if required_skills else 0

    st.success("Both resume and job role analysis are complete!")
    st.write(f"**Match Score:** {round(match_score * 100, 1)}%")
    st.markdown("**Missing Skills:** " + (", ".join(missing_skills) if missing_skills else "None 🎉"))

    with st.spinner("Generating personalized improvement suggestions..."):
        suggestions = generate_suggestions(
            job_role=job_role,
            required_skills=required_skills,
            resume_skills=resume_skills,
            missing_skills=missing_skills,
            match_score=match_score
        )
        st.markdown(suggestions)

else:
    st.info("⬆Please complete **Step 1 (Resume Analysis)** and **Step 2 (Job Role Analysis)** first.")

# ----------------------------
# Step 4: Start Quiz
# ----------------------------
st.header("Step 4: Start Your Quiz")

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
