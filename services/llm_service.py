from config.settings import OPENAI_API_KEY, MODEL, TEMPERATURE


def generate_cypher(prompt: str) -> str:
    print(f"received prompt: {prompt}")
    return "MATCH (n) RETURN n" 