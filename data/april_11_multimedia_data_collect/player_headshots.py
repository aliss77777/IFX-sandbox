import requests
from bs4 import BeautifulSoup
import csv

ROSTER_URL = "https://www.49ers.com/team/players-roster/"

def scrape_49ers_roster(output_csv='niners_players_headshots.csv'):
    """
    Scrapes the 49ers roster page for player data and saves to CSV.
    Extracts:
        - Name
        - Headshot Image URL
    """
    response = requests.get(ROSTER_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    player_rows = soup.select('div.d3-o-table--horizontal-scroll tbody tr')
    if not player_rows:
        raise ValueError("No player rows found. The page structure may have changed.")

    roster_data = []
    for row in player_rows:
        try:
            # Extract player name and headshot
            player_cell = row.find('td')
            name_tag = player_cell.select_one('.nfl-o-roster__player-name')
            name = name_tag.get_text(strip=True) if name_tag else ""

            img_tag = player_cell.find('img')
            headshot_url = img_tag['src'] if img_tag and img_tag.get('src') else ""
            
            # Fix the URL by replacing t_lazy with t_thumb_squared_2x
            if headshot_url:
                headshot_url = headshot_url.replace('/t_thumb_squared/t_lazy/', '/t_thumb_squared_2x/')

            # Other stats (in order of table columns)
            # cells = row.find_all('td')
            # jersey_number = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            # position = cells[2].get_text(strip=True) if len(cells) > 2 else ""
            # height = cells[3].get_text(strip=True) if len(cells) > 3 else ""
            # weight = cells[4].get_text(strip=True) if len(cells) > 4 else ""
            # age = cells[5].get_text(strip=True) if len(cells) > 5 else ""
            # experience = cells[6].get_text(strip=True) if len(cells) > 6 else ""
            # college = cells[7].get_text(strip=True) if len(cells) > 7 else ""

            roster_data.append({
                'name': name,
                # 'jersey_number': jersey_number,
                # 'position': position,
                # 'height': height,
                # 'weight': weight,
                # 'age': age,
                # 'experience': experience,
                # 'college': college,
                'headshot_url': headshot_url
            })

        except Exception as e:
            print(f"[WARNING] Skipping row due to error: {e}")
            continue

    # Save to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'headshot_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(roster_data)

    print(f"[INFO] Successfully saved {len(roster_data)} players to '{output_csv}'.")

if __name__ == "__main__":
    scrape_49ers_roster()
