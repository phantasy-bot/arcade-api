"""Base test class for all game tests."""

import unittest
from game_abc import AbstractGame, GameMove
from typing import Dict, Any, Type, List, Optional
import time
import copy
from dataclasses import asdict


class BaseGameTest(unittest.TestCase):
    """
    Base class for game tests.

    Subclasses must set the GAME_CLASS class variable to the game class being tested.
    """

    GAME_CLASS: Type[AbstractGame] = None

    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        if cls is BaseGameTest:
            raise unittest.SkipTest("Skip BaseTest tests, it's a base class")
        if cls.GAME_CLASS is None:
            raise unittest.SkipTest("GAME_CLASS not set")

    def setUp(self):
        """Set up the test case."""
        self.game = self.GAME_CLASS(game_id=f"test_game_{id(self)}")
        self.game.initialize_game()

    def make_move(self, player: str, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to make a move."""
        # Create a copy of move_data to avoid modifying the input
        move_data_copy = copy.deepcopy(move_data)
        # Add player to move data if not present
        if "player" not in move_data_copy:
            move_data_copy["player"] = player
        # For chess, we'll pass the move data directly
        # as the chess game expects the move data in a specific format
        return self.game.make_move(move_data_copy)

    def assertValidGameState(self, state: Dict[str, Any]):
        """Assert that the game state is valid."""
        self.assertIsInstance(state, dict)
        self.assertIn("board", state)
        self.assertIn("current_player", state)
        self.assertIn("game_over", state)
        self.assertIn("winner", state)

        # Check board structure
        self.assertIsInstance(state["board"], list)
        for row in state["board"]:
            self.assertIsInstance(row, list)
            for cell in row:
                # Valid cell contents: None, string (for simple games), or dict (for complex games like Shogi)
                if isinstance(cell, dict):
                    self.assertIn("type", cell, "Shogi piece dict should have a 'type' key")
                    # Shogi piece types are stored in lowercase in the dict
                    shogi_base_piece_types = ["k", "g", "s", "n", "l", "p", "b", "r"]
                    self.assertIn(cell["type"], shogi_base_piece_types, f"Unknown Shogi piece type: {cell.get('type')}")
                    self.assertIn("color", cell, "Shogi piece dict should have a 'color' key")
                    self.assertIn(cell["color"], ["w", "b"], f"Unknown Shogi piece color: {cell.get('color')}")
                    self.assertIn("promoted", cell, "Shogi piece dict should have a 'promoted' key")
                    self.assertIsInstance(cell["promoted"], bool, "Shogi piece 'promoted' should be a boolean")
                elif cell is not None and not isinstance(cell, str): # Catch unexpected types
                    self.fail(f"Board cell content must be None, a string, or a dictionary, but got {type(cell)}: {cell}")
                else: # Cell is None or a string
                    valid_string_cells = [None, "X", "O", "R", "Y", "B", "W", "B_KING", "W_KING", 
                                          "P", "L", "N", "S", "G", "K", 
                                          "R_P", "B_P", "+P", "+L", "+N", "+S"] # Original list for non-dict cells
                    self.assertIn(cell, valid_string_cells, f"Invalid string cell content: {cell}")

        # Check current player (supporting multiple game formats)
        self.assertIn(state["current_player"], ["X", "O", "R", "Y", "B", "W", "Sente", "Gote", "w", "b"]) # Added Shogi players w/b

        # Check game over and winner consistency
        if state["game_over"]:
            self.assertIn(state["winner"], [None, "X", "O", "R", "Y", "B", "W", "Sente", "Gote", "draw", "w", "b"]) # Added Shogi players w/b
        else:
            self.assertIsNone(state["winner"])

    def test_initial_state(self):
        """Test the initial game state."""
        state = self.game.get_game_state()
        self.assertValidGameState(state)
        self.assertFalse(state["game_over"])
        self.assertIsNone(state["winner"])

    def test_game_flow(self):
        """Test a complete game flow."""
        # This should be overridden by specific game tests
        pass
