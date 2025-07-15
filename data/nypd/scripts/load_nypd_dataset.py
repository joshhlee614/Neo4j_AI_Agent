#!/usr/bin/env python3

import json
import os

def load_data(file_path="data/nypd/data/2025_nypd.json"):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {file_path}")
        print(f"Records: {len(data)}")
        
        if data:
            record = data[0]
            print(f"\nFields ({len(record.keys())}):")
            for key in sorted(record.keys()):
                value = record[key]
                vtype = type(value).__name__
                
                if isinstance(value, str) and len(value) > 50:
                    sample = f'"{value[:47]}..."'
                else:
                    sample = repr(value)
                
                print(f"  {key:25} ({vtype:10}) = {sample}")
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=== NYPD Dataset Loader ===\n")
    
    dataset = load_data()
    
    if dataset:
        print(f"\nLoaded {len(dataset)} records")
    else:
        print("\nFailed to load dataset")

if __name__ == "__main__":
    main() 