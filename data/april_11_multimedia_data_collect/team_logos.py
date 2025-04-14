import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
NFL_TEAMS_URL = "https://www.nfl.com/teams/"
OUTPUT_DIR = "team_logos"
CSV_OUTPUT = "nfl_team_logos.csv"
EXPECTED_TEAM_COUNT = 32

def ensure_output_dir(dir_path):
    """Ensure output directory exists"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info(f"Created directory: {dir_path}")

def download_image(url, file_path):
    """Download image from URL and save to file_path"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {e}")
        return False

def get_team_logo_urls():
    """
    Get team logo URLs directly from team pages.
    Returns a dictionary mapping team names to their logo URLs.
    """
    logger.info(f"Fetching team information from {NFL_TEAMS_URL}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        response = requests.get(NFL_TEAMS_URL, headers=headers)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch NFL teams page: {e}")
        return {}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all team links
    team_links = []
    for a_tag in soup.find_all('a', href=True):
        if '/teams/' in a_tag['href'] and a_tag['href'].count('/') >= 3:
            # This looks like a team-specific link
            team_links.append(a_tag['href'])
    
    # Get unique team URLs
    team_urls = {}
    for link in team_links:
        # Extract team slug (e.g., 'cardinals', '49ers')
        match = re.search(r'/teams/([a-z0-9-]+)/?$', link)
        if match:
            team_slug = match.group(1)
            if team_slug not in team_urls:
                full_url = f"https://www.nfl.com{link}" if not link.startswith('http') else link
                team_urls[team_slug] = full_url
    
    logger.info(f"Found {len(team_urls)} unique team URLs")
    
    # Visit each team page to get the official logo
    team_logos = {}
    for slug, url in team_urls.items():
        try:
            logger.info(f"Visiting team page: {url}")
            team_response = requests.get(url, headers=headers)
            team_response.raise_for_status()
            
            team_soup = BeautifulSoup(team_response.text, 'html.parser')
            
            # Get team name from title
            title_tag = team_soup.find('title')
            if title_tag:
                title_text = title_tag.text
                team_name = title_text.split('|')[0].strip()
                if not team_name:
                    team_name = slug.replace('-', ' ').title()  # Fallback to slug
            else:
                team_name = slug.replace('-', ' ').title()  # Fallback to slug
            
            # Look for team logo in various places
            logo_url = None
            
            # Method 1: Look for logo in meta tags (most reliable)
            og_image = team_soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                logo_url = og_image.get('content')
            
            # Method 2: Look for team logos in certain image tags or SVGs
            if not logo_url:
                team_header = team_soup.find('div', class_=lambda c: c and ('team-header' in c or 'logo' in c))
                if team_header:
                    img = team_header.find('img')
                    if img and img.get('src'):
                        logo_url = img.get('src')
            
            # Method 3: JavaScript data
            if not logo_url:
                scripts = team_soup.find_all('script')
                for script in scripts:
                    if script.string and ('logo' in script.string.lower() or 'image' in script.string.lower()):
                        # Try to extract JSON data with logo information
                        json_matches = re.findall(r'({.*?"logo".*?})', script.string)
                        for match in json_matches:
                            try:
                                data = json.loads(match)
                                if 'logo' in data and isinstance(data['logo'], str):
                                    logo_url = data['logo']
                                    break
                            except:
                                continue
            
            # Method 4: Fallback to a known pattern based on team abbreviation
            if not logo_url and len(slug) > 2:
                # Some teams have standardized logo URLs with abbreviations
                team_abbr = slug[:2].upper()  # Get first 2 chars as abbreviation
                logo_url = f"https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/{team_abbr}"
            
            # If we found a logo, add it to our dictionary
            if logo_url:
                # If necessary, make the URL absolute
                if not logo_url.startswith('http'):
                    logo_url = f"https://www.nfl.com{logo_url}" if logo_url.startswith('/') else f"https://www.nfl.com/{logo_url}"
                
                team_logos[team_name] = logo_url
                logger.info(f"Found logo for {team_name}: {logo_url}")
            else:
                logger.warning(f"Could not find logo URL for {team_name}")
            
            # Be polite with rate limiting
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error processing team page {url}: {e}")
    
    logger.info(f"Found logos for {len(team_logos)} teams")
    return team_logos

def download_team_logos():
    """Download NFL team logos and save to CSV"""
    logger.info("Starting NFL team logo download")
    
    # Ensure output directory exists
    ensure_output_dir(OUTPUT_DIR)
    
    # Get team logo URLs from team pages
    team_logos = get_team_logo_urls()
    
    # Use a backup approach for any missing teams
    if len(team_logos) < EXPECTED_TEAM_COUNT:
        logger.warning(f"Only found {len(team_logos)} team logos from web scraping. Using ESPN API as backup.")
        # We'll use ESPN's API to get team data including logos
        try:
            espn_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
            response = requests.get(espn_url)
            response.raise_for_status()
            
            espn_data = response.json()
            if 'sports' in espn_data and len(espn_data['sports']) > 0:
                if 'leagues' in espn_data['sports'][0] and len(espn_data['sports'][0]['leagues']) > 0:
                    if 'teams' in espn_data['sports'][0]['leagues'][0]:
                        for team_data in espn_data['sports'][0]['leagues'][0]['teams']:
                            team = team_data.get('team', {})
                            team_name = team.get('displayName')
                            if team_name and team_name not in team_logos:
                                logo_url = team.get('logos', [{}])[0].get('href')
                                if logo_url:
                                    team_logos[team_name] = logo_url
                                    logger.info(f"Added {team_name} logo from ESPN API: {logo_url}")
        except Exception as e:
            logger.error(f"Error fetching from ESPN API: {e}")
    
    # If we still don't have enough teams, use a manually defined dictionary
    if len(team_logos) < EXPECTED_TEAM_COUNT:
        logger.warning(f"Still only have {len(team_logos)} teams. Adding manual definitions for missing teams.")
        
        # Standard team names that should be present
        standard_teams = [
            "Arizona Cardinals", "Atlanta Falcons", "Baltimore Ravens", "Buffalo Bills",
            "Carolina Panthers", "Chicago Bears", "Cincinnati Bengals", "Cleveland Browns",
            "Dallas Cowboys", "Denver Broncos", "Detroit Lions", "Green Bay Packers",
            "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Kansas City Chiefs",
            "Las Vegas Raiders", "Los Angeles Chargers", "Los Angeles Rams", "Miami Dolphins",
            "Minnesota Vikings", "New England Patriots", "New Orleans Saints", "New York Giants",
            "New York Jets", "Philadelphia Eagles", "Pittsburgh Steelers", "San Francisco 49ers",
            "Seattle Seahawks", "Tampa Bay Buccaneers", "Tennessee Titans", "Washington Commanders"
        ]
        
        # Manual dictionary of team logos (use correct ones from NFL's CDN)
        manual_logos = {
            "Arizona Cardinals": "https://static.www.nfl.com/image/private/f_auto/league/u9fltoslqdsyao8cpm0k",
            "Atlanta Falcons": "https://static.www.nfl.com/image/private/f_auto/league/d8m7hzwsyzgg0smz7ifyj",
            "Baltimore Ravens": "https://static.www.nfl.com/image/private/f_auto/league/ucsdijmddsqcj1i9tddd",
            "Buffalo Bills": "https://static.www.nfl.com/image/private/f_auto/league/giphcy6ie9mxbnldntsf",
            "Carolina Panthers": "https://static.www.nfl.com/image/private/f_auto/league/ervfzgrqdpnc7lh5gqwq",
            "Chicago Bears": "https://static.www.nfl.com/image/private/f_auto/league/ra0poq2ivwyahbaq86d2",
            "Cincinnati Bengals": "https://static.www.nfl.com/image/private/f_auto/league/bpx88i8nw4nnabuq0oob",
            "Cleveland Browns": "https://static.www.nfl.com/image/private/f_auto/league/omlzo6n7dpxzbpwrqaak",
            "Dallas Cowboys": "https://static.www.nfl.com/image/private/f_auto/league/dxibuyxbk0b9ua5ih9hn",
            "Denver Broncos": "https://static.www.nfl.com/image/private/f_auto/league/t0p7m5cjdjy18rnzzqbx",
            "Detroit Lions": "https://static.www.nfl.com/image/private/f_auto/league/dhfidtn8jrumakbawoxz",
            "Green Bay Packers": "https://static.www.nfl.com/image/private/f_auto/league/q1l7xmkuuyrpdmnutkzf",
            "Houston Texans": "https://static.www.nfl.com/image/private/f_auto/league/bpx88i8nw4nnabuq0oob",
            "Indianapolis Colts": "https://static.www.nfl.com/image/private/f_auto/league/ketwqeuschqzjsllbid5",
            "Jacksonville Jaguars": "https://static.www.nfl.com/image/private/f_auto/league/bwl1nuab0n2bhi8nxiar",
            "Kansas City Chiefs": "https://static.www.nfl.com/image/private/f_auto/league/ujshjqvmnxce8m4obmvs",
            "Las Vegas Raiders": "https://static.www.nfl.com/image/private/f_auto/league/gzcojbzcyjgubgyb6xf2",
            "Los Angeles Chargers": "https://static.www.nfl.com/image/private/f_auto/league/dhfidtn8jrumakbawoxz",
            "Los Angeles Rams": "https://static.www.nfl.com/image/private/f_auto/league/rjxoqpjirhjvvitffvwh",
            "Miami Dolphins": "https://static.www.nfl.com/image/private/f_auto/league/lits6p8ycthy9to70bnt",
            "Minnesota Vikings": "https://static.www.nfl.com/image/private/f_auto/league/teguylrnqqmfcwxvcmmz",
            "New England Patriots": "https://static.www.nfl.com/image/private/f_auto/league/moyfxx3dq5pio4aiftnc",
            "New Orleans Saints": "https://static.www.nfl.com/image/private/f_auto/league/grhjkahghuebpwzo6kxn",
            "New York Giants": "https://static.www.nfl.com/image/private/f_auto/league/t6mhdmgizi6qhndh8b9p",
            "New York Jets": "https://static.www.nfl.com/image/private/f_auto/league/ekijosiae96gektbo1lj",
            "Philadelphia Eagles": "https://static.www.nfl.com/image/private/f_auto/league/puhrqgj71gobgmwb5g3p",
            "Pittsburgh Steelers": "https://static.www.nfl.com/image/private/f_auto/league/xujik9a3j8hl6jjumu25",
            "San Francisco 49ers": "https://static.www.nfl.com/image/private/f_auto/league/dxibuyxbk0b9ua5ih9hn",
            "Seattle Seahawks": "https://static.www.nfl.com/image/private/f_auto/league/gcytzwpjdzbpwnwxincg",
            "Tampa Bay Buccaneers": "https://static.www.nfl.com/image/private/f_auto/league/v8uqiualryypwqgvwcih",
            "Tennessee Titans": "https://static.www.nfl.com/image/private/f_auto/league/pln44vuzugjgipyidsre",
            "Washington Commanders": "https://static.www.nfl.com/image/private/f_auto/league/xymxwrxtyj9fhaegfwof"
        }
        
        # Fill in any missing teams with manual data
        for team_name in standard_teams:
            if team_name not in team_logos and team_name in manual_logos:
                team_logos[team_name] = manual_logos[team_name]
                logger.info(f"Added {team_name} logo from manual dictionary")
    
    # Process and download team logos
    results = []
    for team_name, logo_url in team_logos.items():
        # Create safe filename
        safe_name = team_name.replace(' ', '_').lower()
        file_extension = '.png'  # Default to PNG
        filename = f"{safe_name}{file_extension}"
        local_path = os.path.join(OUTPUT_DIR, filename)
        
        # Download the logo
        logger.info(f"Downloading logo for {team_name} from {logo_url}")
        download_success = download_image(logo_url, local_path)
        
        if download_success:
            results.append({
                'team_name': team_name,
                'logo_url': logo_url,
                'local_path': local_path
            })
            logger.info(f"Successfully downloaded logo for {team_name}")
        else:
            logger.error(f"Failed to download logo for {team_name}")
        
        # Add a small delay
        time.sleep(0.5)
    
    # Save to CSV
    with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['team_name', 'logo_url', 'local_path']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    logger.info(f"Successfully saved {len(results)} team logos out of {len(team_logos)} teams.")
    logger.info(f"CSV data saved to '{CSV_OUTPUT}'")
    
    if len(results) < EXPECTED_TEAM_COUNT:
        logger.warning(f"Only downloaded {len(results)} team logos, expected {EXPECTED_TEAM_COUNT}.")
    else:
        logger.info(f"SUCCESS! Downloaded all {EXPECTED_TEAM_COUNT} NFL team logos!")
    
    return results

if __name__ == "__main__":
    download_team_logos()