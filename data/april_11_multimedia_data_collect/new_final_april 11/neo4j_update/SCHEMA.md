# Updated Neo4j Game Node Schema

## Game Node

After running the `update_game_nodes.py` script, Game nodes in the Neo4j database will have the following attributes:

| Attribute           | Type   | Description                                   |
|---------------------|--------|-----------------------------------------------|
| game_id             | String | Primary key for the game                      |
| date                | String | Game date                                     |
| location            | String | Game location                                 |
| home_team           | String | Home team name                                |
| away_team           | String | Away team name                                |
| result              | String | Game result (score)                           |
| summary             | String | Brief game summary                            |
| home_team_logo_url  | String | URL to the home team's logo image             |
| away_team_logo_url  | String | URL to the away team's logo image             |
| highlight_video_url | String | URL to the game's highlight video             |
| embedding           | Vector | Vector embedding of the game summary (if any) |

## Assumptions and Implementation Notes

1. The update script uses `game_id` as the primary key to match existing Game nodes.
2. The script only updates the following attributes:
   - home_team_logo_url
   - away_team_logo_url
   - highlight_video_url
3. The script does not modify existing attributes or create new Game nodes.
4. The data source for updates is the `schedule_with_result_april_11.csv` file.

## Usage

To update the Game nodes, run the following command from the project root:

```bash
python ifx-sandbox/data/april_11_multimedia_data_collect/new_final_april\ 11/neo4j_update/update_game_nodes.py
```

The script will:
1. Prompt for confirmation before making any changes
2. Connect to Neo4j using credentials from the .env file
3. Update Game nodes with the new attributes
4. Report on the success/failure of the updates
5. Verify that the updates were applied correctly 