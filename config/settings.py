import os
from dotenv import load_dotenv

# force reload environment variables
load_dotenv(override=True)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7689")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your_password")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...")
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# mock toggles for development
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "true").lower() == "true"
USE_MOCK_NEO4J = os.getenv("USE_MOCK_NEO4J", "true").lower() == "true"

# logging and debugging
VERBOSE = os.getenv("VERBOSE", "false").lower() == "true" 