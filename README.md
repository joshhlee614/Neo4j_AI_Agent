# Neo4j AI Agent & Knowledge Graph Builder

An LLM-powered system that builds knowledge graphs from documents and provides natural language querying capabilities. Upload PDFs or text files, automatically extract entities and relationships, and query the resulting graph using plain English.

## Features

### Knowledge Graph Builder
- **PDF/Text Ingestion**: Process PDFs, text files, and markdown documents
- **LLM Entity Extraction**: Automatically identify entities, relationships, and attributes
- **Dynamic Schema Generation**: Infer graph schema from extracted data
- **Cypher Generation**: Convert structured data to Neo4j CREATE statements
- **Full Pipeline Orchestration**: One-command document-to-graph processing

### AI Query Agent
- **Natural Language Queries**: Ask questions in plain English
- **Dynamic Schema Discovery**: Automatically discovers database structure
- **Cypher Translation**: Converts questions to optimized Cypher queries
- **Professional Output**: Clean table formatting and error handling
- **Schema-Aware**: Only uses existing nodes, relationships, and properties

## Architecture

```
Document Input → LLM Processing → Knowledge Graph → Natural Language Queries

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF/Text      │───▶│  Entity          │───▶│  Schema         │───▶│  Cypher         │
│   Ingestion     │    │  Extraction      │    │  Generation     │    │  Generation     │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
                                                                              │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐           │
│   Natural       │───▶│  Query           │───▶│  Neo4j          │◀──────────┘
│   Language      │    │  Generation      │    │  Database       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Project Structure

```
Neo4j_AI_Agent/
├── builder/                    # Knowledge graph builder pipeline
│   ├── build_graph.py         # Main orchestration pipeline
│   ├── extract_entities.py    # LLM entity extraction
│   ├── generate_schema.py     # Schema inference
│   ├── generate_cypher.py     # Cypher statement generation
│   └── ingest_pdf.py          # Document processing
├── agent/                     # AI query agent
│   ├── agent_runner.py        # Query processing
│   ├── prompt_template.py     # Dynamic prompt generation
│   └── schema_discovery.py    # Live schema discovery
├── services/                  # Core services
│   ├── llm_service.py         # OpenAI integration
│   ├── neo4j_service.py       # Database operations
│   └── output_formatter.py    # Result formatting
├── prompts/                   # LLM prompt templates
│   ├── extract_entities.txt
│   ├── generate_schema.txt
│   └── generate_cypher.txt
├── data/                      # Input/output files
└── app.py                     # Main CLI interface
```

## Requirements

- Python 3.8+
- Neo4j database instance (Desktop, Cloud, or Enterprise)
- OpenAI API key (optional - has mock mode)

## Installation

```bash
git clone https://github.com/yourusername/Neo4j_AI_Agent.git
cd Neo4j_AI_Agent
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your settings:

```bash
# Neo4j connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# OpenAI API
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-3.5-turbo
TEMPERATURE=0.3

# Development toggles
USE_MOCK_LLM=false
USE_MOCK_NEO4J=false
VERBOSE=false
```

## Usage

### Build Knowledge Graph from Document

```bash
# Process a PDF and populate Neo4j database
python app.py --build data/sample_document.pdf --ingest

# Process without ingesting (generate Cypher only)
python app.py --build data/sample_document.pdf
```

### Query the Knowledge Graph

```bash
# Ask natural language questions
python app.py "What companies are mentioned in the database?"
python app.py "Show me all relationships between people and organizations"
python app.py "How many nodes are in the database?"
```

### Interactive Mode

```bash
python app.py
# Enter questions interactively
```

## Example Workflow

1. **Upload Document**: Place PDF in `data/` directory
2. **Build Graph**: `python app.py --build data/document.pdf --ingest`
3. **Query Graph**: `python app.py "What entities were extracted?"`

## Development

### Mock Mode Testing

```bash
# Test without OpenAI API
USE_MOCK_LLM=true python app.py --build data/sample_input.txt

# Test without Neo4j database
USE_MOCK_NEO4J=true python app.py "test query"
```

### Module Testing

```bash
# Test individual components
python builder/ingest_pdf.py data/sample.pdf
python builder/extract_entities.py
python builder/generate_schema.py data/entities.json
```

## Supported Domains

- **Financial Data**: Companies, markets, trading strategies
- **Academic Papers**: Authors, institutions, research topics
- **Business Documents**: Organizations, people, processes
- **General Text**: Any domain with entities and relationships

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- OpenAI for GPT models
- Neo4j for graph database technology
- PyPDF2 for PDF processing 
