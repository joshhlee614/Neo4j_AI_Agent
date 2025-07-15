#!/usr/bin/env python3
"""
Inspect column properties in NYPD dataset
"""

import json
from collections import defaultdict, Counter

def load_nypd_dataset(file_path: str = "data/2025_nypd.json"):
    """Load the NYPD dataset"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def analyze_column_properties(data, sample_size=10000):
    """Analyze properties of each column"""
    print(f"Analyzing {len(data)} records (sampling {min(sample_size, len(data))} for unique values)")
    
    # sample data for performance
    sample_data = data[:sample_size] if len(data) > sample_size else data
    
    column_info = {}
    
    # collect all possible keys
    all_keys = set()
    for record in sample_data:
        all_keys.update(record.keys())
    
    for key in sorted(all_keys):
        values = []
        types = []
        
        # collect values and types for this key
        for record in sample_data:
            value = record.get(key)
            values.append(value)
            types.append(type(value).__name__)
        
        # analyze the column
        non_null_values = [v for v in values if v is not None]
        unique_values = set(non_null_values)
        type_counts = Counter(types)
        
        # determine primary type
        primary_type = type_counts.most_common(1)[0][0] if type_counts else 'unknown'
        
        # calculate statistics
        total_count = len(values)
        null_count = total_count - len(non_null_values)
        unique_count = len(unique_values)
        null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
        
        # categorize field type
        field_category = categorize_field(key, unique_values, primary_type, unique_count, total_count)
        
        column_info[key] = {
            'primary_type': primary_type,
            'unique_count': unique_count,
            'null_count': null_count,
            'null_percentage': round(null_percentage, 1),
            'category': field_category,
            'sample_values': list(unique_values)[:5] if unique_values else []
        }
    
    return column_info

def categorize_field(key, unique_values, primary_type, unique_count, total_count):
    """Categorize field based on its properties"""
    
    # identifier patterns
    if key.lower().endswith('id') or key.lower().endswith('num') or key.lower().endswith('code'):
        return 'identifier'
    
    # date/time patterns
    if 'date' in key.lower() or 'time' in key.lower():
        return 'temporal'
    
    # location patterns
    if any(loc in key.lower() for loc in ['coord', 'lat', 'lon', 'precinct', 'borough']):
        return 'location'
    
    # categorical (low unique count relative to total)
    if primary_type == 'str' and unique_count <= 50:
        return 'categorical'
    
    # numeric
    if primary_type == 'int' or primary_type == 'float':
        return 'numeric'
    
    # high cardinality string
    if primary_type == 'str' and unique_count > 50:
        return 'text'
    
    # default
    return 'other'

def print_column_summary(column_info):
    """Print a formatted summary of column properties"""
    print("\n" + "="*80)
    print("COLUMN PROPERTY ANALYSIS")
    print("="*80)
    
    print(f"{'Column Name':<25} {'Type':<10} {'Unique':<8} {'Null%':<8} {'Category':<12} {'Sample Values'}")
    print("-"*80)
    
    for key, info in column_info.items():
        sample_str = str(info['sample_values'])[:40] + "..." if len(str(info['sample_values'])) > 40 else str(info['sample_values'])
        
        print(f"{key:<25} {info['primary_type']:<10} {info['unique_count']:<8} {info['null_percentage']:<8} {info['category']:<12} {sample_str}")

def categorize_by_type(column_info):
    """Group columns by their categories"""
    categories = defaultdict(list)
    
    for key, info in column_info.items():
        categories[info['category']].append(key)
    
    print("\n" + "="*50)
    print("COLUMNS BY CATEGORY")
    print("="*50)
    
    for category, columns in categories.items():
        print(f"\n{category.upper()} ({len(columns)} columns):")
        for col in columns:
            print(f"  - {col}")

def main():
    """Main function to inspect column properties"""
    print("=== NYPD Dataset Column Inspector ===\n")
    
    # load dataset
    data = load_nypd_dataset()
    
    # analyze column properties
    column_info = analyze_column_properties(data)
    
    # print summary
    print_column_summary(column_info)
    
    # categorize columns
    categorize_by_type(column_info)
    
    # save analysis
    with open('data/column_analysis.json', 'w') as f:
        json.dump(column_info, f, indent=2)
    
    print(f"\nColumn analysis saved to: data/column_analysis.json")
    print("Ready for null field handling analysis")

if __name__ == "__main__":
    main() 