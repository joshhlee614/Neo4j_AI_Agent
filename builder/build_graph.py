import json
import os
import sys
from datetime import datetime

# add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from builder.ingest_pdf import load_and_chunk_file
from builder.extract_entities import extract_entities_from_chunks
from builder.generate_schema import generate_schema_from_entities
from builder.generate_cypher import generate_cypher_from_schema


def run_build_pipeline(input_file: str) -> None:
    """orchestrates the full pipeline: text -> schema -> cypher -> neo4j"""
    print(f"starting build pipeline for: {input_file}")
    
    try:
        # step 1: ingest and chunk file
        print("step 1: loading and chunking file...")
        chunks = load_and_chunk_file(input_file)
        print(f"created {len(chunks)} chunks")
        
        # step 2: extract entities from chunks
        print("step 2: extracting entities...")
        entities = extract_entities_from_chunks(chunks)
        print(f"extracted {len(entities)} entities/relationships")
        
        # step 3: generate schema from entities
        print("step 3: generating schema...")
        schema = generate_schema_from_entities(entities)
        node_count = len(schema.get("nodes", {}))
        edge_count = len(schema.get("edges", {}))
        print(f"generated schema with {node_count} node types and {edge_count} edge types")
        
        # step 4: generate cypher from schema and entities
        print("step 4: generating cypher...")
        cypher = generate_cypher_from_schema(schema, entities)
        cypher_lines = len([line for line in cypher.split('\n') if line.strip()])
        print(f"generated {cypher_lines} cypher statements")
        
        # step 5: save outputs
        print("step 5: saving outputs...")
        save_pipeline_outputs(entities, schema, cypher, input_file)
        
        print("pipeline completed successfully!")
        print("outputs saved to data/ directory")
        
    except Exception as e:
        print(f"pipeline failed: {e}")
        raise


def save_pipeline_outputs(entities: list, schema: dict, cypher: str, input_file: str) -> None:
    """saves all pipeline outputs to data/ directory"""
    # ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # save entities
    entities_file = os.path.join(data_dir, f"{base_name}_entities_{timestamp}.json")
    with open(entities_file, "w") as f:
        json.dump(entities, f, indent=2)
    print(f"entities saved to: {entities_file}")
    
    # save schema
    schema_file = os.path.join(data_dir, f"{base_name}_schema_{timestamp}.json")
    with open(schema_file, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"schema saved to: {schema_file}")
    
    # save cypher
    cypher_file = os.path.join(data_dir, f"{base_name}_cypher_{timestamp}.cypher")
    with open(cypher_file, "w") as f:
        f.write(cypher)
    print(f"cypher saved to: {cypher_file}")
    
    # also save to standard names for easy access
    with open(os.path.join(data_dir, "latest_entities.json"), "w") as f:
        json.dump(entities, f, indent=2)
    
    with open(os.path.join(data_dir, "latest_schema.json"), "w") as f:
        json.dump(schema, f, indent=2)
    
    with open(os.path.join(data_dir, "latest_cypher.cypher"), "w") as f:
        f.write(cypher)


def main():
    """cli entry point for build_graph.py"""
    if len(sys.argv) != 2:
        print("usage: python build_graph.py <input_file>")
        print("example: python build_graph.py data/sample_input.txt")
        return
    
    input_file = sys.argv[1]
    
    # check if file exists
    if not os.path.exists(input_file):
        print(f"error: file not found: {input_file}")
        return
    
    run_build_pipeline(input_file)


if __name__ == "__main__":
    main() 