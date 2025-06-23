# Neo4j AI Agent

Converts natural language queries to Cypher and executes them against Neo4j databases. Works with any Neo4j database schema including financial, social, and business data.

## Features

- Natural language to Cypher translation using OpenAI
- Universal Neo4j database compatibility 
- Mock/real service toggles for development
- Professional table output formatting
- Robust error handling and fallbacks

## Requirements

- Python 3.8+
- Neo4j database instance (Desktop, Cloud, or Enterprise)
- OpenAI API key (optional - has mock mode)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Neo4j connection (Neo4j Desktop default port)
NEO4J_URI=bolt://localhost:7689
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# OpenAI API
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Development toggles
USE_MOCK_LLM=true
USE_MOCK_NEO4J=false
```

## Usage

```bash
python app.py "show me similar assets"
```

Or interactive mode:
```bash
python app.py
``` 