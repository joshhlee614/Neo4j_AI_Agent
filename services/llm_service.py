from openai import OpenAI
from config.settings import OPENAI_API_KEY, MODEL, TEMPERATURE, USE_MOCK_LLM

# initialize openai client for real mode
client = OpenAI(api_key=OPENAI_API_KEY) if not USE_MOCK_LLM else None

def generate_cypher_mock(prompt: str) -> str:
    """mock cypher generation based on keywords"""
    prompt_lower = prompt.lower()
    
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

def generate_cypher_real(prompt: str) -> str:
    """real openai api cypher generation"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # fallback to mock on api error
        return generate_cypher_mock(prompt)

def generate_cypher(prompt: str) -> str:
    """main entry point - routes to mock or real based on toggle"""
    if USE_MOCK_LLM:
        return generate_cypher_mock(prompt)
    else:
        return generate_cypher_real(prompt) 