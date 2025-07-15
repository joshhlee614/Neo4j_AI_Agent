#!/usr/bin/env python3

import json
from collections import defaultdict, Counter

def load_data(file_path="data/nypd/data/2025_nypd.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_columns(data, sample_size=10000):
    print(f"Analyzing {len(data)} records (sampling {min(sample_size, len(data))})")
    
    sample_data = data[:sample_size] if len(data) > sample_size else data
    
    info = {}
    
    keys = set()
    for record in sample_data:
        keys.update(record.keys())
    
    for key in sorted(keys):
        values = []
        types = []
        
        for record in sample_data:
            value = record.get(key)
            values.append(value)
            types.append(type(value).__name__)
        
        non_null = [v for v in values if v is not None]
        unique = set(non_null)
        type_counts = Counter(types)
        
        primary_type = type_counts.most_common(1)[0][0] if type_counts else 'unknown'
        
        total = len(values)
        null_count = total - len(non_null)
        unique_count = len(unique)
        null_pct = (null_count / total) * 100 if total > 0 else 0
        
        category = categorize(key, unique, primary_type, unique_count, total)
        
        info[key] = {
            'primary_type': primary_type,
            'unique_count': unique_count,
            'null_count': null_count,
            'null_percentage': round(null_pct, 1),
            'category': category,
            'sample_values': list(unique)[:5] if unique else []
        }
    
    return info

def categorize(key, unique_values, primary_type, unique_count, total_count):
    if key.lower().endswith('id') or key.lower().endswith('num') or key.lower().endswith('code'):
        return 'identifier'
    
    if 'date' in key.lower() or 'time' in key.lower():
        return 'temporal'
    
    if any(loc in key.lower() for loc in ['coord', 'lat', 'lon', 'precinct', 'borough']):
        return 'location'
    
    if primary_type == 'str' and unique_count <= 50:
        return 'categorical'
    
    if primary_type == 'int' or primary_type == 'float':
        return 'numeric'
    
    if primary_type == 'str' and unique_count > 50:
        return 'text'
    
    return 'other'

def print_summary(info):
    print("\n" + "="*80)
    print("COLUMN PROPERTY ANALYSIS")
    print("="*80)
    
    print(f"{'Column Name':<25} {'Type':<10} {'Unique':<8} {'Null%':<8} {'Category':<12} {'Sample Values'}")
    print("-"*80)
    
    for key, data in info.items():
        sample_str = str(data['sample_values'])[:40] + "..." if len(str(data['sample_values'])) > 40 else str(data['sample_values'])
        
        print(f"{key:<25} {data['primary_type']:<10} {data['unique_count']:<8} {data['null_percentage']:<8} {data['category']:<12} {sample_str}")

def print_by_category(info):
    categories = defaultdict(list)
    
    for key, data in info.items():
        categories[data['category']].append(key)
    
    print("\n" + "="*50)
    print("COLUMNS BY CATEGORY")
    print("="*50)
    
    for category, columns in categories.items():
        print(f"\n{category.upper()} ({len(columns)} columns):")
        for col in columns:
            print(f"  - {col}")

def main():
    print("=== NYPD Dataset Column Inspector ===\n")
    
    data = load_data()
    info = analyze_columns(data)
    
    print_summary(info)
    print_by_category(info)
    
    with open('data/nypd/data/column_analysis.json', 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"\nSaved to: data/nypd/data/column_analysis.json")

if __name__ == "__main__":
    main() 