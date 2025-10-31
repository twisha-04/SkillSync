# utils/neo4jutils.py

from neo4j import GraphDatabase
import os


class Neo4jConnection:
    """
    Handles all Neo4j operations — connection, queries, and helper methods
    for adding candidates, job roles, and comparing skills.
    Fully compatible with Neo4j Aura Cloud instance.
    """

    def __init__(self, uri=None, user=None, password=None):
        # Use cloud connection by default
        self.uri = uri or os.getenv("NEO4J_URI", "neo4j+s://7586518c.databases.neo4j.io")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv(
            "NEO4J_PASSWORD",
            "N-S-f5vww6Hg91iI3aANYb5rRRUa5sm9LFVV00Kbyjo"
        )

        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("✅ Connected to Neo4j Aura successfully.")
        except Exception as e:
            print(f"❌ Neo4j connection error: {e}")
            self.driver = None

    # -------------------------------------------------------------------------
    # Basic Operations
    # -------------------------------------------------------------------------
    def close(self):
        if self.driver:
            self.driver.close()

    def query(self, query, parameters=None):
        """Execute any Cypher query and return result as list of dicts."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    # -------------------------------------------------------------------------
    # Create / Update Job Role
    # -------------------------------------------------------------------------
    def add_job_role(self, role_name, skills):
        """Create a job role and link required skills."""
        with self.driver.session() as session:
            session.execute_write(self._add_job_role_tx, role_name, skills)

    @staticmethod
    def _add_job_role_tx(tx, role_name, skills):
        tx.run("""
            MERGE (j:JobRole {name: $role_name})
            WITH j
            UNWIND $skills AS skill
            MERGE (s:Skill {name: skill})
            MERGE (j)-[:REQUIRES]->(s)
        """, role_name=role_name, skills=skills)

    # -------------------------------------------------------------------------
    # Create / Update Candidate Resume
    # -------------------------------------------------------------------------
    def add_candidate(self, candidate_name, email=None, skills=None):
        """Creates or updates a candidate and links their skills."""
        with self.driver.session() as session:
            session.run("""
                MERGE (c:Candidate {name: $candidate_name})
                ON CREATE SET c.email = $email, c.created_at = datetime()
                ON MATCH SET c.last_updated = datetime()
            """, candidate_name=candidate_name, email=email)

            if skills:
                session.run("""
                    MATCH (c:Candidate {name: $candidate_name})
                    UNWIND $skills AS skill
                    MERGE (s:Skill {name: skill})
                    MERGE (c)-[:HAS_SKILL]->(s)
                """, candidate_name=candidate_name, skills=skills)

    # -------------------------------------------------------------------------
    # Relationship Management
    # -------------------------------------------------------------------------
    def link_candidate_to_jobrole(self, candidate_name, role_name):
        """Links candidate to job role."""
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Candidate {name: $candidate_name}),
                      (j:JobRole {name: $role_name})
                MERGE (c)-[:INTERESTED_IN]->(j)
            """, candidate_name=candidate_name, role_name=role_name)

    # -------------------------------------------------------------------------
    # Fetch / Analysis
    # -------------------------------------------------------------------------
    def fetch_jobrole_skills(self, role_name):
        """Fetch all required skills for a specific job role."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (j:JobRole {name: $role_name})-[:REQUIRES]->(s:Skill)
                RETURN collect(DISTINCT s.name) AS skills
            """, role_name=role_name)
            record = result.single()
            return record["skills"] if record else []

    def compare_candidate_to_jobrole(self, candidate_name, role_name):
        """Compares candidate’s skills with job role requirements."""
        with self.driver.session() as session:
            query = """
            MATCH (c:Candidate {name: $candidate_name})-[:HAS_SKILL]->(s:Skill),
                  (j:JobRole {name: $role_name})-[:REQUIRES]->(s2:Skill)
            WITH collect(DISTINCT s.name) AS candidate_skills,
                 collect(DISTINCT s2.name) AS role_skills
            RETURN apoc.coll.intersection(candidate_skills, role_skills) AS matched,
                   apoc.coll.subtract(role_skills, candidate_skills) AS missing,
                   apoc.coll.subtract(candidate_skills, role_skills) AS extras
            """
            result = session.run(query, candidate_name=candidate_name, role_name=role_name)
            return result.single()
