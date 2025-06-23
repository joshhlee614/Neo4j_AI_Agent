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
from services.neo4j_service import run_cypher_real


def run_build_pipeline(input_file: str, ingest_to_neo4j: bool = False) -> None:
    """runs the full build pipeline"""
    print(f"starting build pipeline for: {input_file}")
    
    try:
        # load and chunk file
        print("loading and chunking file...")
        chunks = load_and_chunk_file(input_file)
        print(f"created {len(chunks)} chunks")
        
        # extract entities from chunks
        print("extracting entities...")
        entities = extract_entities_from_chunks(chunks)
        print(f"extracted {len(entities)} entities/relationships")
        
        # generate schema from entities
        print("generating schema...")
        schema = generate_schema_from_entities(entities)
        node_count = len(schema.get("nodes", {}))
        edge_count = len(schema.get("edges", {}))
        print(f"generated schema with {node_count} node types and {edge_count} edge types")
        
        # generate cypher from schema and entities
        print("generating cypher...")
        cypher = generate_cypher_from_schema(schema, entities)
        cypher_lines = len([line for line in cypher.split('\n') if line.strip()])
        print(f"generated {cypher_lines} cypher statements")
        
        # save outputs
        print("saving outputs...")
        save_pipeline_outputs(entities, schema, cypher, input_file)
        
        # ingest to neo4j if requested
        if ingest_to_neo4j:
            print("ingesting to neo4j...")
            ingest_cypher_to_neo4j(cypher)
        
        print("pipeline completed successfully!")
        print("outputs saved to data/ directory")
        if ingest_to_neo4j:
            print("data ingested to neo4j database")
        
    except Exception as e:
        print(f"pipeline failed: {e}")
        raise


def ingest_cypher_to_neo4j(cypher: str) -> None:
    """executes cypher statements in neo4j"""
    # split cypher into individual statements
    statements = [stmt.strip() for stmt in cypher.split(';') if stmt.strip()]
    
    print(f"ingesting {len(statements)} cypher statements...")
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements):
        try:
            print(f"executing statement {i+1}/{len(statements)}: {statement[:50]}...")
            result = run_cypher_real(statement)
            
            # check if result indicates an error
            if result and isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and result[0].get("status") == "database_error":
                    print(f"error in statement {i+1}: {result[0].get('message', 'unknown error')}")
                    error_count += 1
                else:
                    success_count += 1
            else:
                success_count += 1
                
        except Exception as e:
            print(f"error executing statement {i+1}: {e}")
            error_count += 1
    
    print(f"ingestion complete: {success_count} successful, {error_count} errors")
    
    if error_count > 0:
        print("warning: some statements failed to execute")
    
    # verify ingestion with a simple count query
    try:
        count_result = run_cypher_real("MATCH (n) RETURN count(n) as total_nodes")
        if count_result and len(count_result) > 0:
            total_nodes = count_result[0].get("total_nodes", 0)
            print(f"verification: {total_nodes} total nodes in database")
    except Exception as e:
        print(f"verification query failed: {e}")


def save_pipeline_outputs(entities: list, schema: dict, cypher: str, input_file: str) -> None:
    """saves outputs to data directory"""
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
    
    # save to standard output filenames
    with open(os.path.join(data_dir, "schema_output.json"), "w") as f:
        json.dump(schema, f, indent=2)
    print(f"schema saved to: {os.path.join(data_dir, 'schema_output.json')}")
    
    with open(os.path.join(data_dir, "cypher_output.cypher"), "w") as f:
        f.write(cypher)
    print(f"cypher saved to: {os.path.join(data_dir, 'cypher_output.cypher')}")


def main():
    """cli entry point for build_graph.py"""
    if len(sys.argv) < 2:
        print("usage: python build_graph.py <input_file> [--ingest]")
        print("example: python build_graph.py data/sample_input.txt")
        print("example: python build_graph.py data/sample_input.txt --ingest")
        return
    
    input_file = sys.argv[1]
    ingest_to_neo4j = "--ingest" in sys.argv
    
    # check if file exists
    if not os.path.exists(input_file):
        print(f"error: file not found: {input_file}")
        return
    
    run_build_pipeline(input_file, ingest_to_neo4j)


if __name__ == "__main__":
    main() 