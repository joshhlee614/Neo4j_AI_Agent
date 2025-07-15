#!/usr/bin/env python3

import json
import os

def load_data(file_path="data/nypd/data/2025_nypd.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def flatten(record):
    result = {}
    
    for key, value in record.items():
        if isinstance(value, dict):
            for nested_key, nested_value in value.items():
                result[f"{key}_{nested_key}"] = nested_value
        elif isinstance(value, list):
            if len(value) == 0:
                result[key] = None
            elif len(value) == 1:
                result[key] = value[0]
            else:
                result[key] = str(value)
        else:
            result[key] = value
    
    return result

def process_data(data):
    return [flatten(record) for record in data]

def main():
    print("=== Flattening NYPD Dataset ===\n")
    
    data = load_data()
    print(f"Original: {len(data)} records")
    
    flattened = process_data(data)
    print(f"Flattened: {len(flattened)} records")
    
    if data and flattened:
        orig = data[0]
        flat = flattened[0]
        
        print(f"\nOriginal keys: {len(orig.keys())}")
        print(f"Flattened keys: {len(flat.keys())}")
        
        print("\nFlattened structure:")
        for key in sorted(flat.keys()):
            value = flat[key]
            vtype = type(value).__name__
            
            if isinstance(value, str) and len(value) > 50:
                sample = f'"{value[:47]}..."'
            else:
                sample = repr(value)
            
            print(f"  {key:25} ({vtype:10}) = {sample}")
    
    output_file = "data/nypd/data/flattened_nypd_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flattened, f, indent=2)
    
    print(f"\nSaved to: {output_file}")

if __name__ == "__main__":
    main() 