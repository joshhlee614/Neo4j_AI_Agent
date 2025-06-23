def format_response(question: str, cypher_query: str, results: list) -> str:
    output = []
    
    output.append(f"question: {question}")
    output.append(f"generated cypher: {cypher_query}")
    output.append("")
    
    if not results:
        output.append("no results found")
    elif len(results) == 1 and results[0].get('status') == 'connection_failed':
        output.append("note: using sample data (database not connected)")
        output.append("sample results:")
        output.append("- alice (person)")
        output.append("- bob (person)")  
        output.append("- usa (country)")
    else:
        output.append("results:")
        for i, record in enumerate(results[:10], 1):
            if isinstance(record, dict):
                items = []
                for key, value in record.items():
                    if key != 'status':
                        items.append(f"{key}: {value}")
                if items:
                    output.append(f"- {', '.join(items)}")
            else:
                output.append(f"- {record}")
        
        if len(results) > 10:
            output.append(f"... and {len(results) - 10} more results")
    
    return "\n".join(output) 