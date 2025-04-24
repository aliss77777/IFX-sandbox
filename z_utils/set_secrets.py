#!/usr/bin/env python
import os
import subprocess
from dotenv import load_dotenv
from huggingface_hub import HfApi

# Load environment variables from .env file
load_dotenv()

# Get Neo4j credentials
AURA_CONNECTION_URI = os.environ.get("AURA_CONNECTION_URI")
AURA_USERNAME = os.environ.get("AURA_USERNAME")
AURA_PASSWORD = os.environ.get("AURA_PASSWORD")

# Get OpenAI credentials
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL")

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

print("Setting secrets for", repo_id)

# Set each secret
try:
    # Set Neo4j credentials
    api.add_space_secret(repo_id=repo_id, key="AURA_CONNECTION_URI", value=AURA_CONNECTION_URI)
    print("✓ Set AURA_CONNECTION_URI")
    
    api.add_space_secret(repo_id=repo_id, key="AURA_USERNAME", value=AURA_USERNAME)
    print("✓ Set AURA_USERNAME")
    
    api.add_space_secret(repo_id=repo_id, key="AURA_PASSWORD", value=AURA_PASSWORD)
    print("✓ Set AURA_PASSWORD")
    
    # Set OpenAI credentials
    api.add_space_secret(repo_id=repo_id, key="OPENAI_API_KEY", value=OPENAI_API_KEY)
    print("✓ Set OPENAI_API_KEY")
    
    api.add_space_secret(repo_id=repo_id, key="OPENAI_MODEL", value=OPENAI_MODEL)
    print("✓ Set OPENAI_MODEL")
    
    print("\nAll secrets set successfully!")
except Exception as e:
    print(f"Error setting secrets: {str(e)}")
    exit(1) 