#!/usr/bin/env python3
import os
import re
from huggingface_hub import HfApi

# Initialize the Hugging Face API
api = HfApi()

# Define the repository (Space) name
repo_id = "aliss77777/ifx-sandbox"

# Function to parse .env file
def parse_env_file(file_path):
    secrets = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse key-value pairs
            match = re.match(r'^([A-Za-z0-9_]+)\s*=\s*["\'](.*)["\']$', line)
            if match:
                key, value = match.groups()
                secrets[key] = value
            else:
                # Try without quotes
                match = re.match(r'^([A-Za-z0-9_]+)\s*=\s*(.*)$', line)
                if match:
                    key, value = match.groups()
                    secrets[key] = value
    
    return secrets

# Parse the .env file
secrets = parse_env_file('.env')

# Upload each secret to the Hugging Face Space
for key, value in secrets.items():
    try:
        print(f"Setting secret: {key}")
        api.add_space_secret(repo_id=repo_id, key=key, value=value)
        print(f"✅ Successfully set secret: {key}")
    except Exception as e:
        print(f"❌ Error setting secret {key}: {str(e)}")

print("\nAll secrets have been processed.") 