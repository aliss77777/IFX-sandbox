###################################
# regenerate_49ers_data.py
###################################

import pandas as pd
import random
import uuid
from faker import Faker
import os

# CONFIG: Where your input CSVs live
INPUT_DIR = os.path.dirname(os.path.abspath(__file__))  # Uses the current script's directory
COMMUNITIES_FILE = "49ers_fan_communities_clean_GOOD.csv"
ROSTER_FILE = "49ers roster - Sheet1.csv"
SCHEDULE_FILE = "nfl-2024-san-francisco-49ers-with-results.csv"

# CONFIG: Output directory for final CSVs
OUTPUT_DIR = os.path.join(INPUT_DIR, "niners_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_FANS = 2500  # We want 2500 synthetic fans

# ------------------------------------------------------------
# 1. READ REAL CSVs
# ------------------------------------------------------------
def load_real_data():
    # Adjust columns/types based on your actual CSV structure
    df_communities = pd.read_csv(os.path.join(INPUT_DIR, COMMUNITIES_FILE))
    df_roster = pd.read_csv(os.path.join(INPUT_DIR, ROSTER_FILE))
    df_schedule = pd.read_csv(os.path.join(INPUT_DIR, SCHEDULE_FILE))

    # Optional: rename columns or add IDs if your CSVs don't have them
    # For example, ensure df_roster has "player_id" column for each player
    if "player_id" not in df_roster.columns:
        df_roster["player_id"] = [str(uuid.uuid4()) for _ in range(len(df_roster))]

    # If df_schedule lacks a unique "game_id," add one:
    if "game_id" not in df_schedule.columns:
        df_schedule["game_id"] = [str(uuid.uuid4()) for _ in range(len(df_schedule))]

    # If df_communities lacks a "community_id," add one:
    if "community_id" not in df_communities.columns:
        df_communities["community_id"] = [str(uuid.uuid4()) for _ in range(len(df_communities))]

    return df_communities, df_roster, df_schedule

# ------------------------------------------------------------
# 2. GENERATE 2,500 FANS (FAKE DATA)
# ------------------------------------------------------------
def generate_synthetic_fans(num_fans: int) -> pd.DataFrame:
    """
    Create a DataFrame of synthetic fans.
    Each fan has:
      - fan_id (UUID)
      - first_name
      - last_name
      - email
      - favorite_players (list of player_ids)
      - community_memberships (list of community_ids)
    """
    fake = Faker()
    fans_list = []
    for _ in range(num_fans):
        fan_id = str(uuid.uuid4())
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()

        fans_list.append({
            "fan_id": fan_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            # We'll assign favorite_players & community_memberships below
            "favorite_players": [],
            "community_memberships": []
        })

    return pd.DataFrame(fans_list)

# ------------------------------------------------------------
# 3. ASSIGN RANDOM FAVORITE PLAYERS AND COMMUNITIES
# ------------------------------------------------------------
def assign_relationships(df_fans: pd.DataFrame,
                         df_roster: pd.DataFrame,
                         df_communities: pd.DataFrame):
    """
    - Pick 1-3 random favorite players for each fan from the real roster
    - Assign 0 or 1 community to each fan from the real communities
    """
    player_ids = df_roster["player_id"].tolist()
    community_ids = df_communities["community_id"].tolist()

    for idx, fan in df_fans.iterrows():
        # Choose 1-3 players
        if len(player_ids) > 0:
            num_players = random.randint(1, 3)
            chosen_players = random.sample(player_ids, k=num_players)
        else:
            chosen_players = []

        # 50% chance to join a community
        chosen_community = []
        if len(community_ids) > 0 and random.choice([True, False]):
            chosen_community = [random.choice(community_ids)]

        # Update the row's columns
        df_fans.at[idx, "favorite_players"] = chosen_players
        df_fans.at[idx, "community_memberships"] = chosen_community

# ------------------------------------------------------------
# 4. MAIN PIPELINE
# ------------------------------------------------------------
def main():
    # 4.1. Load real data
    df_communities, df_roster, df_schedule = load_real_data()

    # 4.2. Generate 2,500 synthetic fans
    df_fans = generate_synthetic_fans(NUM_FANS)

    # 4.3. Assign random relationships
    assign_relationships(df_fans, df_roster, df_communities)

    # 4.4. Export everything to CSV
    # (If you'd like to keep the original real-data files as is,
    #  you can simply re-write them or rename them. Below we do an explicit "to_csv".)

    df_communities.to_csv(os.path.join(OUTPUT_DIR, "fan_communities.csv"), index=False)
    df_roster.to_csv(os.path.join(OUTPUT_DIR, "roster.csv"), index=False)
    df_schedule.to_csv(os.path.join(OUTPUT_DIR, "schedule.csv"), index=False)
    df_fans.to_csv(os.path.join(OUTPUT_DIR, "fans.csv"), index=False)

    print(f"Data generation complete! Files are in {OUTPUT_DIR}")
    print(" - fan_communities.csv  (REAL)")
    print(" - roster.csv           (REAL)")
    print(" - schedule.csv         (REAL)")
    print(" - fans.csv             (SYNTHETIC + relationships)")

if __name__ == "__main__":
    main()
