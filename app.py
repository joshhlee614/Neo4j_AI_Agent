import sys
import os
from agent.agent_runner import answer_question
from builder.build_graph import run_build_pipeline


def show_usage():
    print("neo4j ai assistant")
    print()
    print("usage:")
    print("  python app.py <question>                    # ask a question")
    print("  python app.py --build <input_file>          # build knowledge graph")
    print("  python app.py --build <input_file> --ingest # build and ingest to neo4j")
    print()
    print("examples:")
    print("  python app.py \"who lives in france?\"")
    print("  python app.py --build data/knowledge_graph/sample_input.txt")
    print("  python app.py --build data/knowledge_graph/sample_input.pdf --ingest")


def main():
    if len(sys.argv) == 1 or "--help" in sys.argv or "-h" in sys.argv:
        show_usage()
        return
    
    if "--build" in sys.argv:
        try:
            build_index = sys.argv.index("--build")
            if build_index + 1 >= len(sys.argv):
                print("error: --build requires an input file")
                show_usage()
                return
            
            input_file = sys.argv[build_index + 1]
            ingest_to_neo4j = "--ingest" in sys.argv
            
            if not os.path.exists(input_file):
                print(f"error: file not found: {input_file}")
                return
            
            print("neo4j ai assistant - build mode")
            print(f"building knowledge graph from: {input_file}")
            if ingest_to_neo4j:
                print("will ingest to neo4j database")
            print("-" * 50)
            print()
            
            run_build_pipeline(input_file, ingest_to_neo4j)
            
            print()
            print("-" * 50)
            print("build complete!")
            if ingest_to_neo4j:
                print("knowledge graph is now available for querying")
                print("try: python app.py \"your question here\"")
            else:
                print("to ingest to neo4j, run with --ingest flag")
        
        except Exception as e:
            print(f"build failed: {e}")
            return
    
    else:
        print("neo4j ai assistant")
        print("ask questions about your knowledge graph")
        print("-" * 50)
        
        if len(sys.argv) > 1:
            question = " ".join(sys.argv[1:])
            print(f"your question: {question}")
        else:
            question = input("your question: ")
        
        print()
        print(answer_question(question))


if __name__ == "__main__":
    main() 