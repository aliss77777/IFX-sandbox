import pandas as pd
import nfl_data_py as nfl
import warnings
warnings.filterwarnings("ignore")

# =============================================
# SECTION 1: BASIC STATS (ORIGINAL CODE)
# =============================================

# 1. Setup
season = 2024
team_abbr = "SF"

# 2. Load play-by-play data for the 2024 season
print("Loading play-by-play data...")
pbp_df = nfl.import_pbp_data(years=[season], downcast=True)

# 3. Filter for games involving the San Francisco 49ers
sf_games = pbp_df[(pbp_df['home_team'] == team_abbr) | (pbp_df['away_team'] == team_abbr)]

# 4. Get unique game IDs
game_ids = sf_games['game_id'].unique()

# 5. Create separate dataframes for passing, rushing, and receiving stats
# Passing stats
passing_stats = sf_games[sf_games['passer_player_id'].notna()].groupby(['game_id', 'passer_player_id', 'passer_player_name', 'posteam']).agg(
    passing_yards=('passing_yards', 'sum'),
    passing_tds=('pass_touchdown', 'sum'),
    interceptions=('interception', 'sum')
).reset_index()

# Rushing stats
rushing_stats = sf_games[sf_games['rusher_player_id'].notna()].groupby(['game_id', 'rusher_player_id', 'rusher_player_name', 'posteam']).agg(
    rushing_yards=('rushing_yards', 'sum'),
    rushing_tds=('rush_touchdown', 'sum')
).reset_index()

# Receiving stats - we need to identify receiving touchdowns from the touchdown column
# First, create a flag for receiving touchdowns
sf_games['receiving_td'] = (sf_games['touchdown'] == 1) & (sf_games['play_type'] == 'pass') & (sf_games['receiver_player_id'].notna())

# Then group by receiver
receiving_stats = sf_games[sf_games['receiver_player_id'].notna()].groupby(['game_id', 'receiver_player_id', 'receiver_player_name', 'posteam']).agg(
    receiving_yards=('receiving_yards', 'sum'),
    receiving_tds=('receiving_td', 'sum')
).reset_index()

# 6. Rename columns for consistency
passing_stats = passing_stats.rename(columns={'passer_player_id': 'player_id', 'passer_player_name': 'player_name'})
rushing_stats = rushing_stats.rename(columns={'rusher_player_id': 'player_id', 'rusher_player_name': 'player_name'})
receiving_stats = receiving_stats.rename(columns={'receiver_player_id': 'player_id', 'receiver_player_name': 'player_name'})

# 7. Merge all stats together
player_stats = pd.merge(passing_stats, rushing_stats, on=['game_id', 'player_id', 'player_name', 'posteam'], how='outer')
player_stats = pd.merge(player_stats, receiving_stats, on=['game_id', 'player_id', 'player_name', 'posteam'], how='outer')

# 8. Fill NaN values with 0
player_stats = player_stats.fillna(0)

# 9. Filter to only San Francisco 49ers players (on offense)
player_stats = player_stats[player_stats['posteam'] == team_abbr]

# 10. Load roster info to enrich with player position
roster_df = nfl.import_seasonal_rosters(years=[season])
player_stats = player_stats.merge(
    roster_df[['player_id', 'position', 'team']],
    on='player_id',
    how='left'
)

# 11. Export to CSV
output_path = "49ers_2024_player_box_scores.csv"
player_stats.to_csv(output_path, index=False)
print(f"Saved basic player box scores to {output_path}")

# 12. Preview results
print("\nBasic Stats Preview:")
print(player_stats.head())

# =============================================
# SECTION 2: ENHANCED STATS
# =============================================

print("\nGenerating enhanced statistics...")

# 1. Advanced Passing Stats
advanced_passing = sf_games[sf_games['passer_player_id'].notna()].groupby(['game_id', 'passer_player_id', 'passer_player_name', 'posteam']).agg(
    air_yards=('air_yards', 'sum'),
    yards_after_catch=('yards_after_catch', 'sum'),
    cpoe=('cpoe', 'mean'),  # Completion Percentage Over Expected
    qb_epa=('qb_epa', 'sum'),  # QB-specific EPA
    pass_attempts=('pass_attempt', 'sum'),
    complete_passes=('complete_pass', 'sum'),
    avg_air_yards=('air_yards', 'mean'),
    avg_yac=('yards_after_catch', 'mean'),
    pass_location_left=('pass_location', lambda x: (x == 'left').sum()),
    pass_location_middle=('pass_location', lambda x: (x == 'middle').sum()),
    pass_location_right=('pass_location', lambda x: (x == 'right').sum()),
    pass_length_short=('pass_length', lambda x: (x == 'short').sum()),
    pass_length_medium=('pass_length', lambda x: (x == 'medium').sum()),
    pass_length_deep=('pass_length', lambda x: (x == 'deep').sum())
).reset_index()

# 2. Advanced Rushing/Receiving Stats
advanced_rushing = sf_games[sf_games['rusher_player_id'].notna()].groupby(['game_id', 'rusher_player_id', 'rusher_player_name', 'posteam']).agg(
    rush_attempts=('rush_attempt', 'sum'),
    first_downs_rush=('first_down_rush', 'sum'),
    xyac_mean=('xyac_mean_yardage', 'mean'),
    xyac_median=('xyac_median_yardage', 'mean'),
    xyac_success_rate=('xyac_success', 'mean'),
    rush_epa=('epa', 'sum'),
    run_location_left=('run_location', lambda x: (x == 'left').sum()),
    run_location_middle=('run_location', lambda x: (x == 'middle').sum()),
    run_location_right=('run_location', lambda x: (x == 'right').sum()),
    run_gap_guard=('run_gap', lambda x: (x == 'guard').sum()),
    run_gap_tackle=('run_gap', lambda x: (x == 'tackle').sum()),
    run_gap_end=('run_gap', lambda x: (x == 'end').sum())
).reset_index()

advanced_receiving = sf_games[sf_games['receiver_player_id'].notna()].groupby(['game_id', 'receiver_player_id', 'receiver_player_name', 'posteam']).agg(
    receiving_attempts=('pass_attempt', 'sum'),
    first_downs_receiving=('first_down_pass', 'sum'),
    receiving_epa=('epa', 'sum'),
    avg_yac=('yards_after_catch', 'mean'),
    avg_air_yards=('air_yards', 'mean')
).reset_index()

# 3. Defensive Player Stats
# Create a list of all defensive player IDs from various defensive play columns
defensive_player_ids = []
defensive_player_names = []

# Solo tackles
solo_tackle_players = sf_games[sf_games['solo_tackle_1_player_id'].notna()][['game_id', 'solo_tackle_1_player_id', 'solo_tackle_1_player_name', 'defteam']]
solo_tackle_players = solo_tackle_players.rename(columns={'solo_tackle_1_player_id': 'player_id', 'solo_tackle_1_player_name': 'player_name'})
defensive_player_ids.append(solo_tackle_players)

# Assisted tackles
assist_tackle_players = sf_games[sf_games['assist_tackle_1_player_id'].notna()][['game_id', 'assist_tackle_1_player_id', 'assist_tackle_1_player_name', 'defteam']]
assist_tackle_players = assist_tackle_players.rename(columns={'assist_tackle_1_player_id': 'player_id', 'assist_tackle_1_player_name': 'player_name'})
defensive_player_ids.append(assist_tackle_players)

# Sacks
sack_players = sf_games[sf_games['sack_player_id'].notna()][['game_id', 'sack_player_id', 'sack_player_name', 'defteam']]
sack_players = sack_players.rename(columns={'sack_player_id': 'player_id', 'sack_player_name': 'player_name'})
defensive_player_ids.append(sack_players)

# Interceptions
int_players = sf_games[sf_games['interception_player_id'].notna()][['game_id', 'interception_player_id', 'interception_player_name', 'defteam']]
int_players = int_players.rename(columns={'interception_player_id': 'player_id', 'interception_player_name': 'player_name'})
defensive_player_ids.append(int_players)

# Forced fumbles
ff_players = sf_games[sf_games['forced_fumble_player_1_player_id'].notna()][['game_id', 'forced_fumble_player_1_player_id', 'forced_fumble_player_1_player_name', 'forced_fumble_player_1_team']]
ff_players = ff_players.rename(columns={'forced_fumble_player_1_player_id': 'player_id', 'forced_fumble_player_1_player_name': 'player_name', 'forced_fumble_player_1_team': 'defteam'})
defensive_player_ids.append(ff_players)

# Fumble recoveries
fr_players = sf_games[sf_games['fumble_recovery_1_player_id'].notna()][['game_id', 'fumble_recovery_1_player_id', 'fumble_recovery_1_player_name', 'fumble_recovery_1_team']]
fr_players = fr_players.rename(columns={'fumble_recovery_1_player_id': 'player_id', 'fumble_recovery_1_player_name': 'player_name', 'fumble_recovery_1_team': 'defteam'})
defensive_player_ids.append(fr_players)

# Pass defenses
pd_players = sf_games[sf_games['pass_defense_1_player_id'].notna()][['game_id', 'pass_defense_1_player_id', 'pass_defense_1_player_name', 'defteam']]
pd_players = pd_players.rename(columns={'pass_defense_1_player_id': 'player_id', 'pass_defense_1_player_name': 'player_name'})
defensive_player_ids.append(pd_players)

# Combine all defensive player dataframes
defensive_players = pd.concat(defensive_player_ids, ignore_index=True)
defensive_players = defensive_players.drop_duplicates()

# Now calculate defensive stats for each player
defensive_stats = sf_games.groupby(['game_id', 'defteam']).agg(
    solo_tackles=('solo_tackle', 'sum'),
    assisted_tackles=('assist_tackle', 'sum'),
    tackles_for_loss=('tackled_for_loss', 'sum'),
    qb_hits=('qb_hit', 'sum'),
    sacks=('sack', 'sum'),
    interceptions=('interception', 'sum'),
    forced_fumbles=('fumble_forced', 'sum'),
    fumble_recoveries=('fumble_recovery_1_yards', lambda x: (x > 0).sum()),
    pass_defenses=('pass_defense_1_player_id', lambda x: x.notna().sum())
).reset_index()

# Create a function to calculate individual defensive player stats
def calculate_defensive_player_stats(player_id, player_name, game_id, team):
    player_games = sf_games[sf_games['game_id'] == game_id]
    
    # Solo tackles
    solo_tackles = player_games[player_games['solo_tackle_1_player_id'] == player_id].shape[0]
    solo_tackles += player_games[player_games['solo_tackle_2_player_id'] == player_id].shape[0]
    
    # Assisted tackles
    assist_tackles = player_games[player_games['assist_tackle_1_player_id'] == player_id].shape[0]
    assist_tackles += player_games[player_games['assist_tackle_2_player_id'] == player_id].shape[0]
    assist_tackles += player_games[player_games['assist_tackle_3_player_id'] == player_id].shape[0]
    assist_tackles += player_games[player_games['assist_tackle_4_player_id'] == player_id].shape[0]
    
    # Sacks
    sacks = player_games[player_games['sack_player_id'] == player_id].shape[0]
    sacks += player_games[player_games['half_sack_1_player_id'] == player_id].shape[0] * 0.5
    sacks += player_games[player_games['half_sack_2_player_id'] == player_id].shape[0] * 0.5
    
    # Interceptions
    interceptions = player_games[player_games['interception_player_id'] == player_id].shape[0]
    
    # Forced fumbles
    forced_fumbles = player_games[player_games['forced_fumble_player_1_player_id'] == player_id].shape[0]
    forced_fumbles += player_games[player_games['forced_fumble_player_2_player_id'] == player_id].shape[0]
    
    # Fumble recoveries
    fumble_recoveries = player_games[player_games['fumble_recovery_1_player_id'] == player_id].shape[0]
    fumble_recoveries += player_games[player_games['fumble_recovery_2_player_id'] == player_id].shape[0]
    
    # Pass defenses
    pass_defenses = player_games[player_games['pass_defense_1_player_id'] == player_id].shape[0]
    pass_defenses += player_games[player_games['pass_defense_2_player_id'] == player_id].shape[0]
    
    # Tackles for loss
    tackles_for_loss = player_games[player_games['tackle_for_loss_1_player_id'] == player_id].shape[0]
    tackles_for_loss += player_games[player_games['tackle_for_loss_2_player_id'] == player_id].shape[0]
    
    # QB hits
    qb_hits = player_games[player_games['qb_hit_1_player_id'] == player_id].shape[0]
    qb_hits += player_games[player_games['qb_hit_2_player_id'] == player_id].shape[0]
    
    return pd.Series({
        'solo_tackles': solo_tackles,
        'assisted_tackles': assist_tackles,
        'tackles_for_loss': tackles_for_loss,
        'qb_hits': qb_hits,
        'sacks': sacks,
        'interceptions': interceptions,
        'forced_fumbles': forced_fumbles,
        'fumble_recoveries': fumble_recoveries,
        'pass_defenses': pass_defenses
    })

# Apply the function to each defensive player
defensive_player_stats = []
for _, row in defensive_players.iterrows():
    stats = calculate_defensive_player_stats(row['player_id'], row['player_name'], row['game_id'], row['defteam'])
    stats['game_id'] = row['game_id']
    stats['player_id'] = row['player_id']
    stats['player_name'] = row['player_name']
    stats['posteam'] = row['defteam']  # Use defteam as posteam for consistency
    defensive_player_stats.append(stats)

# Convert to DataFrame
defensive_player_stats_df = pd.DataFrame(defensive_player_stats)

# 4. Additional Context Stats
context_stats = sf_games.groupby(['game_id', 'posteam']).agg(
    total_plays=('play_id', 'count'),
    third_down_attempts=('down', lambda x: (x == 3).sum()),
    third_down_conversions=('third_down_converted', 'sum'),
    fourth_down_attempts=('down', lambda x: (x == 4).sum()),
    fourth_down_conversions=('fourth_down_converted', 'sum'),
    red_zone_attempts=('yardline_100', lambda x: (x <= 20).sum()),
    red_zone_touchdowns=('touchdown', lambda x: ((x == 1) & (sf_games['yardline_100'] <= 20)).sum()),
    avg_field_position=('yardline_100', 'mean'),
    total_epa=('epa', 'sum')
).reset_index()

# Rename columns for consistency
advanced_passing = advanced_passing.rename(columns={'passer_player_id': 'player_id', 'passer_player_name': 'player_name'})
advanced_rushing = advanced_rushing.rename(columns={'rusher_player_id': 'player_id', 'rusher_player_name': 'player_name'})
advanced_receiving = advanced_receiving.rename(columns={'receiver_player_id': 'player_id', 'receiver_player_name': 'player_name'})

# Merge all enhanced stats
enhanced_stats = pd.merge(advanced_passing, advanced_rushing, on=['game_id', 'player_id', 'player_name', 'posteam'], how='outer')
enhanced_stats = pd.merge(enhanced_stats, advanced_receiving, on=['game_id', 'player_id', 'player_name', 'posteam'], how='outer')

# Add defensive player stats
enhanced_stats = pd.merge(enhanced_stats, defensive_player_stats_df, on=['game_id', 'player_id', 'player_name', 'posteam'], how='outer')

# Add roster information
enhanced_stats = enhanced_stats.merge(
    roster_df[['player_id', 'position', 'team']],
    on='player_id',
    how='left'
)

# Fill NaN values with 0
enhanced_stats = enhanced_stats.fillna(0)

# Filter to only San Francisco 49ers players
enhanced_stats = enhanced_stats[enhanced_stats['posteam'] == team_abbr]

# Export enhanced stats
enhanced_output_path = "49ers_2024_enhanced_stats.csv"
enhanced_stats.to_csv(enhanced_output_path, index=False)
print(f"Saved enhanced player statistics to {enhanced_output_path}")

# Preview enhanced stats
print("\nEnhanced Stats Preview:")
print(enhanced_stats.head())

# =============================================
# SECTION 3: COLUMN DEFINITIONS
# =============================================

print("\nGenerating column definitions...")

# Create a dictionary of column definitions
column_definitions = {
    # Basic identifiers
    'game_id': 'Unique identifier for each game (format: YYYY_WK_HOME_AWAY)',
    'player_id': 'Unique identifier for each player',
    'player_name': 'Player name (Last.First format)',
    'posteam': 'Team the player was on for this play',
    'position': 'Player position (QB, RB, WR, TE, OL, DL, LB, DB, etc.)',
    'team': 'Team the player was on for the season',
    
    # Passing stats
    'passing_yards': 'Total passing yards',
    'passing_tds': 'Total passing touchdowns',
    'air_yards': 'Total air yards (distance ball traveled in the air)',
    'yards_after_catch': 'Total yards after catch (YAC)',
    'cpoe': 'Completion Percentage Over Expected (average)',
    'qb_epa': 'Expected Points Added by quarterback',
    'pass_attempts': 'Number of pass attempts',
    'complete_passes': 'Number of completed passes',
    'avg_air_yards': 'Average air yards per pass attempt',
    'avg_yac': 'Average yards after catch per reception',
    'pass_location_left': 'Number of passes thrown to the left side of the field',
    'pass_location_middle': 'Number of passes thrown to the middle of the field',
    'pass_location_right': 'Number of passes thrown to the right side of the field',
    'pass_length_short': 'Number of short passes (0-9 yards)',
    'pass_length_medium': 'Number of medium passes (10-19 yards)',
    'pass_length_deep': 'Number of deep passes (20+ yards)',
    
    # Rushing stats
    'rushing_yards': 'Total rushing yards',
    'rushing_tds': 'Total rushing touchdowns',
    'rush_attempts': 'Number of rush attempts',
    'first_downs_rush': 'Number of first downs achieved by rushing',
    'xyac_mean': 'Expected Yards After Contact (mean)',
    'xyac_median': 'Expected Yards After Contact (median)',
    'xyac_success_rate': 'Expected Yards After Contact success rate',
    'rush_epa': 'Expected Points Added by rushing plays',
    'run_location_left': 'Number of rushes to the left side of the field',
    'run_location_middle': 'Number of rushes to the middle of the field',
    'run_location_right': 'Number of rushes to the right side of the field',
    'run_gap_guard': 'Number of rushes through the guard gap',
    'run_gap_tackle': 'Number of rushes through the tackle gap',
    'run_gap_end': 'Number of rushes through the end gap',
    
    # Receiving stats
    'receiving_yards': 'Total receiving yards',
    'receiving_tds': 'Total receiving touchdowns',
    'receiving_attempts': 'Number of pass attempts targeting this player',
    'first_downs_receiving': 'Number of first downs achieved by receiving',
    'receiving_epa': 'Expected Points Added by receiving plays',
    'avg_yac_y': 'Average yards after catch per reception',
    'avg_air_yards_y': 'Average air yards per target',
    
    # Defensive stats
    'solo_tackles': 'Number of solo tackles',
    'assisted_tackles': 'Number of assisted tackles',
    'tackles_for_loss': 'Number of tackles for loss',
    'qb_hits': 'Number of quarterback hits',
    'sacks': 'Number of sacks (including half sacks)',
    'interceptions': 'Number of interceptions',
    'forced_fumbles': 'Number of forced fumbles',
    'fumble_recoveries': 'Number of fumble recoveries',
    'pass_defenses': 'Number of pass defenses (passes defended)',
    
    # Context stats
    'total_plays': 'Total number of plays',
    'third_down_attempts': 'Number of third down attempts',
    'third_down_conversions': 'Number of third down conversions',
    'fourth_down_attempts': 'Number of fourth down attempts',
    'fourth_down_conversions': 'Number of fourth down conversions',
    'red_zone_attempts': 'Number of plays in the red zone (inside 20-yard line)',
    'red_zone_touchdowns': 'Number of touchdowns scored in the red zone',
    'avg_field_position': 'Average field position (yard line)',
    'total_epa': 'Total Expected Points Added'
}

# Create a DataFrame from the dictionary
column_definitions_df = pd.DataFrame({
    'column_name': list(column_definitions.keys()),
    'definition': list(column_definitions.values())
})

# Export column definitions
column_definitions_path = "49ers_2024_column_definitions.csv"
column_definitions_df.to_csv(column_definitions_path, index=False)
print(f"Saved column definitions to {column_definitions_path}")

print("\nScript completed successfully!")
