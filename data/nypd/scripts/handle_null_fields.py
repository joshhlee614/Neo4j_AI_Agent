#!/usr/bin/env python3

import json

def load_analysis():
    with open('data/nypd/data/column_analysis.json', 'r') as f:
        return json.load(f)

def get_action(field_name, null_pct, category):
    if null_pct >= 100.0:
        return 'drop', 'no data'
    
    if null_pct > 90.0:
        if category == 'identifier' and 'id' in field_name.lower():
            return 'drop', 'high null id'
        else:
            return 'drop', 'too many nulls'
    
    if null_pct >= 30.0:
        return 'keep_optional', 'incomplete'
    
    return 'keep', 'sufficient data'

def create_recommendations(info):
    recs = {
        'drop': [],
        'keep_optional': [],
        'keep': []
    }
    
    for field_name, data in info.items():
        action, reason = get_action(field_name, data['null_percentage'], data['category'])
        
        recs[action].append({
            'field': field_name,
            'null_percentage': data['null_percentage'],
            'category': data['category'],
            'reason': reason
        })
    
    return recs

def print_recommendations(recs):
    print("="*80)
    print("FIELD HANDLING RECOMMENDATIONS")
    print("="*80)
    
    for action, fields in recs.items():
        if not fields:
            continue
            
        print(f"\n{action.upper().replace('_', ' ')} ({len(fields)} fields):")
        print("-" * 50)
        
        for field in fields:
            print(f"  {field['field']:<25} {field['null_percentage']:>6.1f}% null  {field['category']:<12} - {field['reason']}")

def create_schema(info, recs):
    fields = []
    
    for field in recs['keep']:
        fields.append({
            'field': field['field'],
            'required': True,
            'category': field['category']
        })
    
    for field in recs['keep_optional']:
        fields.append({
            'field': field['field'],
            'required': False,
            'category': field['category']
        })
    
    return fields

def main():
    print("=== NYPD Dataset Null Field Handler ===\n")
    
    info = load_analysis()
    print(f"Loaded {len(info)} columns")
    
    recs = create_recommendations(info)
    print_recommendations(recs)
    
    schema = create_schema(info, recs)
    
    with open('data/nypd/data/field_recommendations.json', 'w') as f:
        json.dump(recs, f, indent=2)
    
    with open('data/nypd/data/clean_schema.json', 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"\nSummary:")
    print(f"  - DROP: {len(recs['drop'])} fields")
    print(f"  - KEEP OPTIONAL: {len(recs['keep_optional'])} fields")
    print(f"  - KEEP: {len(recs['keep'])} fields")
    print(f"  - Schema: {len(schema)} fields")
    
    print(f"\nSaved to: data/nypd/data/field_recommendations.json")
    print(f"Saved to: data/nypd/data/clean_schema.json")

if __name__ == "__main__":
    main() 