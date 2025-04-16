#!/usr/bin/env python3
"""
update_player_nodes.py - Updates existing Player nodes in Neo4j with additional attributes

This script reads player data from the roster_april_11.csv file and updates
existing Player nodes in Neo4j with the following attributes:
- headshot_url
- instagram_url
- highlight_video_url

The script uses Player_id as the primary key for matching and updating nodes.
"""

import os
import sys
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Define base project directory relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct absolute path to project root (ifx-sandbox) based on known workspace structure
# This assumes the script is always located at the same relative depth
WORKSPACE_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../../..")) # Goes up 5 levels to workspace root
PROJECT_DIR = os.path.join(WORKSPACE_ROOT, "ifx-sandbox") # Specify ifx-sandbox within workspace

# Add parent directory (ifx-sandbox) to path if needed for imports, though unlikely needed here
# sys.path.append(PROJECT_DIR)

# Set up paths using PROJECT_DIR
DATA_DIR = os.path.join(PROJECT_DIR, "data")
ROSTER_DATA_DIR = os.path.join(DATA_DIR, "april_11_multimedia_data_collect", "new_final_april 11")
ROSTER_FILE = os.path.join(ROSTER_DATA_DIR, "roster_april_11.csv")

# Load environment variables from ifx-sandbox/.env
ENV_FILE = os.path.join(PROJECT_DIR, ".env")

if not os.path.exists(ENV_FILE):
    print(f"Error: .env file not found at {ENV_FILE}")
    # Attempt fallback if PROJECT_DIR might be wrong
    alt_project_dir = os.path.join(os.path.abspath(os.path.join(SCRIPT_DIR, "../../../../../")), "ifx-sandbox") # Go up 6 and specify
    alt_env_file = os.path.join(alt_project_dir, ".env")
    if os.path.exists(alt_env_file):
        print("Fallback: Found .env using alternative path calculation.")
        ENV_FILE = alt_env_file
    else:
        sys.exit(1)

# Explicitly pass the path to load_dotenv
load_dotenv(dotenv_path=ENV_FILE)
print(f"Loading environment variables from: {ENV_FILE}")

# Neo4j connection credentials
NEO4J_URI = os.getenv('AURA_CONNECTION_URI')
NEO4J_USER = os.getenv('AURA_USERNAME')
NEO4J_PASS = os.getenv('AURA_PASSWORD')

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASS]):
    print(f"Error: Missing required Neo4j credentials in {ENV_FILE}")
    print(f"Required variables: AURA_CONNECTION_URI, AURA_USERNAME, AURA_PASSWORD")
    sys.exit(1)

def clean_row_dict(row):
    """Convert pandas row to dict and replace NaN or empty strings with None"""
    return {k: None if pd.isna(v) or v == '' else v for k, v in row.items()}

def update_player_nodes():
    """
    Updates existing Player nodes with additional attributes from the roster CSV.
    Uses Player_id as the primary key for matching.
    """
    print(f"Loading player roster data from: {ROSTER_FILE}")

    # Check if the file exists
    if not os.path.exists(ROSTER_FILE):
        print(f"Error: Roster file not found at {ROSTER_FILE}")
        return False

    # Load the roster data
    try:
        roster_df = pd.read_csv(ROSTER_FILE)
        print(f"Loaded {len(roster_df)} players from CSV")
    except Exception as e:
        print(f"Error loading roster CSV: {str(e)}")
        return False

    # Verify required columns exist
    required_columns = ['player_id', 'headshot_url', 'instagram_url', 'highlight_video_url']
    missing_columns = [col for col in required_columns if col not in roster_df.columns]

    if missing_columns:
        print(f"Error: Missing required columns in CSV: {', '.join(missing_columns)}")
        return False

    # Connect to Neo4j
    print(f"Connecting to Neo4j at {NEO4J_URI}")
    driver = None # Initialize driver to None
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        print("Neo4j connection successful.")
        with driver.session() as session:
            result = session.run("MATCH (p:Player) RETURN count(p) as count")
            player_count = result.single()["count"]
            print(f"Found {player_count} Player nodes in Neo4j")
    except Exception as e:
        print(f"Error connecting to or querying Neo4j: {str(e)}")
        if driver:
            driver.close()
        return False

    # Update player nodes
    success_count = 0
    error_count = 0

    with driver.session() as session:
        for index, row in roster_df.iterrows():
            # Use player_id (lowercase) which is the correct column name
            player_id_val = row.get('player_id')

            if not player_id_val:
                error_count += 1
                print(f"Skipping row {index + 1}: Missing player_id")
                continue

            params = clean_row_dict(row)
            # Ensure the key used for matching exists in params for the query
            params['match_player_id'] = player_id_val

            # Update query - Use correct case for property key and parameter name
            query = """
            MATCH (p:Player {player_id: $match_player_id})
            SET p.headshot_url = $headshot_url,
                p.instagram_url = $instagram_url,
                p.highlight_video_url = $highlight_video_url
            RETURN p.player_id as player_id
            """

            try:
                result = session.run(query, params)
                updated_player = result.single()

                if updated_player:
                    success_count += 1
                    if success_count % 10 == 0 or success_count == 1:
                        print(f"Updated {success_count} players...")
                else:
                    error_count += 1
                    print(f"Warning: Player with ID {player_id_val} not found in Neo4j")
            except Exception as e:
                error_count += 1
                print(f"Error updating player {player_id_val}: {str(e)}")

    # Close the driver
    driver.close()

    # Print summary
    print("\nUpdate Summary:")
    print(f"Total players in CSV: {len(roster_df)}")
    print(f"Successfully updated: {success_count}")
    print(f"Errors/not found: {error_count}")

    # Verify updates
    if success_count > 0:
        print("\nVerifying updates...")
        verify_updates()

    return success_count > 0

def verify_updates():
    """Verify that Player nodes were updated with the new attributes"""
    driver = None
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        with driver.session() as session:
            # Check for players with headshot & instagram URLs
            query1 = """
            MATCH (p:Player)
            WHERE p.headshot_url IS NOT NULL AND p.instagram_url IS NOT NULL
            RETURN count(p) as count
            """
            result1 = session.run(query1)
            count1 = result1.single()["count"]

            # Check for players with highlight URLs
            query2 = """
            MATCH (p:Player)
            WHERE p.highlight_video_url IS NOT NULL
            RETURN count(p) as count
            """
            result2 = session.run(query2)
            count2 = result2.single()["count"]

            print(f"Players with headshot & Instagram URLs: {count1}")
            print(f"Players with highlight URLs: {count2}")
    except Exception as e:
        print(f"Error during verification: {str(e)}")
    finally:
        if driver:
            driver.close()

def main():
    print("=== Player Node Update Tool ===")
    print("This script will update existing Player nodes in Neo4j with additional attributes")
    print(f"from the {ROSTER_FILE} file.")

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
    success = update_player_nodes()

    if success:
        print("\n✅ Player nodes updated successfully!")
    else:
        print("\n❌ Player node update failed. Please check the errors above.")

if __name__ == "__main__":
    main()
