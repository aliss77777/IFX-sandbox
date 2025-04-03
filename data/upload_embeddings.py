import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Neo4j connection details
NEO4J_URI = os.getenv('AURA_CONNECTION_URI')
NEO4J_USER = os.getenv('AURA_USERNAME')
NEO4J_PASS = os.getenv('AURA_PASSWORD')

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASS]):
    raise ValueError("Missing required Neo4j credentials in .env file")

def restore_game_data_with_embeddings():
    # Path to the CSV files
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    game_data_file = os.path.join(SCRIPT_DIR, "niners_output/schedule_with_result.csv")
    embeddings_file = os.path.join(SCRIPT_DIR, "niners_output/schedule_with_result_embedding.csv")
    
    print(f"Reading game data from: {game_data_file}")
    print(f"Reading embeddings from: {embeddings_file}")
    
    # Read the CSV files
    game_df = pd.read_csv(game_data_file)
    embeddings_df = pd.read_csv(embeddings_file)
    
    # Get the embedding columns (all columns starting with 'dim_')
    embedding_cols = [col for col in embeddings_df.columns if col.startswith('dim_')]
    
    # Merge the game data with embeddings on game_id
    merged_df = pd.merge(game_df, embeddings_df, on='game_id', how='left')
    
    print(f"Merged {len(game_df)} games with {len(embeddings_df)} embeddings")
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    def update_game_data(tx, game_id, game_data, embedding):
        # First, create/update the game node with basic properties
        tx.run("""
            MERGE (g:Game {game_id: $game_id})
            SET g.date = $date,
                g.home_team = $home_team,
                g.away_team = $away_team,
                g.home_score = $home_score,
                g.away_score = $away_score,
                g.result = $result
        """, game_id=game_id, 
             date=game_data['date'],
             home_team=game_data['home_team'],
             away_team=game_data['away_team'],
             home_score=game_data['home_score'],
             away_score=game_data['away_score'],
             result=game_data['result'])
        
        # Then set the vector embedding using the proper Neo4j vector operation
        tx.run("""
            MATCH (g:Game {game_id: $game_id})
            CALL db.create.setNodeVectorProperty(g, 'gameEmbedding', $embedding)
            YIELD node
            RETURN node
        """, game_id=game_id, embedding=embedding)

    # Process each game and update Neo4j
    with driver.session() as session:
        for _, row in merged_df.iterrows():
            # Convert embedding columns to list
            embedding = row[embedding_cols].values.tolist()
            
            # Create game data dictionary
            game_data = {
                'date': row['date'],
                'home_team': row['home_team'],
                'away_team': row['away_team'],
                'home_score': row['home_score'],
                'away_score': row['away_score'],
                'result': row['result']
            }
            
            # Update the game data in Neo4j
            session.execute_write(update_game_data, row['game_id'], game_data, embedding)
            
    print("Finished updating game data in Neo4j")
    driver.close()

if __name__ == "__main__":
    restore_game_data_with_embeddings()