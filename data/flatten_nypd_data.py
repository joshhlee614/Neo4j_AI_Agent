#!/usr/bin/env python3
"""
Flatten nested structures in NYPD dataset
"""

import json
import os

def load_nypd_dataset(file_path: str = "data/2025_nypd.json"):
    """Load the NYPD dataset"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def flatten_record(record):
    """Flatten a single record, handling nested structures"""
    flattened = {}
    
    for key, value in record.items():
        if isinstance(value, dict):
            # flatten nested dictionaries
            for nested_key, nested_value in value.items():
                flattened[f"{key}_{nested_key}"] = nested_value
        elif isinstance(value, list):
            # handle lists - convert to string or extract elements
            if len(value) == 0:
                flattened[key] = None
            elif len(value) == 1:
                flattened[key] = value[0]
            else:
                flattened[key] = str(value)
        else:
            # keep regular values as-is
            flattened[key] = value
    
    return flattened

def flatten_dataset(data):
    """Flatten all records in the dataset"""
    flattened_data = []
    
    for record in data:
        flattened_record = flatten_record(record)
        flattened_data.append(flattened_record)
    
    return flattened_data

def main():
    """Main function to flatten dataset"""
    print("=== Flattening NYPD Dataset ===\n")
    
    # load original dataset
    data = load_nypd_dataset()
    print(f"Original dataset: {len(data)} records")
    
    # flatten nested structures
    flattened_data = flatten_dataset(data)
    print(f"Flattened dataset: {len(flattened_data)} records")
    
    # compare first record before and after
    if data and flattened_data:
        original_record = data[0]
        flattened_record = flattened_data[0]
        
        print(f"\nOriginal record keys: {len(original_record.keys())}")
        print(f"Flattened record keys: {len(flattened_record.keys())}")
        
        print("\nFlattened record structure:")
        for key in sorted(flattened_record.keys()):
            value = flattened_record[key]
            value_type = type(value).__name__
            
            # show sample value (truncated if too long)
            if isinstance(value, str) and len(value) > 50:
                sample = f'"{value[:47]}..."'
            else:
                sample = repr(value)
            
            print(f"  {key:25} ({value_type:10}) = {sample}")
    
    # save flattened dataset
    output_file = "data/flattened_nypd_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flattened_data, f, indent=2)
    
    print(f"\nFlattened dataset saved to: {output_file}")
    print("Ready for column property analysis")

if __name__ == "__main__":
    main() 