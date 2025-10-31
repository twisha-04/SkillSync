from models.ChatGroq import get_chatgroq
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def compare_skills_llm(job_description, resume_text):
    """
    Uses ChatGroq LLM to extract, compare, and return match score + missing skills.
    """
    llm = get_chatgroq(model_name="openai/gpt-oss-20b", temperature=0.3)

    prompt = PromptTemplate(
        input_variables=["job_description", "resume_text"],
        template="""
        You are an AI career assistant.
        1. Extract key required skills from this job description:
        {job_description}

        2. Extract candidate's skills from this resume:
        {resume_text}

        3. Compare both lists and compute:
            - Matched skills
            - Missing skills
            - Match score (0.0 to 1.0)

        Return structured JSON:
        {{
            "required_skills": [...],
            "resume_skills": [...],
            "matched_skills": [...],
            "missing_skills": [...],
            "match_score": 0.0
        }}
        """
    )

    chain = LLMChain(llm=llm.as_langchain_llm(), prompt=prompt)
    response = chain.invoke({
        "job_description": job_description,
        "resume_text": resume_text
    })

    try:
        return json.loads(response["text"])
    except Exception:
        return {"error": "Could not parse JSON", "raw_response": response["text"]}
