def build_prompt(question: str) -> str:
    with open("schema.md", "r") as f:
        schema = f.read()
    
    prompt = f"""you are a cypher expert. convert natural language questions to cypher queries.

### Schema
```
{schema}
```

### Examples

Q: Which people live in France?
A: MATCH (p:Person)-[:LIVES_IN]->(c:Country {{name: "France"}}) RETURN p.name

Q: Show me all people who buy products
A: MATCH (p:Person)-[:BUYS]->(pr:Product) RETURN p.name, pr.name

Q: How many countries are there?
A: MATCH (c:Country) RETURN count(c)

question: {question}

return only the cypher query, no explanation."""
    
    return prompt 