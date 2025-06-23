import json
import os
import sys

# add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import client


def generate_schema_from_entities(entities: list[dict]) -> dict:
    """infers graph schema from extracted entities"""
    try:
        # load prompt template
        prompt = load_schema_prompt()
        
        # format entities for prompt
        entities_text = json.dumps(entities, indent=2)
        formatted_prompt = prompt.format(entities=entities_text)
        
        # get schema from llm
        if os.getenv("USE_MOCK_LLM", "false").lower() == "true":
            raw_response = generate_schema_mock(entities)
        else:
            raw_response = generate_schema_real(formatted_prompt)
        
        # parse and return structured format
        return format_schema_output(raw_response)
    
    except Exception as e:
        print(f"error generating schema: {e}")
        return {"nodes": {}, "edges": {}}


def load_schema_prompt() -> str:
    """loads schema generation prompt template"""
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "generate_schema.txt")
    
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "generate a graph schema from these entities: {entities}"


def generate_schema_mock(entities: list[dict]) -> str:
    """mock schema generation for testing"""
    # analyze entities to create schema
    nodes = {}
    edges = {}
    
    for item in entities:
        if "entity" in item:
            entity_type = item["entity"]
            if entity_type not in nodes:
                nodes[entity_type] = []
            
            # add attributes
            if "attributes" in item:
                for attr in item["attributes"]:
                    if attr not in nodes[entity_type]:
                        nodes[entity_type].append(attr)
            
            # add name as default property
            if "name" not in nodes[entity_type]:
                nodes[entity_type].append("name")
        
        elif "relationship" in item:
            rel_type = item["relationship"]
            if rel_type not in edges:
                # try to infer from/to types from the entities
                from_entity = "Entity"
                to_entity = "Entity"
                
                # look for entities with matching names
                for entity in entities:
                    if "entity" in entity:
                        if entity.get("name") == item.get("from"):
                            from_entity = entity["entity"]
                        elif entity.get("name") == item.get("to"):
                            to_entity = entity["entity"]
                
                edges[rel_type] = {"from": from_entity, "to": to_entity}
    
    schema = {"nodes": nodes, "edges": edges}
    return json.dumps(schema, indent=2)


def generate_schema_real(prompt: str) -> str:
    """real schema generation using openai"""
    if not client:
        return generate_schema_mock([])
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"error calling openai: {e}")
        return '{"nodes": {}, "edges": {}}'


def format_schema_output(raw_llm_response: str) -> dict:
    """parses llm response into structured schema format"""
    try:
        # try to parse as json
        if raw_llm_response.strip().startswith("{"):
            return json.loads(raw_llm_response)
        
        # try to find json in response
        start_idx = raw_llm_response.find("{")
        end_idx = raw_llm_response.rfind("}") + 1
        
        if start_idx != -1 and end_idx != -1:
            json_str = raw_llm_response[start_idx:end_idx]
            return json.loads(json_str)
        
        # fallback
        return {"nodes": {}, "edges": {}}
    
    except Exception as e:
        print(f"error parsing schema response: {e}")
        return {"nodes": {}, "edges": {}}


def main():
    """cli interface for testing"""
    if len(sys.argv) < 2:
        print("usage: python generate_schema.py <entities_file>")
        sys.exit(1)
    
    entities_file = sys.argv[1]
    
    try:
        with open(entities_file, "r") as f:
            entities = json.load(f)
        
        schema = generate_schema_from_entities(entities)
        print(json.dumps(schema, indent=2))
    
    except FileNotFoundError:
        print(f"file not found: {entities_file}")
    except Exception as e:
        print(f"error: {e}")


if __name__ == "__main__":
    main() 