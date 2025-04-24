#!/usr/bin/env python
import os
import time
import subprocess
from huggingface_hub import HfApi

# Get token from environment or from stored token
def get_token():
    # Try to get token from cached location
    try:
        token_path = os.path.expanduser("~/.cache/huggingface/token")
        if os.path.exists(token_path):
            with open(token_path, "r") as f:
                return f.read().strip()
    except:
        pass
    
    # If that fails, try using the huggingface-cli to print the token
    try:
        result = subprocess.run(["huggingface-cli", "whoami", "--token"], 
                              capture_output=True, text=True, check=True)
        if result.stdout:
            return result.stdout.strip()
    except:
        pass
    
    return None

# Get the token
token = get_token()
if not token:
    print("No Hugging Face token found. Please login using 'huggingface-cli login'")
    exit(1)

# Hugging Face repo ID
repo_id = "aliss77777/IFX-sandbox"

# Initialize the Hugging Face API with the token
api = HfApi(token=token)

print(f"Restarting Space: {repo_id}")

try:
    # Restart the Space
    api.restart_space(repo_id=repo_id)
    print(f"✓ Space restart request sent!")
    print(f"The Space should restart shortly. You can check its status at: https://huggingface.co/spaces/{repo_id}")
except Exception as e:
    print(f"Error restarting Space: {str(e)}")
    exit(1) 