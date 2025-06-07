"""Additional tests for Tic Tac Toe to achieve 100% coverage."""
import unittest
from games.tic_tac_toe import TicTacToeGame
from game_abc import GameMove

class TestTicTacToeExtra(unittest.TestCase):
    """Additional test cases for Tic Tac Toe."""
    
    def setUp(self):
        """Set up test fixture."""
        self.game = TicTacToeGame("test_game")
    
    def test_init_game_state(self):
        """Test _init_game_state method."""
        # This should call initialize_game()
        self.game._init_game_state()
        self.assertEqual(self.game.current_player, "X")
        self.assertEqual(self.game.board, [[None] * 3 for _ in range(3)])
    
    def test_update_game_state(self):
        """Test _update_game_state method."""
        # This is a no-op method, just verify it doesn't raise an exception
        self.game._update_game_state({})
        
        # Make sure it doesn't modify the game state
        self.assertEqual(self.game.current_player, "X")
    
    def test_validate_move_game_over(self):
        """Test validate_move when game is over."""
        # Force game over by filling the board
        self.game.board = [
            ["X", "O", "X"],
            ["X", "O", "O"],
            ["O", "X", "X"]
        ]
        self.assertTrue(self.game.is_game_over())
        
        # Should return False since game is over
        self.assertFalse(self.game.validate_move({"row": 0, "col": 0, "player": "X"}))
    
    def test_validate_move_exceptions(self):
        """Test exception handling in validate_move."""
        # Test with invalid move data (missing 'row' key)
        # Should return False instead of raising KeyError
        self.assertFalse(self.game.validate_move({"col": 0, "player": "X"}))
        
        # Test with invalid move data (non-integer row/col)
        # Should return False instead of raising ValueError
        self.assertFalse(self.game.validate_move({"row": "a", "col": 0, "player": "X"}))
        
        # Test with invalid move data (wrong type)
        # This will raise an AttributeError when trying to call .get() on a string
        with self.assertRaises(AttributeError):
            self.game.validate_move("not a dict")
    
    def test_make_move_add_player_to_move(self):
        """Test make_move when player needs to be added to move data."""
        # Make a move without specifying player in the move data
        # The player should be added automatically from current_player (X)
        result = self.game.make_move({"move_data": {"row": 0, "col": 0}})
        self.assertEqual(result["board"][0][0], "X")
        self.assertEqual(result["current_player"], "O")  # Player should switch
        
        # Make another move for O without specifying player
        result = self.game.make_move({"move_data": {"row": 1, "col": 1}})
        self.assertEqual(result["board"][1][1], "O")
        self.assertEqual(result["current_player"], "X")  # Player should switch back
    
    def test_make_move_game_over(self):
        """Test make_move when game is over."""
        # Force game over by filling the board
        self.game.board = [
            ["X", "O", "X"],
            ["X", "O", "O"],
            ["O", "X", "X"]
        ]
        
        # Should raise ValueError since game is over
        with self.assertRaises(ValueError):
            self.game.make_move({"row": 0, "col": 0, "player": "X"})

if __name__ == "__main__":
    unittest.main()
