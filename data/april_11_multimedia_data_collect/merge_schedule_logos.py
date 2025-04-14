import pandas as pd
import os

# Read the CSV files
schedule_df = pd.read_csv('data/april_11_multimedia_data_collect/nfl-2024-san-francisco-49ers-with-results.csv')
logos_df = pd.read_csv('data/april_11_multimedia_data_collect/nfl_team_logos_revised.csv')

# Create dictionaries to map team names to logo URLs
home_logos = {}
away_logos = {}

for _, row in logos_df.iterrows():
    home_logos[row['team_name']] = row['logo_url']
    away_logos[row['team_name']] = row['logo_url']

# Add logo URL columns to the schedule dataframe
schedule_df['home_team_logo_url'] = schedule_df['Home Team'].map(home_logos)
schedule_df['away_team_logo_url'] = schedule_df['Away Team'].map(away_logos)

# Save the merged dataframe to a new CSV file
output_path = 'data/april_11_multimedia_data_collect/schedule_with_result_and_logo_urls.csv'
schedule_df.to_csv(output_path, index=False)

print(f'CSV file created successfully at {output_path}!') 