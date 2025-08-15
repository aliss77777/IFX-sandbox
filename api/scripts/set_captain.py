import os
import sys

from model_player import Player


def set_captain(team_name: str, player_jersey_number: int):
    """
    Sets a new team captain, demoting the old one if necessary.
    """
    # Demote current captain if one exists
    current_captain = Player.get_captain(team_name)
    if current_captain:
        print(f"Demoting current captain: {current_captain.name}")
        current_captain.update_captain_status(False)

    # Promote new captain
    new_captain = Player.get_player_by_number(team_name, player_jersey_number)
    if not new_captain:
        print(
            f"Error: Player with number {player_jersey_number} not found in team {team_name}."
        )
        sys.exit(1)

    print(f"Promoting new captain: {new_captain.name}")
    new_captain.update_captain_status(True)

    print("Captain updated successfully.")

    # # Reload vector store
    # print("Reloading vector store...")
    # try:
    #     # Assuming the script is run from the root of the repository
    #     subprocess.run(['python', 'api/scripts/vectorstore_load.py'], check=True)
    #     print("Vector store reloaded successfully.")
    # except subprocess.CalledProcessError as e:
    #     print(f"Error reloading vector store: {e}")
    #     sys.exit(1)
    # except FileNotFoundError:
    #     print("Error: 'python' command not found. Make sure Python is in your PATH.")
    #     sys.exit(1)


if __name__ == "__main__":
    # This allows the script to be run from the root directory
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

    if len(sys.argv) != 3:
        print(
            "Usage: python api/scripts/set_captain.py <team_name> <player_jersey_number>"
        )
        sys.exit(1)

    team_name_arg = sys.argv[1].replace("_", " ")
    player_number_arg = int(sys.argv[2])

    set_captain(team_name_arg, player_number_arg)
