from agent.prompt_template import build_prompt
from services.llm_service import generate_cypher
from services.neo4j_service import run_cypher


def answer_question(question: str) -> str:
    print(f"processing question: {question}")
    
    prompt = build_prompt(question)
    cypher = generate_cypher(prompt)
    results = run_cypher(cypher)
    
    print(f"final results: {results}")
    return str(results) 