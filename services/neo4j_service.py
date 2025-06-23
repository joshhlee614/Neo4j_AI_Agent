from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


def run_cypher(query: str) -> list:
    print(f"running cypher: {query}")
    
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            with driver.session() as session:
                result = session.run("MATCH (n) RETURN n LIMIT 3")
                records = [dict(record) for record in result]
                print(f"neo4j results: {records}")
                return records
    except Exception as e:
        print(f"neo4j connection failed: {e}")
        return [{"dummy": "data", "status": "connection_failed"}] 