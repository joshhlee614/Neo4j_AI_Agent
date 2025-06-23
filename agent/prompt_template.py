def build_prompt(question: str) -> str:
    with open("schema.md", "r") as f:
        schema = f.read()
    
    prompt = f"""you are a cypher expert. convert natural language questions to cypher queries.

{schema}

question: {question}

return only the cypher query, no explanation."""
    
    print(f"built prompt: {prompt}")
    return prompt 