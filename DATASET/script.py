from neo4j import GraphDatabase
import json

# ----------------------------
# Configuration
# ----------------------------
NEO4J_URI = "neo4j+s://7586518c.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "N-S-f5vww6Hg91iI3aANYb5rRRUa5sm9LFVV00Kbyjo"
JSON_FILE = r"C:\SkillSync\DATASET\dataset.json"  # Path to your JSON file

# ----------------------------
# Connect to Neo4j
# ----------------------------
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ----------------------------
# Load JSON
# ----------------------------
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# ----------------------------
# Function to create JobRole nodes and relationships
# ----------------------------
def create_jobrole(tx, job):
    # Create JobRole node
    tx.run(
        "MERGE (j:JobRole {name: $job_role})",
        job_role=job['job_role']
    )
    
    # Create ITSkill nodes and relationships
    for skill in job['it_skills']:
        tx.run(
            """
            MERGE (s:ITSkill {name: $skill})
            WITH s
            MATCH (j:JobRole {name: $job_role})
            MERGE (j)-[:HAS_IT_SKILL]->(s)
            """,
            skill=skill,
            job_role=job['job_role']
        )
    
    # Create SoftSkill nodes and relationships
    for skill in job['soft_skills']:
        tx.run(
            """
            MERGE (s:SoftSkill {name: $skill})
            WITH s
            MATCH (j:JobRole {name: $job_role})
            MERGE (j)-[:HAS_SOFT_SKILL]->(s)
            """,
            skill=skill,
            job_role=job['job_role']
        )

# ----------------------------
# Execute
# ----------------------------
with driver.session() as session:
    for job in data:
        session.execute_write(create_jobrole, job)

driver.close()
print("Job roles and skills created successfully!")
