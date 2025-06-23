import json
import re
import sys
import os

# add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import client, USE_MOCK_LLM, MODEL, TEMPERATURE


def extract_entities_from_chunks(text_chunks: list[str]) -> list[dict]:
    """extracts entities from text chunks"""
    all_entities = []
    
    for chunk in text_chunks:
        entities = extract_entities_from_text(chunk)
        all_entities.extend(entities)
    
    return all_entities


def extract_entities_from_text(text: str) -> list[dict]:
    """extracts entities from a single text chunk"""
    prompt = load_extraction_prompt(text)
    
    if USE_MOCK_LLM:
        response = extract_entities_mock(text)
    else:
        response = extract_entities_real(prompt)
    
    return format_entities_output(response)


def load_extraction_prompt(text: str) -> str:
    """loads extraction prompt template"""
    try:
        # adjust path for running from builder directory
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "extract_entities.txt")
        with open(prompt_path, "r") as f:
            template = f.read()
        return template.format(text=text)
    except FileNotFoundError:
        # fallback prompt if file not found
        return f"""extract all relevant entities and relationships from the following text.

return your response as a json list with this format:
[
  {{"type": "entity", "label": "Person", "name": "alice", "properties": {{"age": 30}}}},
  {{"type": "relationship", "label": "WORKS_FOR", "from": "alice", "to": "acme corp"}}
]

text to analyze:
{text}"""


def extract_entities_mock(text: str) -> str:
    """mock entity extraction for testing"""
    text_lower = text.lower()
    entities = []
    
    # extract people
    if "alice" in text_lower:
        entities.append({"entity": "Person", "name": "Alice", "attributes": {"age": 30}})
    if "bob" in text_lower:
        entities.append({"entity": "Person", "name": "Bob", "attributes": {}})
    if "charlie" in text_lower:
        entities.append({"entity": "Person", "name": "Charlie", "attributes": {"age": 28}})
    
    # extract companies
    if "acme" in text_lower:
        entities.append({"entity": "Company", "name": "Acme Corporation", "attributes": {"founded": 1990}})
    if "tech innovations" in text_lower:
        entities.append({"entity": "Company", "name": "Tech Innovations Inc", "attributes": {"founded": 2020}})
    
    # extract relationships
    if "friends" in text_lower and "alice" in text_lower and "bob" in text_lower:
        entities.append({"relationship": "FRIEND", "from": "Alice", "to": "Bob"})
    
    if "works at" in text_lower or "ceo of" in text_lower:
        if "alice" in text_lower and "acme" in text_lower:
            entities.append({"relationship": "WORKS_FOR", "from": "Alice", "to": "Acme Corporation"})
        if "bob" in text_lower and "acme" in text_lower:
            entities.append({"relationship": "WORKS_FOR", "from": "Bob", "to": "Acme Corporation"})
        if "charlie" in text_lower and "tech innovations" in text_lower:
            entities.append({"relationship": "WORKS_FOR", "from": "Charlie", "to": "Tech Innovations Inc"})
    
    if "knows" in text_lower and "charlie" in text_lower and "alice" in text_lower:
        entities.append({"relationship": "KNOWS", "from": "Charlie", "to": "Alice"})
    
    return json.dumps(entities, indent=2)


def extract_entities_real(prompt: str) -> str:
    """real openai api entity extraction"""
    if not client:
        return extract_entities_mock(prompt.split("text to analyze:")[-1])
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # fallback to mock on any api error
        return extract_entities_mock(prompt.split("text to analyze:")[-1])


def format_entities_output(raw_llm_response: str) -> list[dict]:
    """parses llm response into entities"""
    try:
        # try to parse as json directly
        if raw_llm_response.strip().startswith('['):
            return json.loads(raw_llm_response)
        
        # look for json in code blocks
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_llm_response, re.DOTALL | re.IGNORECASE)
        if json_match:
            return json.loads(json_match.group(1).strip())
        
        # look for json array pattern
        json_match = re.search(r'\[.*\]', raw_llm_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        # if no valid json found, return empty list
        return []
        
    except json.JSONDecodeError:
        # if parsing fails, return empty list
        return []


def main():
    """cli entry point for testing extract_entities.py"""
    test_text = """alice works at acme corporation as a software engineer. she is 30 years old.
    bob is the ceo of acme corporation. he is friends with alice."""
    
    entities = extract_entities_from_chunks([test_text])
    print(f"extracted {len(entities)} entities:")
    print(json.dumps(entities, indent=2))


if __name__ == "__main__":
    main() 