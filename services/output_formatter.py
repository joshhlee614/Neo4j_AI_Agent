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
        output.append(format_table(results))
    
    return "\n".join(output) 