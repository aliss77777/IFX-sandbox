import csv
import re
import os
from pathlib import Path
from collections import defaultdict


# Define file paths
YOUTUBE_HIGHLIGHTS_PATH =  "youtube_highlights.csv"
PLAYERS_ROSTER_PATH =  "niners_players_headshots_with_socials_merged.csv"
GAMES_SCHEDULE_PATH = "nfl-2024-san-francisco-49ers-with-results.csv"
OUTPUT_PLAYERS_PATH =  "new_niners_players_with_highlights.csv"
OUTPUT_GAMES_PATH =   "new_games_with_highlights.csv"
OUTPUT_TEAM_VIDEOS_PATH =   "new_team_highlights.csv"

def load_youtube_highlights():
    """Load YouTube highlights data from CSV file."""
    highlights = []
    with open(YOUTUBE_HIGHLIGHTS_PATH, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            highlights.append({
                'video_id': row['video_id'],
                'title': row['title'],
                'description': row['description'],
                'published_at': row['published_at'],
                'video_url': row['video_url']
            })
    return highlights

def load_players():
    """Load player roster data from CSV file."""
    players = []
    with open(PLAYERS_ROSTER_PATH, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            players.append({
                'name': row['name'],
                'headshot_url': row['headshot_url'],
                'instagram_url': row['instagram_url'],
                'highlight_video_url': ''  # Initialize with empty string
            })
    return players

def load_games():
    """Load game schedule data from CSV file."""
    games = []
    with open(GAMES_SCHEDULE_PATH, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            opponent = row['Away Team'] if row['Home Team'] == 'San Francisco 49ers' else row['Home Team']
            opponent = opponent.replace('San Francisco 49ers', '').strip()
            
            games.append({
                'match_number': row['Match Number'],
                'round_number': row['Round Number'],
                'date': row['Date'],
                'location': row['Location'],
                'home_team': row['Home Team'],
                'away_team': row['Away Team'],
                'result': row['Result'],
                'game_result': row['game_result'],
                'opponent': opponent,
                'highlight_video_url': ''  # Initialize with empty string
            })
    return games

def match_highlights_to_players_and_games(highlights, players, games):
    """Match YouTube highlights to players and games."""
    # Create a copy of highlights to track which ones are assigned
    unassigned_highlights = highlights.copy()
    
    # Track assigned videos
    assigned_video_ids = set()
    
    # Match players first
    for player in players:
        player_name = player['name']
        first_name = player_name.split()[0]
        last_name = player_name.split()[-1]
        
        # Create patterns to match player names
        full_name_pattern = re.compile(r'\b' + re.escape(player_name) + r'\b', re.IGNORECASE)
        last_name_pattern = re.compile(r'\b' + re.escape(last_name) + r'\b', re.IGNORECASE)
        
        # Try to find a match in the unassigned highlights
        for highlight in unassigned_highlights:
            if highlight['video_id'] in assigned_video_ids:
                continue
                
            title = highlight['title']
            description = highlight['description']
            
            # Check for full name match in title first (most specific)
            if full_name_pattern.search(title):
                player['highlight_video_url'] = highlight['video_url']
                assigned_video_ids.add(highlight['video_id'])
                break
            
            # Then check for last name match in title
            elif last_name_pattern.search(title):
                player['highlight_video_url'] = highlight['video_url']
                assigned_video_ids.add(highlight['video_id'])
                break
    
    # Match games next
    for game in games:
        opponent = game['opponent']
        week_pattern = re.compile(r'\bWeek\s+' + re.escape(game['round_number']) + r'\b', re.IGNORECASE)
        opponent_pattern = re.compile(r'\b' + re.escape(opponent) + r'\b', re.IGNORECASE)
        
        # Try to find a match in the unassigned highlights
        for highlight in unassigned_highlights:
            if highlight['video_id'] in assigned_video_ids:
                continue
                
            title = highlight['title']
            description = highlight['description']
            
            # Check for both week and opponent match in title (most specific)
            if week_pattern.search(title) and opponent_pattern.search(title):
                game['highlight_video_url'] = highlight['video_url']
                assigned_video_ids.add(highlight['video_id'])
                break
            
            # Then check for opponent match in title
            elif opponent_pattern.search(title):
                game['highlight_video_url'] = highlight['video_url']
                assigned_video_ids.add(highlight['video_id'])
                break
    
    # Collect team videos (unassigned highlights)
    team_videos = []
    for highlight in highlights:
        if highlight['video_id'] not in assigned_video_ids:
            team_videos.append(highlight)
    
    return team_videos

def save_players_with_highlights(players):
    """Save players with highlight videos to CSV file."""
    with open(OUTPUT_PLAYERS_PATH, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['name', 'headshot_url', 'instagram_url', 'highlight_video_url']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for player in players:
            writer.writerow(player)

def save_games_with_highlights(games):
    """Save games with highlight videos to CSV file."""
    with open(OUTPUT_GAMES_PATH, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['match_number', 'round_number', 'date', 'location', 'home_team', 'away_team', 
                     'result', 'game_result', 'opponent', 'highlight_video_url']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for game in games:
            writer.writerow(game)

def save_team_videos(team_videos):
    """Save team videos to CSV file."""
    with open(OUTPUT_TEAM_VIDEOS_PATH, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['video_id', 'title', 'description', 'published_at', 'video_url']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for video in team_videos:
            writer.writerow(video)

def main():
    # Load data
    highlights = load_youtube_highlights()
    players = load_players()
    games = load_games()
    
    # Match highlights to players and games
    team_videos = match_highlights_to_players_and_games(highlights, players, games)
    
    # Save results
    save_players_with_highlights(players)
    save_games_with_highlights(games)
    save_team_videos(team_videos)
    
    # Print summary
    player_matches = sum(1 for player in players if player['highlight_video_url'])
    game_matches = sum(1 for game in games if game['highlight_video_url'])
    
    print(f"Total YouTube highlights: {len(highlights)}")
    print(f"Players with highlight videos: {player_matches}/{len(players)}")
    print(f"Games with highlight videos: {game_matches}/{len(games)}")
    print(f"Team videos (unassigned): {len(team_videos)}")
    print(f"\nOutput files created:")
    print(f"- {OUTPUT_PLAYERS_PATH}")
    print(f"- {OUTPUT_GAMES_PATH}")
    print(f"- {OUTPUT_TEAM_VIDEOS_PATH}")

if __name__ == "__main__":
    main()
