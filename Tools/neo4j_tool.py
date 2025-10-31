from langchain.tools import BaseTool
from utils.neo4jutils import Neo4jConnection

class Neo4jQueryTool(BaseTool):
    name: str = "Neo4j Knowledge Graph Search"
    description: str = (
        "Use this tool to query information from the Neo4j database. "
        "Provide a Cypher query as input and it will return the matching records."
    )

    def _run(self, query: str):
        """Generic query runner."""
        try:
            conn = Neo4jConnection()
            results = conn.query(query)
            conn.close()
            return results if results else "No results found."
        except Exception as e:
            return f"Neo4j query error: {e}"

    async def _arun(self, query: str):
        raise NotImplementedError("Async not implemented for Neo4jQueryTool.")

    # Custom helper: Fetch related skills for a given job role
    def fetch_related_skills(self, role_name: str):
        """
        Fetch IT and soft skills related to a given job role.
        Expects nodes:
          (:jobrole {name: ...})
          (:itskill {name: ...})
          (:softskill {name: ...})
        and relationships:
          (:jobrole)-[:has_it_skill]->(:itskill)
          (:jobrole)-[:has_soft_skill]->(:softskill)
        """
        try:
            conn = Neo4jConnection()

            query = f"""
            MATCH (r:jobrole {{name: '{role_name}'}})
            OPTIONAL MATCH (r)-[:has_it_skill]->(i:itskill)
            OPTIONAL MATCH (r)-[:has_soft_skill]->(s:softskill)
            RETURN r.name AS job_role,
                   collect(DISTINCT i.name) AS it_skills,
                   collect(DISTINCT s.name) AS soft_skills
            """

            results = conn.query(query)
            conn.close()

            if not results:
                return f"No related skills found for job role '{role_name}'."

            data = results[0]
            it_skills = data.get("it_skills", [])
            soft_skills = data.get("soft_skills", [])

            formatted_output = (
                f"Job Role: {role_name}\n"
                f"IT Skills: {', '.join(it_skills) if it_skills else 'None'}\n"
                f"Soft Skills: {', '.join(soft_skills) if soft_skills else 'None'}"
            )

            return formatted_output

        except Exception as e:
            return f"Neo4j skill fetch error: {e}"
