#!/usr/bin/env python3
"""
Database clearing utility for Neo4j AI Agent demos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.neo4j_service import run_cypher_real, USE_MOCK_NEO4J
from config.settings import NEO4J_URI, NEO4J_USER


def clear_database():
    """Clear all nodes and relationships from the database"""
    
    if USE_MOCK_NEO4J:
        print("Mock mode is enabled - no real database to clear")
        return
    
    print("🧹 Clearing Neo4j database...")
    print(f"Database: {NEO4J_URI}")
    print(f"User: {NEO4J_USER}")
    print()
    
    # Ask for confirmation
    confirm = input("This will DELETE ALL DATA in the database. Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("Database clearing cancelled")
        return
    
    try:
        # First, get current node count
        print("📊 Checking current database state...")
        count_result = run_cypher_real("MATCH (n) RETURN count(n) as total_nodes")
        
        if count_result and len(count_result) > 0:
            if count_result[0].get("status") == "database_error":
                print(f"Database error: {count_result[0].get('message')}")
                return
            
            total_nodes = count_result[0].get("total_nodes", 0)
            print(f"Found {total_nodes} nodes in database")
            
            if total_nodes == 0:
                print("Database is already empty")
                return
        
        # Clear all data
        print("🗑️  Deleting all nodes and relationships...")
        delete_result = run_cypher_real("MATCH (n) DETACH DELETE n")
        
        # Check if deletion was successful
        if delete_result and len(delete_result) > 0:
            if delete_result[0].get("status") == "database_error":
                print(f"Error during deletion: {delete_result[0].get('message')}")
                return
        
        # Verify deletion
        print("✔️  Verifying database is empty...")
        verify_result = run_cypher_real("MATCH (n) RETURN count(n) as remaining_nodes")
        
        if verify_result and len(verify_result) > 0:
            remaining_nodes = verify_result[0].get("remaining_nodes", -1)
            if remaining_nodes == 0:
                print("Database successfully cleared!")
                print("Ready for demo - you can now run:")
                print("   python app.py --build data/sample_input.txt --ingest")
            else:
                print(f"Warning: {remaining_nodes} nodes still remain")
        
    except Exception as e:
        print(f"Error clearing database: {e}")
        print("Try running the command manually in Neo4j Browser:")
        print("   MATCH (n) DETACH DELETE n;")


def show_database_stats():
    """Show current database statistics"""
    
    if USE_MOCK_NEO4J:
        print("Mock mode is enabled - showing mock statistics")
        print("Mock data: 3 people, 2 companies, 1 country")
        return
    
    print("Current Database Statistics:")
    print(f"Database: {NEO4J_URI}")
    print(f"User: {NEO4J_USER}")
    print()
    
    try:
        # Get node count
        count_result = run_cypher_real("MATCH (n) RETURN count(n) as total_nodes")
        if count_result and len(count_result) > 0:
            total_nodes = count_result[0].get("total_nodes", 0)
            print(f"Total nodes: {total_nodes}")
        
        # Get relationship count
        rel_result = run_cypher_real("MATCH ()-[r]->() RETURN count(r) as total_relationships")
        if rel_result and len(rel_result) > 0:
            total_rels = rel_result[0].get("total_relationships", 0)
            print(f"Total relationships: {total_rels}")
        
        # Get node types
        types_result = run_cypher_real("MATCH (n) RETURN DISTINCT labels(n) as node_types")
        if types_result:
            print("Node types:")
            for record in types_result:
                labels = record.get("node_types", [])
                if labels:
                    print(f"  - {', '.join(labels)}")
        
    except Exception as e:
        print(f"Error getting database stats: {e}")


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Neo4j Database Utility")
        print()
        print("Usage:")
        print("  python clear_database.py clear    # Clear all data")
        print("  python clear_database.py stats    # Show database statistics")
        print("  python clear_database.py help     # Show this help")
        print()
        print("Examples:")
        print("  python clear_database.py stats")
        print("  python clear_database.py clear")
        return
    
    command = sys.argv[1].lower()
    
    if command == "clear":
        clear_database()
    elif command == "stats":
        show_database_stats()
    elif command in ["help", "-h", "--help"]:
        main()  # Show usage
    else:
        print(f"Unknown command: {command}")
        print("Use 'python clear_database.py help' for usage information")


if __name__ == "__main__":
    main() 