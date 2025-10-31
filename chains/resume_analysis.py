import spacy
import re
from langchain.prompts import PromptTemplate
from models.ChatGroq import get_chatgroq  # ✅ Correct import

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


def analyze_resume(resume_text: str):
    """
    Main resume analysis function — extracts skills + generates summary using ChatGroq.
    """
    # llm = get_chatgroq(model_name="gpt-4o-mini", temperature=0.3)
    llm = get_chatgroq(model_name="openai/gpt-oss-20b", temperature=0.3)

    # NLP skill extraction
    skills = extract_skills_from_resume(resume_text)
    skills_bullets = "\n".join([f"• {s}" for s in skills]) if skills else "• No clear skills found."

    # Prompt for LLM
    prompt = PromptTemplate.from_template("""
    You are a professional resume analysis assistant.
    Summarize the candidate’s professional background in 1 paragraph,
    and list the main skill areas mentioned in the resume.
    
    Resume Text:
    {resume_text}
    """)

    llm_input = prompt.format(resume_text=resume_text)
    summary = llm.invoke(llm_input)

    return f"### Resume Summary\n{summary}\n\n### Identified Skills\n{skills_bullets}"