from config.settings import OPENAI_API_KEY, MODEL, TEMPERATURE

def generate_cypher(prompt: str) -> str:
    prompt_lower = prompt.lower()
    
    # smarter mock responses based on keywords
    if "all people" in prompt_lower or "show people" in prompt_lower:
        return "MATCH (p:Person) RETURN p.name"
    elif "country" in prompt_lower and "live" in prompt_lower:
        return "MATCH (p:Person)-[:LIVES_IN]->(c:Country) RETURN p.name, c.name"
    elif "buy" in prompt_lower or "product" in prompt_lower:
        return "MATCH (p:Person)-[:BUYS]->(pr:Product) RETURN p.name, pr.name"
    elif "count" in prompt_lower:
        return "MATCH (n) RETURN count(n)"
    else:
        return "MATCH (n) RETURN n LIMIT 10" 