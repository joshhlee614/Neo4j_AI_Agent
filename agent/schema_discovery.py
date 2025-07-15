import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.neo4j_service import run_cypher_real


def discover_node_types():
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
        
        if labels:
            primary_label = labels[0]
            if primary_label not in node_types:
                node_types[primary_label] = {
                    'properties': set(),
                    'count': 0,
                    'sample_properties': {}
                }
            
            node_types[primary_label]['properties'].update(props)
            node_types[primary_label]['count'] += count
    
    for node_type in node_types.values():
        node_type['properties'] = list(node_type['properties'])
    
    return node_types


def discover_relationship_types():
    query = """
    MATCH (a)-[r]->(b) 
    WITH type(r) as rel_type, labels(a) as start_labels, labels(b) as end_labels, count(*) as count
    WHERE size(start_labels) > 0 AND size(end_labels) > 0
    RETURN rel_type, start_labels[0] as start_label, end_labels[0] as end_label, count
    ORDER BY count DESC
    """
    
    results = run_cypher_real(query)
    relationship_types = {}
    
    for record in results:
        rel_type = record['rel_type']
        start_label = record['start_label']
        end_label = record['end_label']
        count = record['count']
        
        if rel_type not in relationship_types:
            relationship_types[rel_type] = {
                'patterns': [],
                'count': 0
            }
        
        relationship_types[rel_type]['patterns'].append({
            'start': start_label,
            'end': end_label,
            'count': count
        })
        relationship_types[rel_type]['count'] += count
    
    return relationship_types


def get_sample_data():
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
                if hasattr(node, '_properties'):
                    samples[node_type].append(dict(node._properties))
                elif hasattr(node, 'items'):
                    samples[node_type].append(dict(node.items()))
                else:
                    samples[node_type].append(str(node))
        
        except Exception as e:
            print(f"Error getting samples for {node_type}: {e}")
            samples[node_type] = []
    
    return samples


def generate_dynamic_examples():
    try:
        node_types = discover_node_types()
        relationship_types = discover_relationship_types()
        
        examples = []
        
        if node_types:
            for node_type in list(node_types.keys())[:3]:
                examples.append({
                    'question': f"How many {node_type} nodes are there?",
                    'cypher': f"MATCH (n:{node_type}) RETURN count(n) as count"
                })
        
        if relationship_types:
            for rel_type in list(relationship_types.keys())[:2]:
                examples.append({
                    'question': f"Show me {rel_type} relationships",
                    'cypher': f"MATCH (a)-[r:{rel_type}]->(b) RETURN a, r, b LIMIT 10"
                })
        
        examples.extend([
            {
                'question': 'What types of nodes exist?',
                'cypher': 'MATCH (n) RETURN DISTINCT labels(n) as node_types'
            },
            {
                'question': 'What types of relationships exist?',
                'cypher': 'MATCH ()-[r]->() RETURN DISTINCT type(r) as relationship_types'
            }
        ])
        
        return examples
        
    except Exception as e:
        return [
            {
                'question': 'What nodes exist?',
                'cypher': 'MATCH (n) RETURN n LIMIT 10'
            }
        ]


def generate_schema_description():
    try:
        node_types = discover_node_types()
        relationship_types = discover_relationship_types()
        
        if not node_types and not relationship_types:
            return "empty database - no nodes or relationships found"
        
        description = "graph database schema:\n\n"
        
        if node_types:
            description += "node types:\n"
            for node_type, info in node_types.items():
                props = info['properties'][:5]
                description += f"  {node_type}: {props}\n"
            description += "\n"
        
        if relationship_types:
            description += "relationship types:\n"
            for rel_type, info in relationship_types.items():
                patterns = info['patterns'][:3]
                pattern_strs = [f"({p['start']})-[:{rel_type}]->({p['end']})" for p in patterns]
                description += f"  {rel_type}: {', '.join(pattern_strs)}\n"
        
        return description
        
    except Exception as e:
        return f"schema discovery failed: {str(e)}"


def get_database_stats():
    stats = {}
    
    result = run_cypher_real("MATCH (n) RETURN count(n) as total_nodes")
    stats['total_nodes'] = result[0]['total_nodes'] if result else 0
    
    result = run_cypher_real("MATCH ()-[r]->() RETURN count(r) as total_relationships")
    stats['total_relationships'] = result[0]['total_relationships'] if result else 0
    
    stats['node_types'] = discover_node_types()
    stats['relationships'] = discover_relationship_types()
    
    return stats


def main():
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
        print(f"  {rel_type}: {info['count']} relationships")
    
    print("\nGenerated schema description:")
    print(generate_schema_description())
    
    print("\nDynamic examples:")
    examples = generate_dynamic_examples()
    for i, example in enumerate(examples[:5]):
        print(f"{i+1}. Q: {example['question']}")
        print(f"   A: {example['cypher']}")


if __name__ == "__main__":
    main() 