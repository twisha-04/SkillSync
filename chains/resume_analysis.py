import spacy
import re
from langchain.prompts import PromptTemplate
from models.ChatGroq import get_chatgroq
from Tools.neo4j_tool import Neo4jQueryTool  # ✅ Integration

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def extract_skills_from_resume(resume_text: str):
    """
    Extract technical and soft skills from a resume using NLP patterns + keyword matching.
    """
    doc = nlp(resume_text)
    skills = set()

    # Extract short, relevant noun phrases
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3 and re.search(r"[A-Za-z]", chunk.text):
            skills.add(chunk.text.strip())

    # Add keyword-based filtering
    keywords = [
        "Python", "TensorFlow", "Machine Learning", "React", "SQL", "AWS", "Docker",
        "Java", "C++", "NLP", "Deep Learning", "Data Analysis", "Communication",
        "Leadership", "Flask", "Streamlit", "Excel", "Project Management"
    ]

    for word in keywords:
        if re.search(rf"\b{word}\b", resume_text, re.IGNORECASE):
            skills.add(word)

    return sorted(skills)


def analyze_resume(resume_text: str, candidate_name: str = "Candidate_1"):
    """
    Main resume analysis function — extracts skills, stores them in Neo4j,
    and generates an AI-based summary.
    """
    llm = get_chatgroq(model_name="openai/gpt-oss-20b", temperature=0.3)
    neo = Neo4jQueryTool()

    # Step 1: Extract skills
    skills = extract_skills_from_resume(resume_text)
    skills_bullets = "\n".join([f"• {s}" for s in skills]) if skills else "• No clear skills found."

    # Step 2: Store data in Neo4j
    neo.create_candidate_node(candidate_name)
    for skill in skills:
        neo.create_skill_node(skill)
        neo.create_relationship(candidate_name, skill, "HAS_SKILL")

    # Step 3: Generate LLM summary
    prompt = PromptTemplate.from_template("""
    You are a professional resume analysis assistant.
    Summarize the candidate’s professional background in 1 paragraph,
    focusing on technical, analytical, and leadership capabilities.

    Resume Text:
    {resume_text}
    """)

    llm_input = prompt.format(resume_text=resume_text)
    summary = llm.invoke(llm_input)

    # Step 4: Return structured data
    return {
        "candidate": candidate_name,
        "summary": summary,
        "skills": skills,
        "skills_formatted": skills_bullets
    }
