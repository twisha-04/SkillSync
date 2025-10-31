from Tools.wikipedia_tool import WikipediaSearchTool
from Tools.neo4j_tool import Neo4jQueryTool
from Tools.Linkedin_tool import LinkedInTool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from models.ChatGroq import get_chatgroq  # assuming your ChatGroq class is in Models/chatgroq.py


def job_role_info_chain(role_name: str):
    # Initialize LLM (Groq-based GPT-3 model)
    llm = get_chatgroq(model_name="openai/gpt-oss-20b", temperature=0.3)

    # Fetch info from tools
    wiki = WikipediaSearchTool().search(role_name)
    neo = Neo4jQueryTool().fetch_related_skills(role_name)
    linkedin = LinkedInTool().search_jobs(role_name)

    # Combine results
    combined_info = (
        f"WIKIPEDIA:\n{wiki.get('combined_text','')}\n\n"
        f"NEO4J:\n{neo}\n\n"
        f"LINKEDIN JOBS:\n{linkedin}"
    )

    # Define the summarization prompt
    prompt = PromptTemplate(
        input_variables=["role_name", "info"],
        template=(
            "You are a career intelligence assistant. Based on the following data about {role_name}, "
            "summarize its key responsibilities and list the required skills as bullet points.\n\n"
            "{info}"
        )
    )

    # Create and run chain
    llm = get_chatgroq().as_langchain_llm() 
    chain = LLMChain(llm=llm, prompt=prompt)
    summary = chain.run({"role_name": role_name, "info": combined_info})

    # Return structured output
    return {
        "title": role_name,
        "summary": summary,
        "skills_found": [s.strip("• ") for s in summary.split("\n") if s.strip().startswith("•")],
        "wiki_url": wiki.get("wiki_url")
    }
