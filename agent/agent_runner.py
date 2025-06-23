from agent.prompt_template import build_prompt
from services.llm_service import generate_cypher
from services.neo4j_service import run_cypher
from services.output_formatter import format_response


def answer_question(question: str) -> str:
    prompt = build_prompt(question)
    cypher = generate_cypher(prompt)
    results = run_cypher(cypher)
    
    return format_response(question, cypher, results) 