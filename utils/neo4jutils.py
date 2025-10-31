from neo4j import GraphDatabase
import os

class Neo4jConnection:
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        if self.driver:
            self.driver.close()

    def query(self, query, params=None):
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

# Example usage
# neo = Neo4jConnection()
# results = neo.query("MATCH (n:Skill) RETURN n.name LIMIT 5")
# print(results)
