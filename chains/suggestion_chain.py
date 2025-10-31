"""
Personalized Resume Suggestion Chain
------------------------------------
Uses an LLM to generate personalized improvement tips for a candidate’s resume
based on job role, required skills, extracted resume skills, missing skills, and match score.
"""

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from models.ChatGroq import get_chatgroq


def get_personalized_suggestion_chain():
    """Returns an LLMChain that generates personalized resume suggestions."""
    llm = get_chatgroq()

    suggestion_prompt = PromptTemplate(
        input_variables=[
            "job_role",
            "required_skills",
            "resume_skills",
            "missing_skills",
            "match_score",
        ],
        template=(
            "You are an AI Career Assistant.\n"
            "Based on the following candidate data, give **personalized and practical** resume improvement suggestions.\n\n"
            "**Job Role:** {job_role}\n"
            "**Required Skills:** {required_skills}\n"
            "**Resume Skills:** {resume_skills}\n"
            "**Missing Skills:** {missing_skills}\n"
            "**Match Score:** {match_score}\n\n"
            "Your response must include:\n"
            "1. **Summary of Resume Performance**\n"
            "2. **Skills to Learn (with reasoning)**\n"
            "3. **Resume Rewriting or Formatting Suggestions**\n"
            "4. **Optional Learning Paths or Project Ideas**\n\n"
            "Respond in clean, structured **Markdown** format with clear section headings."
        ),
    )

    return LLMChain(llm=llm.as_langchain_llm(), prompt=suggestion_prompt)


def generate_suggestions(job_role, required_skills, resume_skills, missing_skills, match_score):
    """Generates personalized resume improvement suggestions."""
    chain = get_personalized_suggestion_chain()

    required_skills_text = ", ".join(required_skills) if required_skills else "None"
    resume_skills_text = ", ".join(resume_skills) if resume_skills else "None"
    missing_skills_text = ", ".join(missing_skills) if missing_skills else "None"

    inputs = {
        "job_role": job_role,
        "required_skills": required_skills_text,
        "resume_skills": resume_skills_text,
        "missing_skills": missing_skills_text,
        "match_score": f"{round(match_score * 100, 2)}%",
    }

    result = chain.invoke(inputs)

    if isinstance(result, dict) and "text" in result:
        return result["text"]
    elif isinstance(result, str):
        return result
    else:
        return "⚠️ No valid suggestions generated. Please check your input data or try again."
