import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables from .env file (for API key)
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    """Get embedding for text using OpenAI's text-embedding-3-small."""
    if pd.isna(text) or text == "Specific game details are not available.":
        # Return an array of zeros for missing data or non-specific summaries
        return [0] * 1536  # text-embedding-3-small produces 1536-dimensional embeddings
    
    response = client.embeddings.create(
        input=text.strip(),
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def main():
    # Read the CSV file
    input_path = "merged/data/niners_output/schedule_with_result.csv"
    output_path = "merged/data/niners_output/schedule_with_result_embedding.csv"
    
    print(f"Reading from {input_path}")
    df = pd.read_csv(input_path)
    
    # Check if Summary column exists
    if "Summary" not in df.columns:
        print("Error: 'Summary' column not found in the CSV file.")
        return
    
    # Generate embeddings for each summary
    print("Generating embeddings...")
    
    # Add embeddings directly to the original dataframe
    df['embedding'] = df['Summary'].apply(get_embedding)
    
    # Save to CSV
    print(f"Saving embeddings to {output_path}")
    df.to_csv(output_path, index=False)
    print("Done!")

if __name__ == "__main__":
    main()