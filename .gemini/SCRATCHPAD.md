
- the original app was for something else and not using containers. Assume the README.md and *.py files, etc in the root folder to be old and unused. For most of the time focus on the api folder.

## player profiles

the player profiles are in the data/huge-league/players folder in json format. The files are int he format of `team_name_player_number.json`.

### scripts

- api/scripts/create_player_profiles.py - this script created the original player profiles.
- api/scripts/model_player.py - was a simple model for crud operations on the player profiles. 
- api/scripts/vectorstore_load.py - this script loads the player profiles into the vector store file.
