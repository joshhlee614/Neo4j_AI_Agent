def build_prompt(question: str) -> str:
    with open("schema.md", "r") as f:
        schema = f.read()
    
    prompt = f"""you are a cypher expert. convert natural language questions to cypher queries.

CRITICAL SAFETY RULES:
- ONLY generate READ-ONLY queries using MATCH, RETURN, WHERE, ORDER BY, LIMIT, COUNT, etc.
- NEVER generate destructive operations: DELETE, DROP, CREATE, MERGE, SET, REMOVE, DETACH
- If asked to modify/delete/create data, respond with: "I can only read data, not modify it"
- Always return a complete, valid Cypher query that includes a RETURN clause
- Use proper variable names, never use anonymous nodes () in RETURN statements

### Schema
```
{schema}
```

### Examples

Q: Which assets are similar to each other?
A: MATCH (a1:Asset)-[:SIMILAR]->(a2:Asset) RETURN a1.id, a2.id LIMIT 10

Q: Show me assets and their prices on specific dates
A: MATCH (a:Asset)-[:HAS_PRICE]->(d:Date) RETURN a.id, a.type, d.date LIMIT 10

Q: Show me things from 1993 or assets with prices in 1993
A: MATCH (a:Asset)-[:HAS_PRICE]->(d:Date) WHERE d.date CONTAINS '1993' RETURN a.id, a.type, d.date LIMIT 10

Q: How many countries have macro indicators?
A: MATCH (c:Country)-[:HAS_INDICATOR]->(:Year) RETURN count(DISTINCT c)

Q: Show me macro indicators for a specific year
A: MATCH (c:Country)-[:HAS_INDICATOR]->(y:Year) WHERE y.year = 2020 RETURN c.name, y.year LIMIT 10

Q: What are all the relationship types present?
A: MATCH (n)-[r]->(m) RETURN DISTINCT type(r) AS relationship_type

Q: What are all the relationship nodes present?
A: MATCH (n)-[r]->(m) RETURN DISTINCT labels(n) AS from_node, type(r) AS relationship, labels(m) AS to_node LIMIT 20

Q: Show me all types of relationships and their counts
A: MATCH (n)-[r]->(m) RETURN type(r) AS relationship_type, count(r) AS count ORDER BY count DESC

Q: Delete all nodes
A: I can only read data, not modify it

Q: Create a new asset
A: I can only read data, not modify it

question: {question}

return only the cypher query, no explanation. the query must be complete and include a RETURN clause."""
    
    return prompt 