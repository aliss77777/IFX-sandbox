#!/usr/bin/env python3
"""
update_game_nodes.py - Updates existing Game nodes in Neo4j with additional attributes

This script reads game data from the schedule_with_result_april_11.csv file and updates
existing Game nodes in Neo4j with the following attributes:
- home_team_logo_url
- away_team_logo_url
- game_id
- highlight_video_url

The script uses game_id as the primary key for matching and updating nodes.
"""

import os
import sys
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Add parent directory to path to access neo4j_ingestion.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.append(parent_dir)

# Set up paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../../.."))
DATA_DIR = os.path.join(PROJECT_DIR, "ifx-sandbox/data")
SCHEDULE_DIR = os.path.join(DATA_DIR, "april_11_multimedia_data_collect", "new_final_april 11")
SCHEDULE_FILE = os.path.join(SCHEDULE_DIR, "schedule_with_result_april_11.csv")

# Load environment variables from ifx-sandbox/.env
ENV_FILE = os.path.join(PROJECT_DIR, "ifx-sandbox/.env")
load_dotenv(ENV_FILE)
print(f"Loading environment variables from: {ENV_FILE}")

# Neo4j connection credentials
NEO4J_URI = os.getenv('AURA_CONNECTION_URI')
NEO4J_USER = os.getenv('AURA_USERNAME')
NEO4J_PASS = os.getenv('AURA_PASSWORD')

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASS]):
    print(f"Error: Missing required Neo4j credentials in {ENV_FILE}")
    print(f"Required variables: AURA_CONNECTION_URI, AURA_USERNAME, AURA_PASSWORD")
    raise ValueError("Missing required Neo4j credentials in .env file")

def clean_row_dict(row):
    """Convert pandas row to dict and replace NaN with None"""
    return {k: None if pd.isna(v) else v for k, v in row.items()}

def update_game_nodes():
    """
    Updates existing Game nodes with additional attributes from the schedule CSV.
    Uses game_id as the primary key for matching.
    """
    print(f"Loading schedule data from: {SCHEDULE_FILE}")
    
    # Check if the file exists
    if not os.path.exists(SCHEDULE_FILE):
        print(f"Error: Schedule file not found at {SCHEDULE_FILE}")
        return False
    
    # Load the schedule data
    try:
        schedule_df = pd.read_csv(SCHEDULE_FILE)
        print(f"Loaded {len(schedule_df)} games from CSV")
    except Exception as e:
        print(f"Error loading schedule CSV: {str(e)}")
        return False
    
    # Verify required columns exist
    required_columns = ['game_id', 'home_team_logo_url', 'away_team_logo_url', 'highlight_video_url']
    missing_columns = [col for col in required_columns if col not in schedule_df.columns]
    
    if missing_columns:
        print(f"Error: Missing required columns in CSV: {', '.join(missing_columns)}")
        return False
    
    # Connect to Neo4j
    print(f"Connecting to Neo4j at {NEO4J_URI}")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    # Check connection
    try:
        with driver.session() as session:
            result = session.run("MATCH (g:Game) RETURN count(g) as count")
            game_count = result.single()["count"]
            print(f"Found {game_count} Game nodes in Neo4j")
    except Exception as e:
        print(f"Error connecting to Neo4j: {str(e)}")
        driver.close()
        return False
    
    # Update game nodes
    success_count = 0
    error_count = 0
    
    with driver.session() as session:
        for _, row in schedule_df.iterrows():
            params = clean_row_dict(row)
            
            # Skip if game_id is missing
            if not params.get('game_id'):
                error_count += 1
                print(f"Skipping row {_ + 1}: Missing game_id")
                continue
            
            # Update query
            query = """
            MATCH (g:Game {game_id: $game_id})
            SET g.home_team_logo_url = $home_team_logo_url,
                g.away_team_logo_url = $away_team_logo_url,
                g.highlight_video_url = $highlight_video_url
            RETURN g.game_id as game_id
            """
            
            try:
                result = session.run(query, params)
                updated_game = result.single()
                
                if updated_game:
                    success_count += 1
                    if success_count % 5 == 0 or success_count == 1:
                        print(f"Updated {success_count} games...")
                else:
                    error_count += 1
                    print(f"Warning: Game with ID {params['game_id']} not found in Neo4j")
            except Exception as e:
                error_count += 1
                print(f"Error updating game {params.get('game_id')}: {str(e)}")
    
    # Close the driver
    driver.close()
    
    # Print summary
    print("\nUpdate Summary:")
    print(f"Total games in CSV: {len(schedule_df)}")
    print(f"Successfully updated: {success_count}")
    print(f"Errors/not found: {error_count}")
    
    # Verify updates
    if success_count > 0:
        print("\nVerifying updates...")
        verify_updates()
    
    return success_count > 0

def verify_updates():
    """Verify that game nodes were updated with the new attributes"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    with driver.session() as session:
        # Check for games with logo URLs
        logo_query = """
        MATCH (g:Game)
        WHERE g.home_team_logo_url IS NOT NULL AND g.away_team_logo_url IS NOT NULL
        RETURN count(g) as count
        """
        
        logo_result = session.run(logo_query)
        logo_count = logo_result.single()["count"]
        
        # Check for games with highlight URLs
        highlight_query = """
        MATCH (g:Game)
        WHERE g.highlight_video_url IS NOT NULL
        RETURN count(g) as count
        """
        
        highlight_result = session.run(highlight_query)
        highlight_count = highlight_result.single()["count"]
        
        print(f"Games with logo URLs: {logo_count}")
        print(f"Games with highlight URLs: {highlight_count}")
    
    driver.close()

def main():
    print("=== Game Node Update Tool ===")
    print("This script will update existing Game nodes in Neo4j with additional attributes")
    print("from the schedule_with_result_april_11.csv file.")
    
    # Check for --yes flag
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        print("Automatic confirmation enabled. Proceeding with update...")
        confirmed = True
    else:
        # Confirm with user
        user_input = input("\nDo you want to proceed with the update? (y/n): ")
        confirmed = user_input.lower() == 'y'
    
    if not confirmed:
        print("Update cancelled.")
        return
    
    # Run the update
    success = update_game_nodes()
    
    if success:
        print("\n✅ Game nodes updated successfully!")
    else:
        print("\n❌ Game node update failed. Please check the errors above.")

if __name__ == "__main__":
    main() 