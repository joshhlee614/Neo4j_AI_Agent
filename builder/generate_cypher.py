import json
import os
import sys
import re

# add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import client, generate_cypher as llm_generate_cypher
from config.settings import USE_MOCK_LLM


def sanitize_property_name(prop_name):
    """Convert property names to valid Cypher format"""
    if not prop_name:
        return prop_name
    
    # Convert spaces and special characters to underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', str(prop_name))
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = 'prop_' + sanitized
    
    return sanitized or 'unknown_prop'


def sanitize_cypher_properties(cypher_statement):
    """Fix property names in Cypher statements"""
    # Pattern to match property assignments like {name: "value", bad prop: "value2"}
    def fix_properties(match):
        props_content = match.group(1)
        # Split by commas, but be careful with quoted strings
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        
        for char in props_content:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ',' and not in_quotes:
                parts.append(current_part.strip())
                current_part = ""
                continue
            current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Fix each property
        fixed_parts = []
        for part in parts:
            if ':' in part:
                key_part, value_part = part.split(':', 1)
                key_part = key_part.strip()
                
                # Remove quotes from key if present
                if key_part.startswith('"') and key_part.endswith('"'):
                    key_part = key_part[1:-1]
                elif key_part.startswith("'") and key_part.endswith("'"):
                    key_part = key_part[1:-1]
                
                # Sanitize the key
                sanitized_key = sanitize_property_name(key_part)
                fixed_parts.append(f"{sanitized_key}:{value_part}")
            else:
                fixed_parts.append(part)
        
        return "{" + ", ".join(fixed_parts) + "}"
    
    # Apply the fix to all property blocks
    fixed_cypher = re.sub(r'\{([^}]+)\}', fix_properties, cypher_statement)
    return fixed_cypher


def generate_cypher_from_schema(schema: dict, entities: list[dict]) -> str:
    """converts schema and entities into cypher create statements"""
    try:
        # Check if we need to use batched processing
        prompt_template = load_cypher_prompt()
        schema_text = json.dumps(schema, indent=2)
        entities_text = json.dumps(entities, indent=2)
        full_prompt = prompt_template.format(schema=schema_text, entities=entities_text)
        estimated_tokens = len(full_prompt) // 4
        
        # If prompt is too long, use batched processing
        if estimated_tokens > 3500:  # Leave buffer for response
            print(f"prompt too long ({estimated_tokens} tokens), using batched processing...")
            return generate_cypher_batched(schema, entities)
        
        # Original single-batch processing
        formatted_prompt = full_prompt
        
        # get cypher from llm
        if os.getenv("USE_MOCK_LLM", "false").lower() == "true":
            raw_response = generate_cypher_mock(schema, entities)
        else:
            # Use direct OpenAI call to bypass safety restrictions for KG building
            raw_response = generate_cypher_real_direct(formatted_prompt)
            # Sanitize property names in the generated Cypher
            raw_response = sanitize_cypher_properties(raw_response)
        
        # parse and return clean cypher
        return format_cypher_output(raw_response)
    
    except Exception as e:
        print(f"error generating cypher: {e}")
        return "// error generating cypher statements"


def generate_cypher_batched(schema: dict, entities: list[dict], batch_size: int = 30) -> str:
    """Generate Cypher in batches to handle large datasets"""
    all_cypher_statements = []
    
    # Process in batches
    total_batches = (len(entities) + batch_size - 1) // batch_size
    
    for i in range(0, len(entities), batch_size):
        batch = entities[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"processing batch {batch_num}/{total_batches} ({len(batch)} items)...")
        
        try:
            # Generate Cypher for this batch
            prompt = load_cypher_prompt()
            schema_text = json.dumps(schema, indent=2)
            entities_text = json.dumps(batch, indent=2)
            formatted_prompt = prompt.format(schema=schema_text, entities=entities_text)
            
            if os.getenv("USE_MOCK_LLM", "false").lower() == "true":
                raw_response = generate_cypher_mock(schema, batch)
            else:
                raw_response = generate_cypher_real_direct(formatted_prompt)
                raw_response = sanitize_cypher_properties(raw_response)
            
            # Format and collect statements
            batch_cypher = format_cypher_output(raw_response)
            if batch_cypher.strip():
                all_cypher_statements.append(batch_cypher)
                
        except Exception as e:
            print(f"error processing batch {batch_num}: {e}")
            continue
    
    # Combine all batches and deduplicate
    combined_cypher = '\n'.join(all_cypher_statements)
    
    # Final deduplication across all batches
    lines = combined_cypher.split('\n')
    seen_statements = set()
    final_statements = []
    
    for line in lines:
        line = line.strip()
        if line and line not in seen_statements:
            seen_statements.add(line)
            final_statements.append(line)
    
    # Apply final limit
    if len(final_statements) > 150:  # Increased limit for batched processing
        print(f"warning: truncating {len(final_statements)} statements to 150")
        final_statements = final_statements[:150]
    
    return '\n'.join(final_statements)


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
    entity_vars = {}  # map entity names to their variables
    used_vars = set()  # track used variable names
    var_counter = 0
    
    # Helper function to get next available variable
    def get_next_var():
        nonlocal var_counter
        var_counter += 1
        return f"n{var_counter}"
    
    # First pass: create all nodes and assign variables
    for entity in entities:
        if "entity" in entity:
            entity_type = entity["entity"]
            entity_name = entity.get("name", "Unknown")
            
            # Skip if we've already seen this entity
            if entity_name in entity_vars:
                continue
            
            # Get unique variable name
            var_name = get_next_var()
            entity_vars[entity_name] = var_name
            used_vars.add(var_name)
            
            # Build properties (exclude null values)
            props = [f'name: "{entity_name}"']
            if "attributes" in entity:
                for key, value in entity["attributes"].items():
                    if value is not None and value != "null" and value != "":
                        # Sanitize property name
                        clean_key = sanitize_property_name(key)
                        if isinstance(value, str):
                            # Escape quotes in string values
                            escaped_value = value.replace('"', '\\"')
                            props.append(f'{clean_key}: "{escaped_value}"')
                        elif isinstance(value, (int, float)):
                            props.append(f'{clean_key}: {value}')
                        elif isinstance(value, bool):
                            props.append(f'{clean_key}: {str(value).lower()}')
                        elif isinstance(value, list):
                            # Convert list to string representation
                            list_str = str(value).replace("'", '"')
                            props.append(f'{clean_key}: {list_str}')
            
            props_str = ", ".join(props)
            cypher_statements.append(f"MERGE ({var_name}:{entity_type} {{{props_str}}});")
    
    # Second pass: create relationships
    for entity in entities:
        if "relationship" in entity:
            rel_type = entity["relationship"]
            from_name = entity.get("from", "")
            to_name = entity.get("to", "")
            
            # Only create relationship if both entities exist
            if from_name in entity_vars and to_name in entity_vars:
                from_var = entity_vars[from_name]
                to_var = entity_vars[to_name]
                cypher_statements.append(f"MERGE ({from_var})-[:{rel_type}]->({to_var});")
            else:
                # Log missing entities for debugging
                missing = []
                if from_name not in entity_vars:
                    missing.append(f"from: {from_name}")
                if to_name not in entity_vars:
                    missing.append(f"to: {to_name}")
                print(f"warning: skipping relationship {rel_type} - missing entities: {', '.join(missing)}")
    
    return "\n".join(cypher_statements)


def generate_cypher_real_direct(prompt: str) -> str:
    """Direct OpenAI call for KG building (bypasses safety restrictions)"""
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
    """parses llm response into clean cypher statements with deduplication"""
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
        seen_statements = set()  # track duplicates
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('#'):
                # ensure line ends with semicolon if it's a cypher statement
                if line.upper().startswith(('CREATE', 'MERGE', 'MATCH')) and not line.endswith(';'):
                    line += ';'
                
                # deduplicate identical statements
                if line not in seen_statements:
                    seen_statements.add(line)
                    cypher_lines.append(line)
        
        # Validate and fix the Cypher statements
        validated_cypher = validate_cypher_statements(cypher_lines)
        
        # limit to reasonable number of statements
        if len(validated_cypher) > 100:
            print(f"warning: truncating {len(validated_cypher)} statements to 100")
            validated_cypher = validated_cypher[:100]
        
        return '\n'.join(validated_cypher)
    
    except Exception as e:
        print(f"error formatting cypher: {e}")
        return raw_llm_response


def validate_cypher_statements(cypher_lines: list[str]) -> list[str]:
    """validates cypher statements to ensure all nodes have proper labels"""
    validated_lines = []
    
    for line in cypher_lines:
        # Check for unlabeled nodes in MERGE statements
        if line.upper().startswith('MERGE'):
            # Pattern to find nodes without labels: (variable) instead of (variable:Label)
            import re
            
            # Find all node patterns in the statement
            node_pattern = r'\(([^)]+)\)'
            matches = re.findall(node_pattern, line)
            
            has_unlabeled_node = False
            for match in matches:
                # Check if node has a label (contains colon)
                if ':' not in match and '-[' not in line:
                    # This is an unlabeled node (but not a relationship pattern)
                    print(f"warning: found unlabeled node in statement: {line}")
                    has_unlabeled_node = True
                    break
                elif ':' not in match and '-[' in line:
                    # This is a relationship with unlabeled nodes - skip it
                    print(f"warning: found relationship with unlabeled nodes: {line}")
                    has_unlabeled_node = True
                    break
            
            # Skip statements with unlabeled nodes
            if has_unlabeled_node:
                continue
        
        validated_lines.append(line)
    
    return validated_lines


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