import requests
import csv
import os
import time
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file (for API key)
load_dotenv()

# Get the directory where this script is located
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

SERP_API_KEY = os.getenv("SERP_API_KEY")  # Or just hardcode for testing, not recommended

def get_instagram_handle(query, timeout=10, retries=3, delay_between_retries=2):
    """
    Uses SerpAPI to search for query: e.g. 'Brock Purdy Instagram'
    Returns the best guess at Instagram handle/page URL if found, else empty string.
    
    Args:
        query: Search query string
        timeout: Request timeout in seconds
        retries: Number of retries if request fails
        delay_between_retries: Seconds to wait between retries
    """
    if not SERP_API_KEY:
        raise ValueError("SERP_API_KEY environment variable not set or provided!")
    
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
    }
    
    for attempt in range(retries):
        try:
            print(f"[DEBUG] Sending API request for: {query}")
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            # Check if we have organic results
            if "organic_results" not in data:
                print(f"[WARNING] No organic_results found in API response for {query}")
                print(f"[DEBUG] Response keys: {list(data.keys())}")
                return ""
            
            # Typical structure: data['organic_results'] - parse each for relevant domain
            results = data.get("organic_results", [])
            print(f"[DEBUG] Found {len(results)} organic results")
            
            for r in results:
                link = r.get("link", "")
                # If it has 'instagram.com', let's assume it's correct
                if "instagram.com" in link.lower():
                    print(f"[DEBUG] Found Instagram link: {link}")
                    return link
            
            print(f"[WARNING] No Instagram links found for {query}")
            return ""
            
        except requests.exceptions.Timeout:
            print(f"[ERROR] Request timed out for {query} (attempt {attempt+1}/{retries})")
            if attempt < retries - 1:
                print(f"[INFO] Retrying in {delay_between_retries} seconds...")
                time.sleep(delay_between_retries)
            else:
                print(f"[ERROR] All retries failed for {query}")
                return ""
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed for {query}: {str(e)} (attempt {attempt+1}/{retries})")
            if attempt < retries - 1:
                print(f"[INFO] Retrying in {delay_between_retries} seconds...")
                time.sleep(delay_between_retries)
            else:
                print(f"[ERROR] All retries failed for {query}")
                return ""
                
        except Exception as e:
            print(f"[ERROR] Unexpected error for {query}: {str(e)}")
            return ""

def enrich_niners_socials(input_csv='niners_players_headshots.csv',
                          output_csv='niners_players_headshots_with_socials.csv',
                          delay_between_requests=1,
                          start_player=None,
                          max_players=None):
    """
    Reads the roster CSV, queries Instagram for each player's best match,
    then writes the results to a new CSV.
    
    Args:
        input_csv: Path to input CSV file
        output_csv: Path to output CSV file
        delay_between_requests: Seconds to wait between API requests to avoid rate limiting
        start_player: Player number to start processing from (1-indexed)
        max_players: Maximum number of players to process (None for all)
    """
    # Convert relative paths to absolute paths based on script directory
    if not os.path.isabs(input_csv):
        input_csv = os.path.join(SCRIPT_DIR, input_csv)
    if not os.path.isabs(output_csv):
        output_csv = os.path.join(SCRIPT_DIR, output_csv)
        
    print(f"[INFO] Input CSV path: {input_csv}")
    print(f"[INFO] Output CSV path: {output_csv}")
    if not SERP_API_KEY:
        print("[ERROR] SERP_API_KEY not set. Please set your environment variable or update the script.")
        return
    
    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"[ERROR] Input file not found: {input_csv}")
        return
    
    try:
        # Read existing output CSV if it exists to continue from where we left off
        existing_data = []
        if os.path.exists(output_csv):
            with open(output_csv, 'r', encoding='utf-8') as f_existing:
                existing_reader = csv.DictReader(f_existing)
                existing_data = list(existing_reader)
                print(f"[INFO] Loaded {len(existing_data)} existing entries")
        
        # Count total players for progress reporting
        with open(input_csv, 'r', encoding='utf-8') as f:
            total_players = sum(1 for _ in csv.DictReader(f))
        
        print(f"[INFO] Total players: {total_players}")
        
        # Determine start and end points
        start_index = start_player - 1 if start_player is not None else len(existing_data)
        end_index = min(total_players, start_index + (max_players or total_players))
        
        print(f"[INFO] Will process players from {start_index + 1} to {end_index}")
        
        # Reopen input CSV to start processing
        with open(input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            input_fieldnames = reader.fieldnames
            
            # Skip to the start player
            for _ in range(start_index):
                next(reader)
            
            # Process remaining players
            for i, row in enumerate(reader, start_index + 1):
                if i > end_index:
                    print(f"[INFO] Reached maximum number of players. Stopping.")
                    break
                    
                player_name = row['name']
                print(f"[INFO] Processing player {i}/{end_index}: {player_name}")
                
                # Skip if already processed
                if any(existing_row['name'] == player_name for existing_row in existing_data):
                    print(f"[INFO] {player_name} already processed. Skipping.")
                    continue
                
                # Construct a query like 'PLAYER NAME instagram'
                query = f"{player_name} NFL 49ers instagram"
                
                try:
                    insta_url = get_instagram_handle(query)
                    row['instagram_url'] = insta_url
                    
                    # Print result
                    if insta_url:
                        print(f"[SUCCESS] Found Instagram for {player_name}: {insta_url}")
                    else:
                        print(f"[WARNING] No Instagram found for {player_name}")
                    
                    # Append new data
                    existing_data.append(row)
                    
                    # Save progress after each player
                    with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
                        output_fieldnames = input_fieldnames + ['instagram_url']
                        writer = csv.DictWriter(f_out, fieldnames=output_fieldnames)
                        writer.writeheader()
                        writer.writerows(existing_data)
                    
                    # Add delay between requests to avoid rate limiting
                    if i < end_index:
                        print(f"[INFO] Waiting {delay_between_requests} seconds before next request...")
                        time.sleep(delay_between_requests)
                        
                except KeyboardInterrupt:
                    print("\n[INFO] Process interrupted by user. Saving progress...")
                    break
        
        print(f"[INFO] Social data saved to {output_csv}")
        print(f"[INFO] Processed {len(existing_data)}/{total_players} players")
        
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {str(e)}")
        # Try to save any data collected so far
        if existing_data:
            try:
                with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
                    output_fieldnames = input_fieldnames + ['instagram_url']
                    writer = csv.DictWriter(f_out, fieldnames=output_fieldnames)
                    writer.writeheader()
                    writer.writerows(existing_data)
                print(f"[INFO] Partial data saved to {output_csv}")
            except Exception:
                print("[ERROR] Failed to save partial data")

if __name__ == "__main__":
    print("[INFO] Starting player social media enrichment script")
    
    # Parse command line arguments
    delay = 1  # Default delay
    start_player = 51  # Default to start from 51st player
    max_players = None  # Process all remaining players
    
    if len(sys.argv) > 1:
        try:
            delay = float(sys.argv[1])
            print(f"[INFO] Using custom delay between requests: {delay} seconds")
        except ValueError:
            print(f"[WARNING] Invalid delay value: {sys.argv[1]}. Using default: 1 second")
    
    if len(sys.argv) > 2:
        try:
            start_player = int(sys.argv[2])
            print(f"[INFO] Will start processing from player {start_player}")
        except ValueError:
            print(f"[WARNING] Invalid start_player value: {sys.argv[2]}. Using default: 51")
    
    enrich_niners_socials(
        delay_between_requests=delay, 
        start_player=start_player, 
        max_players=max_players
    )
