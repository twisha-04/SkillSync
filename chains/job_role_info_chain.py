from Tools.wikipedia_tool import WikipediaSearchTool
from Tools.neo4j_tool import Neo4jQueryTool
from Tools.Linkedin_tool import LinkedInTool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from models.ChatGroq import get_chatgroq


def job_role_info_chain(role_name: str):
    """
    Fetches job role insights from Wikipedia, Neo4j, and LinkedIn.
    Then summarizes and stores extracted skills in Neo4j.
    """

    # Initialize LLM (Groq-based GPT-3 model)
    llm_wrapper = get_chatgroq(model_name="openai/gpt-oss-20b", temperature=0.3)
    llm = llm_wrapper.as_langchain_llm()

    # Initialize Tools
    wiki_tool = WikipediaSearchTool()
    neo_tool = Neo4jQueryTool()
    linkedin_tool = LinkedInTool()

    # -------------------------
    # 1️⃣ Fetch Data from Sources
    # -------------------------
    wiki = wiki_tool.search(role_name)
    neo_skills = neo_tool.fetch_related_skills(role_name)
    linkedin_jobs = linkedin_tool.search_jobs(role_name)

    # -------------------------
    # 2️⃣ Combine Info
    # -------------------------
    combined_info = (
        f"WIKIPEDIA:\n{wiki.get('combined_text', '')}\n\n"
        f"NEO4J SKILLS:\n{neo_skills}\n\n"
        f"LINKEDIN JOBS:\n{linkedin_jobs}"
    )

    # -------------------------
    # 3️⃣ Summarize & Extract Skills
    # -------------------------
    prompt = PromptTemplate(
        input_variables=["role_name", "info"],
        template=(
            "You are a career intelligence assistant. Based on the following data about {role_name}, "
            "summarize its key responsibilities and list the required skills as bullet points.\n\n"
            "{info}"
        ),
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    summary = chain.run({"role_name": role_name, "info": combined_info})

    # -------------------------
    # 4️⃣ Extract Skill Lines
    # -------------------------
    skills_found = [s.strip("• ").strip() for s in summary.split("\n") if s.strip().startswith("•")]

    # -------------------------
    # 5️⃣ Store Role + Skills in Neo4j
    # -------------------------
    try:
        if skills_found:
            neo_tool.add_job_role_with_skills(role_name, skills_found)
    except Exception as e:
        print(f"[Neo4j Warning] Could not save skills for {role_name}: {e}")

    # -------------------------
    # 6️⃣ Return Structured Output
    # -------------------------
    return {
        "title": role_name,
        "summary": summary,
        "skills_found": skills_found,
        "wiki_url": wiki.get("wiki_url"),
        "neo4j_skills": neo_skills,
        "linkedin_skills": linkedin_jobs,
    }
