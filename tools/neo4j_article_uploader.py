#!/usr/bin/env python
"""
Script to upload structured and summarized team news articles from a CSV file to Neo4j.
"""

import os
import sys
import csv
from datetime import datetime
from dotenv import load_dotenv

# Adjust path to import graph object from the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from gradio_graph import graph # Import the configured graph instance
except ImportError as e:
    print(f"Error importing gradio_graph: {e}")
    print("Please ensure gradio_graph.py exists and is configured correctly.")
    sys.exit(1)

# Load environment variables (though graph should already be configured)
load_dotenv()

# Configuration
# Assumes the CSV is in the same directory as this script
CSV_FILEPATH = os.path.join(os.path.dirname(__file__), "team_news_articles.csv")
TEAM_NAME = "San Francisco 49ers"

def upload_articles_to_neo4j(csv_filepath):
    """Reads the CSV and uploads article data to Neo4j."""
    print(f"Starting Neo4j upload process for {csv_filepath}...")

    if not os.path.exists(csv_filepath):
        print(f"Error: CSV file not found at {csv_filepath}")
        return

    # 1. Ensure the :Team node exists with correct properties
    print(f"Ensuring :Team node exists for '{TEAM_NAME}'...")
    team_merge_query = """
    MERGE (t:Team {name: $team_name})
    SET t.season_record_2024 = $record, 
        t.city = $city, 
        t.conference = $conference, 
        t.division = $division
    RETURN t.name
    """
    team_params = {
        "team_name": TEAM_NAME,
        "record": "6-11", # As specified in instructions
        "city": "San Francisco",
        "conference": "NFC",
        "division": "West"
    }
    try:
        result = graph.query(team_merge_query, params=team_params)
        if result and result[0]['t.name'] == TEAM_NAME:
            print(f":Team node '{TEAM_NAME}' ensured/updated successfully.")
        else:
            print(f"Warning: Problem ensuring :Team node '{TEAM_NAME}'. Result: {result}")
            # Decide whether to proceed or stop
            # return
    except Exception as e:
        print(f"Error executing team merge query: {e}")
        return # Stop if we can't ensure the team node

    # 2. Read CSV and upload articles
    print("Reading CSV and uploading :Team_Story nodes...")
    article_merge_query = """
    MERGE (s:Team_Story {link_to_article: $link_to_article}) 
    SET s.teamName = $Team_name, 
        s.season = toInteger($season), // Ensure season is integer
        s.summary = $summary, 
        s.topic = $topic,
        s.city = $city, 
        s.conference = $conference,
        s.division = $division
        // Add other properties from CSV if needed, like raw_title, raw_date?
    WITH s
    MATCH (t:Team {name: $Team_name})
    MERGE (s)-[:STORY_ABOUT]->(t)
    RETURN s.link_to_article AS article_link, t.name AS team_name 
    """

    upload_count = 0
    error_count = 0
    try:
        with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Prepare parameters for the query
                    # Ensure all expected keys from the query are present in the row or provide defaults
                    params = {
                        "link_to_article": row.get("link_to_article", ""),
                        "Team_name": row.get("Team_name", TEAM_NAME), # Use team name from row or default
                        "season": row.get("season", datetime.now().year), # Default season if missing
                        "summary": row.get("summary", ""),
                        "topic": row.get("topic", ""),
                        "city": row.get("city", "San Francisco"), # Use city from row or default
                        "conference": row.get("conference", "NFC"),
                        "division": row.get("division", "West"),
                    }
                    
                    # Basic validation before sending to Neo4j
                    if not params["link_to_article"]:
                        print(f"Skipping row due to missing link_to_article: {row}")
                        error_count += 1
                        continue
                    if not params["Team_name"]:
                         print(f"Skipping row due to missing Team_name: {row}")
                         error_count += 1
                         continue

                    # Execute the query for the current article
                    graph.query(article_merge_query, params=params)
                    upload_count += 1
                    if upload_count % 20 == 0: # Print progress every 20 articles
                         print(f"Uploaded {upload_count} articles...")

                except Exception as e:
                    print(f"Error processing/uploading row: {row}")
                    print(f"Error details: {e}")
                    error_count += 1
                    # Continue to next row even if one fails?
                    # Or break? For now, let's continue.
                    
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_filepath}")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading CSV or uploading: {e}")
        return

    print(f"\nNeo4j upload process finished.")
    print(f"Successfully uploaded/merged: {upload_count} articles.")
    print(f"Rows skipped due to errors/missing data: {error_count}.")


if __name__ == "__main__":
    print("Running Neo4j Article Uploader script...")
    upload_articles_to_neo4j(CSV_FILEPATH)
    print("Script execution complete.") 