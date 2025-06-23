import json
import os
import sys
import re

# add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import client


def generate_cypher_from_schema(schema: dict, entities: list[dict]) -> str:
    """converts schema and entities into cypher create statements"""
    try:
        # load prompt template
        prompt = load_cypher_prompt()
        
        # format schema and entities for prompt
        schema_text = json.dumps(schema, indent=2)
        entities_text = json.dumps(entities, indent=2)
        formatted_prompt = prompt.format(schema=schema_text, entities=entities_text)
        
        # get cypher from llm
        if os.getenv("USE_MOCK_LLM", "false").lower() == "true":
            raw_response = generate_cypher_mock(schema, entities)
        else:
            raw_response = generate_cypher_real(formatted_prompt)
        
        # parse and return clean cypher
        return format_cypher_output(raw_response)
    
    except Exception as e:
        print(f"error generating cypher: {e}")
        return "// error generating cypher statements"


def load_cypher_prompt() -> str:
    """loads cypher generation prompt template"""
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "generate_cypher.txt")
    
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "generate cypher create statements from this schema and entities: schema: {schema} entities: {entities}"


def generate_cypher_mock(schema: dict, entities: list[dict]) -> str:
    """mock cypher generation for testing"""
    cypher_statements = []
    entity_vars = {}  # track variable names for relationships
    
    # create nodes
    for entity in entities:
        if "entity" in entity:
            entity_type = entity["entity"]
            entity_name = entity.get("name", "Unknown")
            
            # create variable name (first letter + counter)
            var_name = entity_type.lower()[0]
            counter = 1
            base_var = var_name
            while var_name in entity_vars.values():
                var_name = f"{base_var}{counter}"
                counter += 1
            
            entity_vars[entity_name] = var_name
            
            # build properties
            props = [f'name: "{entity_name}"']
            if "attributes" in entity:
                for key, value in entity["attributes"].items():
                    if isinstance(value, str):
                        props.append(f'{key}: "{value}"')
                    else:
                        props.append(f'{key}: {value}')
            
            props_str = ", ".join(props)
            cypher_statements.append(f"CREATE ({var_name}:{entity_type} {{{props_str}}});")
    
    # create relationships
    for entity in entities:
        if "relationship" in entity:
            rel_type = entity["relationship"]
            from_name = entity.get("from", "")
            to_name = entity.get("to", "")
            
            from_var = entity_vars.get(from_name, "a")
            to_var = entity_vars.get(to_name, "b")
            
            cypher_statements.append(f"CREATE ({from_var})-[:{rel_type}]->({to_var});")
    
    return "\n".join(cypher_statements)


def generate_cypher_real(prompt: str) -> str:
    """real cypher generation using openai"""
    if not client:
        return generate_cypher_mock({}, [])
    
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
        return "// error calling openai api"


def format_cypher_output(raw_llm_response: str) -> str:
    """parses llm response into clean cypher statements"""
    try:
        # remove markdown code blocks if present
        if "```" in raw_llm_response:
            # extract cypher from code blocks
            pattern = r'```(?:cypher)?\s*(.*?)\s*```'
            matches = re.findall(pattern, raw_llm_response, re.DOTALL | re.IGNORECASE)
            if matches:
                raw_llm_response = matches[0]
        
        # clean up the response
        lines = raw_llm_response.strip().split('\n')
        cypher_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('#'):
                # ensure line ends with semicolon if it's a cypher statement
                if line.upper().startswith(('CREATE', 'MERGE', 'MATCH')) and not line.endswith(';'):
                    line += ';'
                cypher_lines.append(line)
        
        return '\n'.join(cypher_lines)
    
    except Exception as e:
        print(f"error formatting cypher: {e}")
        return raw_llm_response


def main():
    """cli interface for testing"""
    if len(sys.argv) < 3:
        print("usage: python generate_cypher.py <schema_file> <entities_file>")
        sys.exit(1)
    
    schema_file = sys.argv[1]
    entities_file = sys.argv[2]
    
    try:
        with open(schema_file, "r") as f:
            schema = json.load(f)
        
        with open(entities_file, "r") as f:
            entities = json.load(f)
        
        cypher = generate_cypher_from_schema(schema, entities)
        print(cypher)
    
    except FileNotFoundError as e:
        print(f"file not found: {e}")
    except Exception as e:
        print(f"error: {e}")


if __name__ == "__main__":
    main() 