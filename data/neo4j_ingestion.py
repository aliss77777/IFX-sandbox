############################################
# neo4j_ingestion.py
############################################

import os
import csv
import uuid
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ------------------------------------------------------------------------------
# CONFIGURE THESE TO MATCH YOUR ENVIRONMENT
# ------------------------------------------------------------------------------
NEO4J_URI = os.getenv('AURA_CONNECTION_URI')
NEO4J_USER = os.getenv('AURA_USERNAME')
NEO4J_PASS = os.getenv('AURA_PASSWORD')

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASS]):
    raise ValueError("Missing required Neo4j credentials in .env file")

# Update CSV_DIR to use absolute path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(SCRIPT_DIR, "niners_output")  # Updated to correct folder name
REL_CSV_DIR = os.path.join(SCRIPT_DIR, "relationship_csvs")

# Create directories if they don't exist
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(REL_CSV_DIR, exist_ok=True)

# Filenames for each CSV
COMMUNITIES_FILE = "fan_communities.csv"
ROSTER_FILE = "roster.csv"
#SCHEDULE_FILE = "schedule.csv"
SCHEDULE_FILE = "schedule_with_result_embedding.csv"
FANS_FILE = "fans.csv"

print("Script directory:", SCRIPT_DIR)
print("CSV directory:", CSV_DIR)
print("Looking for files in:")
print(f"- {os.path.join(CSV_DIR, COMMUNITIES_FILE)}")
print(f"- {os.path.join(CSV_DIR, ROSTER_FILE)}")
print(f"- {os.path.join(CSV_DIR, SCHEDULE_FILE)}")
print(f"- {os.path.join(CSV_DIR, FANS_FILE)}")

# Add this after the file path prints:
print("\nChecking CSV column names:")
for file_name in [COMMUNITIES_FILE, ROSTER_FILE, SCHEDULE_FILE, FANS_FILE]:
    df = pd.read_csv(os.path.join(CSV_DIR, file_name))
    print(f"\n{file_name} columns:")
    print(df.columns.tolist())

# ------------------------------------------------------------------------------
# 1) Create Relationship CSVs from fans.csv
# ------------------------------------------------------------------------------
def create_relationship_csvs():
    """
    Reads fans.csv, which includes columns:
      - fan_id
      - favorite_players (string list)
      - community_memberships (string list)
    Expands these lists into separate relationship rows, which we export as:
      fan_player_rels.csv and fan_community_rels.csv
    """
    fans_path = os.path.join(CSV_DIR, FANS_FILE)
    df_fans = pd.read_csv(fans_path)

    fan_player_relationships = []
    fan_community_relationships = []

    for _, row in df_fans.iterrows():
        fan_id = row["fan_id"]

        # favorite_players (could be "['id1','id2']" or a single string)
        fav_players_raw = row.get("favorite_players", "[]")
        fav_players_list = parse_string_list(fav_players_raw)

        for pid in fav_players_list:
            fan_player_relationships.append({
                "start_id": fan_id,
                "end_id": pid,
                "relationship_type": "FAVORITE_PLAYER"
            })

        # community_memberships
        comm_memberships_raw = row.get("community_memberships", "[]")
        comm_list = parse_string_list(comm_memberships_raw)

        for cid in comm_list:
            fan_community_relationships.append({
                "start_id": fan_id,
                "end_id": cid,
                "relationship_type": "MEMBER_OF"
            })

    # Convert to DataFrames and write out to CSV
    if fan_player_relationships:
        df_fan_player = pd.DataFrame(fan_player_relationships)
        df_fan_player.to_csv(os.path.join(REL_CSV_DIR, "fan_player_rels.csv"), index=False)

    if fan_community_relationships:
        df_fan_community = pd.DataFrame(fan_community_relationships)
        df_fan_community.to_csv(os.path.join(REL_CSV_DIR, "fan_community_rels.csv"), index=False)

    print("Created relationship CSVs in:", REL_CSV_DIR)

def parse_string_list(raw_val):
    """
    Attempt to parse a Python-style list string (e.g. "['abc','def']")
    or return an empty list if parsing fails.
    """
    if isinstance(raw_val, str):
        try:
            parsed = eval(raw_val)
            if not isinstance(parsed, list):
                return []
            return parsed
        except:
            return []
    elif isinstance(raw_val, list):
        return raw_val
    else:
        return []

# ------------------------------------------------------------------------------
# 2) LOAD Node & Relationship CSVs into Neo4j
# ------------------------------------------------------------------------------
def clean_row_dict(row):
    """Convert pandas row to dict and replace NaN with None"""
    return {k: None if pd.isna(v) else v for k, v in row.items()}

def ingest_to_neo4j():
    """
    Connects to Neo4j, deletes existing data, creates constraints,
    loads node CSVs, then loads relationship CSVs.
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    with driver.session() as session:
        # (A) DELETE CURRENT CONTENTS
        session.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing graph data.")

        # (B) Create uniqueness constraints - Updated with exact column name
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Community) REQUIRE c.fan_chapter_name IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Player) REQUIRE p.player_id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (g:Game) REQUIRE g.game_id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Fan) REQUIRE f.fan_id IS UNIQUE")
        print("Created/ensured constraints.")

        # 1) Communities - Updated to handle duplicates
        communities_df = pd.read_csv(os.path.join(CSV_DIR, COMMUNITIES_FILE))
        
        # Track duplicates
        duplicates = communities_df[communities_df['Fan Chapter Name'].duplicated(keep='first')]
        if not duplicates.empty:
            print(f"\nFound {len(duplicates)} duplicate Fan Chapter Names (keeping first occurrence only):")
            print(duplicates[['Fan Chapter Name']].to_string())
            
            # Export duplicates to CSV for reference
            duplicates.to_csv(os.path.join(CSV_DIR, 'duplicate_chapters.csv'), index=False)
        
        # Keep only first occurrence of each Fan Chapter Name
        communities_df = communities_df.drop_duplicates(subset=['Fan Chapter Name'], keep='first')
        
        # Process unique chapters
        for _, row in communities_df.iterrows():
            params = clean_row_dict(row)
            
            # Map the correct columns
            params["fan_chapter_name"] = params.pop("Fan Chapter Name", "") or ""
            params["city"] = params.pop("Meeting Location Address (City)", "") or ""
            params["state"] = params.pop("Meeting Location Address (State)", "") or ""
            params["email_contact"] = params.pop("Email Address", "") or ""
            params["meetup_info"] = f"{params.pop('Venue', '')} - {params.pop('Venue Location', '')}"

            session.run("""
                CREATE (c:Community {
                    fan_chapter_name: $fan_chapter_name,
                    city: $city,
                    state: $state,
                    email_contact: $email_contact,
                    meetup_info: $meetup_info
                })
            """, params)
        print(f"Imported {len(communities_df)} unique Communities.")

        # 2) Players - Updated with correct column names
        players_df = pd.read_csv(os.path.join(CSV_DIR, ROSTER_FILE))
        for _, row in players_df.iterrows():
            params = clean_row_dict(row)
            session.run("""
                CREATE (p:Player {
                    player_id: $player_id,
                    name: $Player,
                    position: $Pos,
                    jersey_number: toInteger($Number),
                    height: $HT,
                    weight: $WT,
                    college: $College,
                    years_in_nfl: toInteger($Exp)
                })
            """, params)
        print("Imported Players.")

        # 3) Games - Updated with correct column names
        games_df = pd.read_csv(os.path.join(CSV_DIR, SCHEDULE_FILE))
        for _, row in games_df.iterrows():
            params = clean_row_dict(row)
            session.run("""
                CREATE (g:Game {
                    game_id: $game_id,
                    date: $Date,
                    location: $Location,
                    home_team: $HomeTeam,
                    away_team: $AwayTeam,
                    result: $Result,
                    summary: $Summary,
                    embedding: $embedding
                })
            """, params)
        print("Imported Games.")

        # 4) Fans - This one was correct, no changes needed
        fans_df = pd.read_csv(os.path.join(CSV_DIR, FANS_FILE))
        for _, row in fans_df.iterrows():
            params = clean_row_dict(row)
            session.run("""
                CREATE (f:Fan {
                    fan_id: $fan_id,
                    first_name: $first_name,
                    last_name: $last_name,
                    email: $email
                })
            """, params)
        print("Imported Fans.")

        # (D) LOAD Relationships
        fan_player_path = os.path.join(REL_CSV_DIR, "fan_player_rels.csv")
        if os.path.exists(fan_player_path):
            rels_df = pd.read_csv(fan_player_path)
            for _, row in rels_df.iterrows():
                params = clean_row_dict(row)
                session.run("""
                    MATCH (f:Fan {fan_id: $start_id})
                    MATCH (p:Player {player_id: $end_id})
                    CREATE (f)-[:FAVORITE_PLAYER]->(p)
                """, params)
            print("Created Fan -> Player relationships.")

        fan_community_path = os.path.join(REL_CSV_DIR, "fan_community_rels.csv")
        if os.path.exists(fan_community_path):
            rels_df = pd.read_csv(fan_community_path)
            for _, row in rels_df.iterrows():
                params = clean_row_dict(row)
                session.run("""
                    MATCH (f:Fan {fan_id: $start_id})
                    MATCH (c:Community {fan_chapter_name: $end_id})
                    CREATE (f)-[:MEMBER_OF]->(c)
                """, params)
            print("Created Fan -> Community relationships.")

    driver.close()
    print("Neo4j ingestion complete!")

# ------------------------------------------------------------------------------
# 3) MAIN
# ------------------------------------------------------------------------------
def main():
    # 1) Generate relationship CSVs for fans' favorite_players & community_memberships
    create_relationship_csvs()

    # 2) Ingest all CSVs (nodes + relationships) into Neo4j
    ingest_to_neo4j()

if __name__ == "__main__":
    main()
