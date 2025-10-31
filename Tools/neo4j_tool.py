from langchain.tools import BaseTool
from utils.neo4jutils import Neo4jConnection
from typing import Optional

class Neo4jQueryTool(BaseTool):
    """
    Tool for managing and querying Neo4j AuraDB.
    Supports candidate/jobrole/skill creation, linking, and skill comparison.
    """

    name: str = "Neo4j Knowledge Graph Tool"
    description: str = (
        "Tool to manage and query skills, candidates, and job roles in Neo4j AuraDB. "
        "Supports creation, linking, and skill comparison between candidates and job roles."
    )
    conn: Optional[Neo4jConnection] = None
    # -------------------------------------------------------------------------
    # Initialize a persistent connection
    # -------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.conn = Neo4jConnection()  # ✅ Create once, reused for all operations

    # -------------------------------------------------------------------------
    # Core Query Execution
    # -------------------------------------------------------------------------
    def _run(self, query: str):
        """Execute a raw Cypher query directly on the Neo4j AuraDB."""
        try:
            results = self.conn.query(query)
            return results or "⚠️ No results found for the given query."
        except Exception as e:
            return f"❌ Neo4j query execution failed: {str(e)}"

    async def _arun(self, query: str):
        raise NotImplementedError("Async query execution not supported yet.")

    # -------------------------------------------------------------------------
    # Node Creation Helpers
    # -------------------------------------------------------------------------
    def create_candidate_node(self, candidate_name: str, email: str = None, skills: list = None):
        """Creates a Candidate node and links it with its skills."""
        try:
            self.conn.add_candidate(candidate_name, email, skills)
            return f"✅ Candidate '{candidate_name}' created with {len(skills or [])} skills."
        except Exception as e:
            return f"❌ Failed to create candidate node: {e}"

    def create_jobrole_node(self, role_name: str, skills: list = None):
        """Creates a JobRole node and its required skills."""
        try:
            self.conn.add_job_role(role_name, skills or [])
            return f"✅ JobRole '{role_name}' created with {len(skills or [])} skills."
        except Exception as e:
            return f"❌ Failed to create job role node: {e}"

    # -------------------------------------------------------------------------
    # Skill Management
    # -------------------------------------------------------------------------
    def create_skill_node(self, skill_name: str, skill_type: str = None):
        """Create or update a single Skill node."""
        try:
            query = """
            MERGE (s:Skill {name: $skill_name})
            ON CREATE SET s.type = $skill_type, s.created_at = datetime()
            ON MATCH SET s.last_updated = datetime()
            RETURN s.name AS name, s.type AS type
            """
            result = self.conn.query(query, {"skill_name": skill_name, "skill_type": skill_type})
            if result:
                return {"status": "ok", "skill": result[0]}
            return {"status": "ok", "skill": {"name": skill_name, "type": skill_type}}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_skill_nodes(self, skills: list):
        """Bulk-create multiple Skill nodes efficiently using UNWIND."""
        try:
            normalized = []
            for s in skills:
                if isinstance(s, dict):
                    normalized.append({"name": s.get("name"), "type": s.get("type")})
                else:
                    normalized.append({"name": s, "type": None})

            query = """
            UNWIND $skills AS skill
            MERGE (s:Skill {name: skill.name})
            ON CREATE SET s.type = skill.type, s.created_at = datetime()
            ON MATCH SET s.last_updated = datetime()
            RETURN collect({name:s.name, type:s.type}) AS created
            """
            result = self.conn.query(query, {"skills": normalized})
            return {"status": "ok", "created": result[0].get("created", []) if result else []}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # -------------------------------------------------------------------------
    # General Relationship Creation
    # -------------------------------------------------------------------------
    def create_relationship(self, *args):
        """
        Create a relationship between two nodes.

        Examples:
          create_relationship("Candidate", "Alice", "HAS_SKILL", "Skill", "Python")
          create_relationship("Alice", "Python", "HAS_SKILL")
        """
        try:
            if len(args) == 5:
                node1_label, node1_name, relation, node2_label, node2_name = args
            elif len(args) == 3:
                node1_label, node1_name = "Candidate", args[0]
                relation = args[2]
                node2_label, node2_name = "Skill", args[1]
            else:
                return {"status": "error", "message": "Invalid parameters. Expected 3 or 5 args."}

            query = f"""
            MATCH (a:{node1_label} {{name: $node1_name}})
            MATCH (b:{node2_label} {{name: $node2_name}})
            MERGE (a)-[r:{relation}]->(b)
            RETURN type(r) AS relationship
            """
            result = self.conn.query(query, {"node1_name": node1_name, "node2_name": node2_name})
            if result:
                return {"status": "ok", "relationship": result[0]["relationship"]}
            return {"status": "ok", "relationship": relation}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # -------------------------------------------------------------------------
    # Specific Relationship Helpers
    # -------------------------------------------------------------------------
    def link_candidate_to_skill(self, candidate_name: str, skill_name: str):
        """Creates a HAS_SKILL relationship between Candidate and Skill."""
        return self.create_relationship("Candidate", candidate_name, "HAS_SKILL", "Skill", skill_name)

    def link_jobrole_to_skill(self, role_name: str, skill_name: str):
        """Creates a REQUIRES_SKILL relationship between JobRole and Skill."""
        return self.create_relationship("JobRole", role_name, "REQUIRES_SKILL", "Skill", skill_name)

    def link_candidate_to_jobrole(self, candidate_name: str, role_name: str):
        """Creates an INTERESTED_IN relationship between Candidate and JobRole."""
        return self.create_relationship("Candidate", candidate_name, "INTERESTED_IN", "JobRole", role_name)

        # -------------------------------------------------------------------------
    # Fetch Related Skills
    # -------------------------------------------------------------------------
    def fetch_related_skills(self, entity_name: str, entity_type: str = "Candidate"):
        """
        Fetch all skills connected to a given Candidate or JobRole node.
        entity_type can be 'Candidate' or 'JobRole'.
        """
        try:
            if entity_type not in ["Candidate", "JobRole"]:
                return {"status": "error", "message": "entity_type must be 'Candidate' or 'JobRole'."}

            relation = "HAS_SKILL" if entity_type == "Candidate" else "REQUIRES_SKILL"

            query = f"""
            MATCH (e:{entity_type} {{name: $entity_name}})-[:{relation}]->(s:Skill)
            RETURN collect(s.name) AS skills
            """
            result = self.conn.query(query, {"entity_name": entity_name})
            if result and result[0].get("skills"):
                return {"status": "ok", "skills": result[0]["skills"]}
            return {"status": "ok", "skills": []}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # -------------------------------------------------------------------------
    # Skill Comparison
    # -------------------------------------------------------------------------
    def compare_candidate_to_jobrole(self, candidate_name: str, role_name: str):
        """Compare Candidate skills vs JobRole requirements."""
        try:
            result = self.conn.compare_candidate_to_jobrole(candidate_name, role_name)
            if not result:
                return "⚠️ No matching data found."
            matched = result.get("matched", [])
            missing = result.get("missing", [])
            extras = result.get("extras", [])
            return {
                "matched_skills": matched,
                "missing_skills": missing,
                "extra_skills": extras
            }
        except Exception as e:
            return f"❌ Failed to compare candidate and job role: {e}"

    # -------------------------------------------------------------------------
    # Close Connection
    # -------------------------------------------------------------------------
    def close(self):
        """Gracefully close Neo4j connection."""
        if self.conn:
            self.conn.close()
            print("🔌 Neo4j connection closed.")
