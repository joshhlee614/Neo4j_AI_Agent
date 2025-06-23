def run_build_pipeline(input_file: str) -> None:
    """orchestrates the full pipeline: text -> schema -> cypher -> neo4j"""
    pass


def main():
    """cli entry point for build_graph.py"""
    import sys
    if len(sys.argv) != 2:
        print("usage: python build_graph.py <input_file>")
        return
    
    input_file = sys.argv[1]
    run_build_pipeline(input_file)


if __name__ == "__main__":
    main() 