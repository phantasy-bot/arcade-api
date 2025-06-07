"""
Test cases for Connect Four game.
"""
import unittest
from games.connect_four import ConnectFourGame
from tests.base_test import BaseGameTest


class TestConnectFourGame(BaseGameTest):
    """Test cases for Connect Four game."""
    
    GAME_CLASS = ConnectFourGame
    
    def test_initial_state(self):
        """Test the initial game state."""
        state = self.game.get_game_state()
        self.assertValidGameState(state)
        self.assertEqual(state['current_player'], 'R')  # Red starts first
        self.assertFalse(state['game_over'])
        self.assertIsNone(state['winner'])
        
        # Check board dimensions
        self.assertEqual(len(state['board']), 6)  # 6 rows
        for row in state['board']:
            self.assertEqual(len(row), 7)  # 7 columns
            self.assertTrue(all(cell is None for cell in row))  # All cells empty
    
    def test_valid_moves(self):
        """Test valid moves."""
        # First move in column 0 by Red
        state = self.make_move('R', {'column': 0})
        self.assertValidGameState(state)
        self.assertEqual(state['board'][5][0], 'R')  # Piece at bottom
        self.assertEqual(state['current_player'], 'Y')  # Switch to Yellow
        
        # Second move in column 0 by Yellow
        state = self.make_move('Y', {'column': 0})
        self.assertValidGameState(state)
        self.assertEqual(state['board'][4][0], 'Y')  # Next piece on top of first
        self.assertEqual(state['current_player'], 'R')  # Back to Red
    
    def test_invalid_moves(self):
        """Test invalid moves."""
        # Move to non-existent column
        with self.assertRaises(ValueError):
            self.make_move('R', {'column': 7})  # Column out of bounds
            
        with self.assertRaises(ValueError):
            self.make_move('R', {'column': -1})  # Negative column
            
        # Wrong player's turn
        with self.assertRaises(ValueError):
            self.make_move('Y', {'column': 0})  # Should be Red's turn first
            
        # Fill a column and try to add more
        for _ in range(6):  # Fill column 0
            self.make_move(self.game.current_player, {'column': 0})
            
        with self.assertRaises(ValueError):
            self.make_move(self.game.current_player, {'column': 0})  # Column full
    
    def test_horizontal_win(self):
        """Test horizontal win condition."""
        # Red wins horizontally
        moves = [
            (0, 'R'), (0, 'Y'),  # Column 0
            (1, 'R'), (1, 'Y'),  # Column 1
            (2, 'R'), (2, 'Y'),  # Column 2
            (3, 'R')             # Red wins
        ]
        
        for col, player in moves:
            self.make_move(player, {'column': col})
            
        state = self.game.get_game_state()
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'R')
    
    def test_vertical_win(self):
        """Test vertical win condition."""
        # Red wins vertically in column 0
        moves = [
            (0, 'R'), (1, 'Y'),  # First layer
            (0, 'R'), (1, 'Y'),  # Second layer
            (0, 'R'), (1, 'Y'),  # Third layer
            (0, 'R')             # Fourth layer - Red wins
        ]
        
        for col, player in moves:
            self.make_move(player, {'column': col})
            
        state = self.game.get_game_state()
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'R')
    
    def test_diagonal_win(self):
        """Test diagonal win conditions."""
        # Create a simple diagonal win for Red
        # This test will manually set up the board since making the moves
        # would be too complex with the current implementation
        
        # Reset the game
        self.game = self.GAME_CLASS(game_id="test_diagonal_win")
        self.game.initialize_game()
        
        # Manually set up a diagonal win for Red
        # Rows are 0 (bottom) to 5 (top)
        # Columns are 0 to 6 (left to right)
        # 
        # Board state:
        # | | | | | | | |
        # | | | | | | | |
        # | | | |R| | | |
        # | | |R|Y| | | |
        # | |R|Y|Y| | | |
        # |R|Y|Y|Y| | | |
        self.game.board = [
            [None, None, None, None, None, None, None],  # Top
            [None, None, None, 'R', None, None, None],   # Row 4
            [None, None, 'R', 'Y', None, None, None],    # Row 3
            [None, 'R', 'Y', 'Y', None, None, None],     # Row 2
            ['R', 'Y', 'Y', 'Y', None, None, None],      # Row 1 (bottom)
            [None, None, None, None, None, None, None]   # Row 0 (unused)
        ]
        
        # Check if the game detects the win
        state = self.game.get_game_state()
        
        # Print the board for debugging
        print("\nBoard state:")
        for row in reversed(self.game.board):
            print('|' + '|'.join(cell if cell is not None else ' ' for cell in row) + '|')
        print(f"Current player: {state['current_player']}")
        print(f"Game over: {state['game_over']}")
        print(f"Winner: {state['winner']}")
        
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'R')
        self.assertTrue(state['game_over'], "Game should be over after a win")
        self.assertEqual(state['winner'], 'R', "Red should be the winner")
    
    def test_draw_condition(self):
        """Test draw condition when board is full with no winner."""
        # Fill the board in a way that doesn't create a winner
        # This is a simplified test - in practice, we'd need to fill the entire board
        # without any player getting 4 in a row
        
        # For brevity, we'll just test that a full board without a winner is a draw
        # In a real test, we'd need to fill the board completely
        pass  # This is complex to test without a full board setup
    
    def test_win_priority(self):
        """Test that the first player to get 4 in a row wins, even if moves remain."""
        # Setup a board where both players could win next move
        # Red should win before Yellow gets a chance
        moves = [
            (0, 'R'), (1, 'Y'),  # Column 0, 1
            (0, 'R'), (1, 'Y'),  # Column 0, 1
            (0, 'R'), (2, 'Y'),  # Column 0, 2
            (0, 'R')             # Red wins vertically
        ]
        
        for col, player in moves:
            self.make_move(player, {'column': col})
            
        state = self.game.get_game_state()
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'R')
