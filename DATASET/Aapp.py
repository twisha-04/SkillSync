import json
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY") # 🔑 Replace with your key
MODEL_NAME = "llama-3.3-70b-versatile"    # ✅ Supported model


llm = ChatGroq(model=MODEL_NAME, groq_api_key=GROQ_API_KEY)

# -------------------------------
# 1️⃣ JOB ROLE → REQUIRED SKILLS
# -------------------------------
job_prompt = PromptTemplate(
    input_variables=[],
    template="""
Generate a JSON dataset mapping job roles to required skills in this format:

[
  {{
    "id": 1,
    "job_role": "Data Scientist",
    "steps": [
      "Step 1: Identify domain → Data Science",
      "Step 2: Analyze tasks → data analysis, modeling, visualization",
      "Step 3: Derive technical stack",
      "Step 4: Finalize key skills list"
    ],
    "derived_skills": ["Python", "Machine Learning", "SQL", "Statistics", "Data Visualization"]
  }}
]

Include 5 diverse job roles (Data Scientist, Frontend Developer, Backend Developer, UI/UX Designer, DevOps Engineer).
Ensure valid JSON output.
"""
)
job_chain = LLMChain(llm=llm, prompt=job_prompt)
job_data = job_chain.invoke({})

with open("job_to_skills.json", "w", encoding="utf-8") as f:
    json.dump(job_data, f, indent=4, ensure_ascii=False)
print("✅ job_to_skills.json generated.")

# -------------------------------
# 2️⃣ RESUME → EXTRACTED SKILLS
# -------------------------------
resume_prompt = PromptTemplate(
    input_variables=[],
    template="""
Generate a JSON dataset mapping resume text to extracted skills:

[
  {{
    "id": 1,
    "resume_text": "Experienced Python developer skilled in Django, MySQL, and REST APIs...",
    "steps": [
      "Step 1: Identify technical keywords",
      "Step 2: Filter duplicates",
      "Step 3: Extract final skill set"
    ],
    "extracted_skills": ["Python", "Django", "MySQL", "REST APIs", "AWS"]
  }}
]

Include 5 unique resumes across domains (Web, ML, Data, Cloud, UI).
Ensure valid JSON output.
"""
)
resume_chain = LLMChain(llm=llm, prompt=resume_prompt)
resume_data = resume_chain.invoke({})

with open("resume_to_skills.json", "w", encoding="utf-8") as f:
    json.dump(resume_data, f, indent=4, ensure_ascii=False)
print("✅ resume_to_skills.json generated.")

# -------------------------------
# 3️⃣ JOB ROLE + RESUME → MATCH SCORE
# -------------------------------
match_prompt = PromptTemplate(
    input_variables=[],
    template="""
Generate a JSON dataset showing job role, resume, reasoning steps, required and extracted skills, matched skills, missing skills, and match score:

[
  {{
    "id": 1,
    "job_role": "Data Analyst",
    "resume_text": "Strong in SQL, Excel, Python, and Power BI.",
    "steps": [
      "Step 1: Identify target role",
      "Step 2: Retrieve required skills",
      "Step 3: Extract resume skills",
      "Step 4: Compare overlap and missing skills",
      "Step 5: Compute match score"
    ],
    "required_skills": ["SQL", "Excel", "Python", "Power BI", "Statistics"],
    "resume_skills": ["SQL", "Excel", "Python", "Power BI"],
    "matched_skills": ["SQL", "Excel", "Python", "Power BI"],
    "missing_skills": ["Statistics"],
    "match_score": 0.8
  }}
]

Include 3 examples across roles like Data Analyst, Backend Developer, Cloud Engineer.
Ensure valid JSON output.
"""
)
match_chain = LLMChain(llm=llm, prompt=match_prompt)
match_data = match_chain.invoke({})

with open("job_resume_match.json", "w", encoding="utf-8") as f:
    json.dump(match_data, f, indent=4, ensure_ascii=False)
print("✅ job_resume_match.json generated.")
