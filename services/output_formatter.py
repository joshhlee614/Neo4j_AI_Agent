def format_table(results: list) -> str:
    """format results as a clean table with headers"""
    if not results:
        return "no results found"
    
    # extract all unique column names from results
    columns = set()
    for record in results:
        if isinstance(record, dict):
            columns.update(record.keys())
    
    # filter out status columns and sort
    columns = sorted([col for col in columns if col != 'status'])
    
    if not columns:
        return "no data to display"
    
    # clean up column names for display
    display_columns = []
    for col in columns:
        # convert p.name -> Name, c.name -> Country, etc.
        if '.' in col:
            prefix, suffix = col.split('.', 1)
            if suffix == 'name':
                if prefix == 'p':
                    display_columns.append('Name')
                elif prefix == 'c':
                    display_columns.append('Country')
                elif prefix == 'pr':
                    display_columns.append('Product')
                else:
                    display_columns.append(suffix.title())
            else:
                display_columns.append(suffix.title())
        else:
            display_columns.append(col.title())
    
    # calculate column widths
    col_widths = []
    for i, col in enumerate(display_columns):
        max_width = len(col)
        for record in results:
            if isinstance(record, dict):
                value = str(record.get(columns[i], ''))
                max_width = max(max_width, len(value))
        col_widths.append(max_width + 2)  # padding
    
    # build table
    table_lines = []
    
    # header separator
    table_lines.append("┌" + "┬".join("─" * width for width in col_widths) + "┐")
    
    # header row
    header_row = "│"
    for i, col in enumerate(display_columns):
        header_row += f" {col:<{col_widths[i]-1}}│"
    table_lines.append(header_row)
    
    # separator between header and data
    table_lines.append("├" + "┼".join("─" * width for width in col_widths) + "┤")
    
    # data rows
    for record in results[:10]:  # limit to 10 results
        if isinstance(record, dict):
            row = "│"
            for i, col in enumerate(columns):
                value = str(record.get(col, ''))
                row += f" {value:<{col_widths[i]-1}}│"
            table_lines.append(row)
    
    # bottom border
    table_lines.append("└" + "┴".join("─" * width for width in col_widths) + "┘")
    
    # add truncation note if needed
    if len(results) > 10:
        table_lines.append(f"\n({len(results)} total results, showing first 10)")
    
    return "\n".join(table_lines)

def format_cypher_query(query: str) -> str:
    """format cypher query in a nice code block"""
    # calculate width based on query length + padding
    query_width = len(query) + 4
    min_width = len("generated cypher:") + 4
    width = max(query_width, min_width, 50)
    
    lines = []
    lines.append("generated cypher:")
    lines.append("┌" + "─" * (width - 2) + "┐")
    lines.append(f"│ {query:<{width - 4}} │")
    lines.append("└" + "─" * (width - 2) + "┘")
    
    return "\n".join(lines)

def format_response(question: str, cypher_query: str, results: list) -> str:
    output = []
    
    output.append(f"question: {question}")
    output.append("")
    
    # display cypher query prominently
    output.append(format_cypher_query(cypher_query))
    output.append("")
    
    if not results:
        output.append("no results found")
    elif len(results) == 1 and results[0].get('status') == 'database_error':
        # handle database error responses
        error = results[0]
        error_type = error.get('error_type', 'unknown')
        message = error.get('message', 'Database error occurred')
        
        output.append("⚠️  database error:")
        output.append(f"┌─ {message}")
        output.append("")
        
        # provide helpful suggestions based on error type
        if error_type == 'connection_failed':
            output.append("suggestions:")
            output.append("• Check if Neo4j is running: docker ps")
            output.append("• Start Neo4j: docker start neo4j-ai") 
            output.append("• Check connection: http://localhost:7474")
        elif error_type == 'authentication_failed':
            output.append("suggestions:")
            output.append("• Check NEO4J_USER and NEO4J_PASSWORD in .env file")
            output.append("• Verify credentials in Neo4j browser")
        
        output.append("")
        output.append("💡 tip: you can enable mock mode to continue testing")
        output.append("   set USE_MOCK_NEO4J=true in .env file")
    elif len(results) == 1 and results[0].get('status') == 'connection_failed':
        # legacy fallback handling
        output.append("note: using sample data (database not connected)")
        output.append("sample results:")
        output.append("- alice (person)")
        output.append("- bob (person)")  
        output.append("- usa (country)")
    else:
        output.append("results:")
        output.append(format_table(results))
    
    return "\n".join(output) 