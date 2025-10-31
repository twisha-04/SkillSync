from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from models.ChatGroq import get_chatgroq
import json

def extract_skills_llm(resume_text):
    """
    Uses the ChatGroq LLM directly to extract skills (both known and OOV)
    from resume text, handling free-form or dictionary-style input.
    """
    llm = get_chatgroq(model_name="openai/gpt-oss-20b", temperature=0.2)

    prompt = PromptTemplate(
        input_variables=["resume_text"],
        template="""
        You are an AI resume analyzer.
        Analyze the following text and extract all **technical, soft, and domain-specific skills**.
        Include both known and emerging (OOV) technologies, frameworks, or tools.

        Resume Text:
        {resume_text}

        Return a valid JSON object in this format:
        {{
            "skills": [
                "Python", "TensorFlow", "LangChain", "Docker", "Communication"
            ]
        }}
        """
    )

    chain = LLMChain(llm=llm.as_langchain_llm(), prompt=prompt)
    response = chain.invoke({"resume_text": resume_text})

    # Parse structured output safely
    try:
        result = json.loads(response["text"])
        return result.get("skills", [])
    except Exception:
        # fallback: extract bullet points or comma-separated items
        return [s.strip("•, ") for s in response["text"].split("\n") if s.strip()]
