#!/usr/bin/env python3
"""
NYPD Dataset Loader
Load and explore the NYPD crime incident dataset
"""

import json
import os
from pathlib import Path

def load_nypd_dataset(file_path: str = "data/2025_nypd.json"):
    """Load the NYPD dataset JSON file"""
    
    # check if file exists
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        print("Please ensure the dataset file is in the data/ directory.")
        return None
    
    try:
        # load json file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print(f"Successfully loaded {file_path}")
        print(f"Dataset contains {len(data)} records")
        
        # display first record structure
        if data:
            first_record = data[0]
            print(f"\nFirst record keys ({len(first_record.keys())}):")
            for key in sorted(first_record.keys()):
                value = first_record[key]
                value_type = type(value).__name__
                
                # show sample value (truncated if too long)
                if isinstance(value, str) and len(value) > 50:
                    sample = f'"{value[:47]}..."'
                else:
                    sample = repr(value)
                
                print(f"  {key:25} ({value_type:10}) = {sample}")
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def main():
    """Main function to load and explore dataset"""
    print("=== NYPD Dataset Loader ===\n")
    
    # load the dataset
    dataset = load_nypd_dataset()
    
    if dataset:
        print(f"\nDataset loaded successfully!")
        print(f"Total records: {len(dataset)}")
        print(f"Ready for analysis and processing")
    else:
        print("\nFailed to load dataset!")
        print("Please check the file path and format")

if __name__ == "__main__":
    main() 