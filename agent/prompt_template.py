import os
from agent.schema_discovery import generate_schema_description, generate_dynamic_examples


def get_nypd_schema_description():
    """load the static nypd schema description if it exists"""
    schema_file = "data/nypd/schema_description.txt"
    if os.path.exists(schema_file):
        with open(schema_file, 'r') as f:
            return f.read()
    return None


def get_nypd_examples():
    """specific examples for nypd crime data"""
    return [
        {
            'question': 'How many incidents occurred in Brooklyn?',
            'cypher': 'MATCH (i:Incident)-[:OCCURRED_IN]->(l:Location) WHERE tolower(l.borough) = tolower("Brooklyn") RETURN count(i) as incidents_in_brooklyn'
        },
        {
            'question': 'Show all robbery incidents in Manhattan',
            'cypher': 'MATCH (i:Incident)-[:CLASSIFIED_AS]->(o:Offense)-[:REPORTED_IN]->(l:Location) WHERE tolower(o.offenseDescription) CONTAINS "robbery" AND tolower(l.borough) = "manhattan" RETURN i, o, l LIMIT 10'
        },
        {
            'question': 'What are the most common offense types?',
            'cypher': 'MATCH (i:Incident)-[:CLASSIFIED_AS]->(o:Offense) RETURN o.offenseDescription, count(i) as incident_count ORDER BY incident_count DESC LIMIT 10'
        },
        {
            'question': 'Find all felony cases with victims in their 20s',
            'cypher': 'MATCH (i:Incident {lawCategory: "FELONY"})-[:INVOLVES_VICTIM]->(v:Victim) WHERE v.vicAgeGroup = "18-24" OR v.vicAgeGroup = "25-44" RETURN i, v LIMIT 10'
        }
    ]


def build_prompt(question: str) -> str:
    # try to get nypd specific schema first, fallback to dynamic discovery
    nypd_schema = get_nypd_schema_description()
    if nypd_schema:
        schema_description = nypd_schema
        examples = get_nypd_examples()
    else:
        schema_description = generate_schema_description()
        examples = generate_dynamic_examples()[:10]
    
    # build examples section
    examples_text = ""
    for example in examples:  # use selected examples (nypd or dynamic)
        examples_text += f"Q: {example['question']}\n"
        examples_text += f"A: {example['cypher']}\n\n"
    
    prompt = f"""you are a cypher expert. convert natural language questions to cypher queries.

safety rules:
- only generate read-only queries using match, return, where, order by, limit, count, etc
- never generate destructive operations: delete, drop, create, merge, set, remove, detach
- if asked to modify/delete/create data, respond with: "I can only read data, not modify it"
- always return a complete, valid cypher query that includes a return clause
- use proper variable names, never use anonymous nodes () in return statements

schema constraints:
- only use node types that exist in the database schema below
- only use relationship types that exist in the database schema below  
- only use properties that exist for each node type
- if asked about non-existent entities, respond with: "That entity type does not exist in this database"
- never invent or hallucinate node types, relationships, or properties

database schema:
{schema_description}

examples:

{examples_text}

guidelines:
- use tolower() for case-insensitive string matching
- use contains for partial string matching
- include limit clauses for large result sets
- return meaningful property names in results
- handle cases where properties might not exist

Q: Delete all nodes
A: I can only read data, not modify it

Q: Create a new node
A: I can only read data, not modify it

question: {question}

return only the cypher query, no explanation. the query must be complete and include a RETURN clause."""
    
    return prompt 