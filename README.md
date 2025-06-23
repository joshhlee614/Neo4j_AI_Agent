# Neo4j AI Agent

Converts natural language queries to Cypher and executes them against Neo4j databases.

## Features

- Natural language to Cypher translation using LLM
- Neo4j database integration
- Minimal setup and configuration

## Requirements

- Python 3.8+
- Neo4j database instance
- OpenAI API key

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set environment variables or update `config/settings.py`:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j" 
export NEO4J_PASSWORD="your_password"
export OPENAI_API_KEY="your_api_key"
```

## Usage

```bash
python app.py
``` 