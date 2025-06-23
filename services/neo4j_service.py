from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, USE_MOCK_NEO4J

def run_cypher_mock(query: str) -> list:
    """mock neo4j responses with sample data"""
    # return sample data that matches our seed.cypher structure
    if "Person" in query and "Country" in query:
        return [
            {"p.name": "Alice", "c.name": "USA"},
            {"p.name": "Bob", "c.name": "Canada"},
            {"p.name": "Charlie", "c.name": "France"}
        ]
    elif "Person" in query and "Product" in query:
        return [
            {"p.name": "Alice", "pr.name": "Laptop"},
            {"p.name": "Bob", "pr.name": "Phone"},
            {"p.name": "Charlie", "pr.name": "Coffee"}
        ]
    elif "Person" in query:
        return [
            {"p.name": "Alice"},
            {"p.name": "Bob"}, 
            {"p.name": "Charlie"}
        ]
    elif "count" in query.lower():
        return [{"count(n)": 12}]
    else:
        return [
            {"name": "Alice"},
            {"name": "USA"},
            {"name": "Laptop"}
        ]

def run_cypher_real(query: str) -> list:
    """real neo4j database query execution"""
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            with driver.session() as session:
                result = session.run(query)
                records = [dict(record) for record in result]
                return records
    except Exception as e:
        # fallback to mock on database error
        return run_cypher_mock(query)

def run_cypher(query: str) -> list:
    """main entry point - routes to mock or real based on toggle"""
    if USE_MOCK_NEO4J:
        return run_cypher_mock(query)
    else:
        return run_cypher_real(query) 