from openai import OpenAI
from config.settings import OPENAI_API_KEY, MODEL, TEMPERATURE, USE_MOCK_LLM
import re

# initialize openai client for real mode with proper validation
client = None
if not USE_MOCK_LLM and OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-..."):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        client = None

def is_safe_query(query: str) -> bool:
    """check if query is read-only and safe to execute"""
    query_upper = query.upper().strip()
    
    # list of destructive operations that should be blocked
    destructive_keywords = [
        'DELETE', 'DROP', 'CREATE', 'MERGE', 'SET', 'REMOVE', 'DETACH',
        'ALTER', 'INSERT', 'UPDATE', 'TRUNCATE'
    ]
    
    # check if query contains destructive keywords as whole words
    for keyword in destructive_keywords:
        # use word boundary regex to match whole words only
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, query_upper):
            return False
    
    return True

def generate_cypher_mock(prompt: str) -> str:
    """mock cypher generation based on keywords"""
    prompt_lower = prompt.lower()
    
    # check for destructive operations first
    if any(word in prompt_lower for word in ['delete', 'drop', 'create', 'remove', 'destroy']):
        return "I can only read data, not modify it"
    
    # check specific queries first
    if "france" in prompt_lower and ("live" in prompt_lower or "who" in prompt_lower):
        return "MATCH (p:Person)-[:LIVES_IN]->(c:Country {name: 'France'}) RETURN p.name"
    elif "count" in prompt_lower:
        return "MATCH (n) RETURN count(n)"  
    elif "buy" in prompt_lower or "product" in prompt_lower:
        return "MATCH (p:Person)-[:BUYS]->(pr:Product) RETURN p.name, pr.name"
    elif "country" in prompt_lower and "live" in prompt_lower:
        return "MATCH (p:Person)-[:LIVES_IN]->(c:Country) RETURN p.name, c.name"
    elif "all people" in prompt_lower or "show people" in prompt_lower:
        return "MATCH (p:Person) RETURN p.name"
    else:
        return "MATCH (n) RETURN n LIMIT 10"

def extract_cypher_from_response(response_text: str) -> str:
    """extract cypher query from llm response, handling code blocks and extra text"""
    # look for cypher in code blocks first
    cypher_match = re.search(r'```(?:cypher)?\s*(.*?)\s*```', response_text, re.DOTALL | re.IGNORECASE)
    if cypher_match:
        return cypher_match.group(1).strip()
    
    # look for complete cypher query (multi-line)
    lines = response_text.split('\n')
    cypher_lines = []
    in_cypher = False
    
    for line in lines:
        line = line.strip()
        # start collecting when we see a cypher keyword
        if line.upper().startswith(('MATCH', 'CREATE', 'MERGE', 'DELETE', 'SET', 'REMOVE')):
            in_cypher = True
            cypher_lines = [line]
        elif in_cypher and line:
            # continue collecting lines that are part of the query
            if line.upper().startswith(('WHERE', 'WITH', 'RETURN', 'ORDER', 'LIMIT', 'SKIP', 'AND', 'OR')):
                cypher_lines.append(line)
            elif line.upper().startswith(('MATCH', 'CREATE', 'MERGE', 'DELETE', 'SET', 'REMOVE')):
                # new query started, reset
                cypher_lines = [line]
            else:
                # end of query
                break
        elif in_cypher and not line:
            # empty line might indicate end of query
            break
    
    if cypher_lines:
        return ' '.join(cypher_lines)
    
    # fallback - return cleaned response
    return response_text.strip()

def generate_cypher_real(prompt: str) -> str:
    """real openai api cypher generation with proper error handling"""
    if not client:
        # no valid api key or client initialization failed
        return generate_cypher_mock(prompt)
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            max_tokens=500
        )
        raw_response = response.choices[0].message.content.strip()
        return extract_cypher_from_response(raw_response)
    except Exception as e:
        # fallback to mock on any api error
        return generate_cypher_mock(prompt)

def generate_cypher(prompt: str) -> str:
    """main entry point - routes to mock or real based on toggle"""
    if USE_MOCK_LLM:
        query = generate_cypher_mock(prompt)
    else:
        query = generate_cypher_real(prompt)
    
    # safety check - block any destructive queries
    if not is_safe_query(query):
        return "I can only read data, not modify it"
    
    return query 