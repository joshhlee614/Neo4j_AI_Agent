from agent.prompt_template import build_prompt
from services.llm_service import generate_cypher
from services.neo4j_service import run_cypher
from services.output_formatter import format_response
from config.settings import VERBOSE


def log_verbose(message: str) -> None:
    """print debug message if verbose mode is enabled"""
    if VERBOSE:
        print(f"[DEBUG] {message}")


def answer_question(question: str) -> str:
    log_verbose("Starting question processing")
    log_verbose(f"Input question: {question}")
    
    # build prompt with schema and examples
    prompt = build_prompt(question)
    log_verbose("Built prompt with schema and examples")
    if VERBOSE:
        print("[DEBUG] Full prompt:")
        print("─" * 50)
        print(prompt)
        print("─" * 50)
    
    # generate cypher query
    log_verbose("Generating Cypher query...")
    cypher = generate_cypher(prompt)
    log_verbose(f"Generated Cypher: {cypher}")
    
    # execute query against database
    log_verbose("Executing query against Neo4j...")
    results = run_cypher(cypher)
    log_verbose(f"Query returned {len(results)} results")
    if VERBOSE and results:
        print("[DEBUG] Raw results:")
        for i, result in enumerate(results[:3]):  # show first 3 results
            print(f"  {i+1}: {result}")
        if len(results) > 3:
            print(f"  ... and {len(results) - 3} more")
    
    # format response for display
    log_verbose("Formatting response for display")
    formatted_response = format_response(question, cypher, results)
    log_verbose("Question processing complete")
    
    return formatted_response 