"""
Dynamic schema discovery for Neo4j knowledge graphs.
This module automatically discovers the actual schema of any Neo4j database
without requiring hardcoded knowledge.
"""

import json
import os
import sys

# add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.neo4j_service import run_cypher_real


def discover_node_types():
    """Discover all node types and their properties in the database"""
    query = """
    MATCH (n) 
    WITH labels(n) as labels, keys(n) as props, count(*) as count
    WHERE size(labels) > 0
    RETURN labels, props, count
    ORDER BY count DESC
    """
    
    results = run_cypher_real(query)
    node_types = {}
    
    for record in results:
        labels = record['labels']
        props = record['props']
        count = record['count']
        
        # use the first label as the primary type
        if labels:
            primary_label = labels[0]
            if primary_label not in node_types:
                node_types[primary_label] = {
                    'properties': set(),
                    'count': 0,
                    'sample_properties': {}
                }
            
            # add properties to the set
            node_types[primary_label]['properties'].update(props)
            node_types[primary_label]['count'] += count
    
    # convert sets to lists for json serialization
    for node_type in node_types.values():
        node_type['properties'] = list(node_type['properties'])
    
    return node_types


def discover_relationships():
    """Discover all relationship types and their patterns"""
    query = """
    MATCH (a)-[r]->(b)
    WITH 
        CASE WHEN size(labels(a)) > 0 THEN labels(a)[0] ELSE 'UnlabeledNode' END as from_label,
        type(r) as rel_type,
        CASE WHEN size(labels(b)) > 0 THEN labels(b)[0] ELSE 'UnlabeledNode' END as to_label,
        count(*) as count
    RETURN from_label, rel_type, to_label, count
    ORDER BY count DESC
    """
    
    results = run_cypher_real(query)
    relationships = {}
    
    for record in results:
        from_label = record['from_label']
        rel_type = record['rel_type']
        to_label = record['to_label']
        count = record['count']
        
        if rel_type not in relationships:
            relationships[rel_type] = {
                'patterns': [],
                'total_count': 0
            }
        
        relationships[rel_type]['patterns'].append({
            'from': from_label,
            'to': to_label,
            'count': count
        })
        relationships[rel_type]['total_count'] += count
    
    return relationships


def get_sample_data():
    """Get sample data for each node type"""
    node_types = discover_node_types()
    samples = {}
    
    for node_type in node_types.keys():
        query = f"""
        MATCH (n:{node_type})
        RETURN n
        LIMIT 3
        """
        
        try:
            results = run_cypher_real(query)
            samples[node_type] = []
            
            for record in results:
                node = record['n']
                # Extract properties from the node
                if hasattr(node, '_properties'):
                    samples[node_type].append(dict(node._properties))
                elif hasattr(node, 'items'):
                    samples[node_type].append(dict(node.items()))
                else:
                    # Fallback for different node representations
                    samples[node_type].append(str(node))
        
        except Exception as e:
            print(f"Error getting samples for {node_type}: {e}")
            samples[node_type] = []
    
    return samples


def generate_dynamic_examples():
    """Generate query examples based on the actual database schema"""
    node_types = discover_node_types()
    relationships = discover_relationships()
    samples = get_sample_data()
    
    examples = []
    
    # Basic node queries
    for node_type, info in node_types.items():
        if info['count'] > 0:
            examples.append({
                'question': f"List all {node_type.lower()}s",
                'cypher': f"MATCH (n:{node_type}) RETURN n.name LIMIT 10"
            })
            
            # If there are properties, add a property-based query
            if 'name' in info['properties']:
                examples.append({
                    'question': f"Find {node_type.lower()} by name",
                    'cypher': f'MATCH (n:{node_type}) WHERE toLower(n.name) CONTAINS "example" RETURN n.name'
                })
    
    # Relationship queries
    for rel_type, info in relationships.items():
        if info['patterns']:
            pattern = info['patterns'][0]  # Use the most common pattern
            from_type = pattern['from']
            to_type = pattern['to']
            
            examples.append({
                'question': f"Show {from_type} {rel_type.lower().replace('_', ' ')} relationships",
                'cypher': f"MATCH (a:{from_type})-[:{rel_type}]->(b:{to_type}) RETURN a.name, b.name LIMIT 10"
            })
    
    # Meta queries
    examples.extend([
        {
            'question': "What types of nodes are in the database?",
            'cypher': "MATCH (n) RETURN DISTINCT labels(n) AS node_types"
        },
        {
            'question': "What relationships exist?",
            'cypher': "MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationship_type"
        },
        {
            'question': "How many nodes are there?",
            'cypher': "MATCH (n) RETURN count(n)"
        }
    ])
    
    return examples


def generate_schema_description():
    """Generate a natural language description of the schema"""
    node_types = discover_node_types()
    relationships = discover_relationships()
    
    description = "database schema\n\n"
    
    # node types
    description += "node types:\n"
    for node_type, info in node_types.items():
        description += f"- **{node_type}**: {info['count']} nodes\n"
        if info['properties']:
            description += f"  - Properties: {', '.join(info['properties'])}\n"
    
    description += "\nrelationships:\n"
    for rel_type, info in relationships.items():
        description += f"- **{rel_type}**: {info['total_count']} relationships\n"
        for pattern in info['patterns'][:3]:  # Show top 3 patterns
            description += f"  - {pattern['from']} → {pattern['to']} ({pattern['count']})\n"
    
    return description


def get_database_stats():
    """Get basic database statistics"""
    stats = {}
    
    # Total nodes
    result = run_cypher_real("MATCH (n) RETURN count(n) as total_nodes")
    stats['total_nodes'] = result[0]['total_nodes'] if result else 0
    
    # Total relationships
    result = run_cypher_real("MATCH ()-[r]->() RETURN count(r) as total_relationships")
    stats['total_relationships'] = result[0]['total_relationships'] if result else 0
    
    # Node type counts
    stats['node_types'] = discover_node_types()
    
    # Relationship type counts
    stats['relationships'] = discover_relationships()
    
    return stats


def main():
    """CLI interface for testing schema discovery"""
    print("Discovering database schema...")
    
    stats = get_database_stats()
    print(f"\nDatabase Statistics:")
    print(f"Total nodes: {stats['total_nodes']}")
    print(f"Total relationships: {stats['total_relationships']}")
    
    print(f"\nNode types: {len(stats['node_types'])}")
    for node_type, info in stats['node_types'].items():
        print(f"  {node_type}: {info['count']} nodes")
    
    print(f"\nRelationship types: {len(stats['relationships'])}")
    for rel_type, info in stats['relationships'].items():
        print(f"  {rel_type}: {info['total_count']} relationships")
    
    print("\nGenerated schema description:")
    print(generate_schema_description())
    
    print("\nDynamic examples:")
    examples = generate_dynamic_examples()
    for i, example in enumerate(examples[:5]):  # Show first 5
        print(f"{i+1}. Q: {example['question']}")
        print(f"   A: {example['cypher']}")


if __name__ == "__main__":
    main() 