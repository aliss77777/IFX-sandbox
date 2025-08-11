import unittest
import os
import json
import sys
from unittest.mock import patch, MagicMock

# Add api/scripts to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from model_player import Player
from set_captain import set_captain

class TestSetCaptain(unittest.TestCase):

    TEST_TEAM_NAME = "Test FC"
    TEST_PLAYER_DIR = "/workspace/data/huge-league/players"

    def setUp(self):
        """Set up a dummy team and players for testing."""
        self.player1_data = {
            "team": self.TEST_TEAM_NAME, "number": 1, "name": "Test Player 1",
            "age": 25, "nationality": "Testland", "shirt_number": 1,
            "position": "Striker", "preferred_foot": "Right", "role": "Starter",
            "bio": "A test player.", "is_captain": False
        }
        self.player2_data = {
            "team": self.TEST_TEAM_NAME, "number": 2, "name": "Test Player 2",
            "age": 28, "nationality": "Testland", "shirt_number": 2,
            "position": "Center Back", "preferred_foot": "Left", "role": "Starter",
            "bio": "Another test player.", "is_captain": False
        }
        self._create_test_player_file(self.player1_data)
        self._create_test_player_file(self.player2_data)

    def tearDown(self):
        """Clean up dummy player files."""
        self._delete_test_player_file(self.player1_data)
        self._delete_test_player_file(self.player2_data)

    def _create_test_player_file(self, player_data):
        player = Player.model_validate(player_data)
        player.save()

    def _delete_test_player_file(self, player_data):
        filename = f"{player_data['team'].replace(' ', '_')}_{player_data['number']}.json"
        filepath = os.path.join(self.TEST_PLAYER_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    def test_initial_state(self):
        """Test that initially there is no captain."""
        captain = Player.get_captain(self.TEST_TEAM_NAME)
        self.assertIsNone(captain)

    @patch('set_captain.subprocess.run')
    def test_promote_first_captain(self, mock_subprocess_run):
        """Test promoting a player to be the first captain."""
        set_captain(self.TEST_TEAM_NAME, 1)

        # Verify player 1 is captain
        p1 = Player.get_player_by_number(self.TEST_TEAM_NAME, 1)
        self.assertTrue(p1.is_captain)
        self.assertIn("is the team captain", p1.bio)

        # Verify player 2 is not captain
        p2 = Player.get_player_by_number(self.TEST_TEAM_NAME, 2)
        self.assertFalse(p2.is_captain)

        # Verify vectorstore reload was called
        mock_subprocess_run.assert_called_once_with(['python', 'api/scripts/vectorstore_load.py'], check=True)

    @patch('set_captain.subprocess.run')
    def test_change_captain(self, mock_subprocess_run):
        """Test changing the captain from one player to another."""
        # 1. Make player 1 the captain first
        set_captain(self.TEST_TEAM_NAME, 1)
        p1_initial = Player.get_player_by_number(self.TEST_TEAM_NAME, 1)
        self.assertTrue(p1_initial.is_captain)

        # 2. Now, change captain to player 2
        set_captain(self.TEST_TEAM_NAME, 2)

        # Verify player 1 is no longer captain
        p1_final = Player.get_player_by_number(self.TEST_TEAM_NAME, 1)
        self.assertFalse(p1_final.is_captain)
        self.assertNotIn("is the team captain", p1_final.bio)

        # Verify player 2 is now captain
        p2 = Player.get_player_by_number(self.TEST_TEAM_NAME, 2)
        self.assertTrue(p2.is_captain)
        self.assertIn("is the team captain", p2.bio)

        # Verify only one captain exists
        captains = [p for p in Player.get_players(self.TEST_TEAM_NAME) if p.is_captain]
        self.assertEqual(len(captains), 1)
        self.assertEqual(captains[0].number, 2)

        # Verify vectorstore reload was called twice
        self.assertEqual(mock_subprocess_run.call_count, 2)

    @patch('set_captain.subprocess.run')
    def test_non_existent_player(self, mock_subprocess_run):
        """Test attempting to promote a non-existent player."""
        with self.assertRaises(SystemExit) as cm:
            set_captain(self.TEST_TEAM_NAME, 99)
        self.assertEqual(cm.exception.code, 1)
        mock_subprocess_run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
