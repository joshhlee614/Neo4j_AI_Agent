from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


def run_cypher(query: str) -> list:
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            with driver.session() as session:
                result = session.run("MATCH (n) RETURN n LIMIT 3")
                records = [dict(record) for record in result]
                return records
    except Exception as e:
        return [{"dummy": "data", "status": "connection_failed"}] 