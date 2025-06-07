"""
Tests for Tic Tac Toe game.
"""
import unittest
from games.tic_tac_toe import TicTacToeGame
from tests.base_test import BaseGameTest


class TestTicTacToeGame(BaseGameTest):
    """Test cases for Tic Tac Toe game."""
    
    GAME_CLASS = TicTacToeGame
    
    def test_initial_state(self):
        """Test the initial game state."""
        state = self.game.get_game_state()
        
        # Check basic game state structure
        self.assertValidGameState(state)
        self.assertIn('board', state)
        self.assertIn('current_player', state)
        self.assertIn('game_over', state)
        self.assertIn('winner', state)
        
        # Check initial board is empty
        self.assertEqual(len(state['board']), 3)
        for row in state['board']:
            self.assertEqual(len(row), 3)
            self.assertTrue(all(cell is None for cell in row))
        
        # Initial player should be 'X'
        self.assertEqual(state['current_player'], 'X')
        self.assertFalse(state['game_over'])
        self.assertIsNone(state['winner'])
    
    def test_valid_moves(self):
        """Test valid moves."""
        # Test first move by X
        state = self.make_move('X', {'row': 0, 'col': 0})
        self.assertEqual(state['board'][0][0], 'X')
        self.assertEqual(state['current_player'], 'O')
        
        # Test second move by O
        state = self.make_move('O', {'row': 1, 'col': 1})
        self.assertEqual(state['board'][1][1], 'O')
        self.assertEqual(state['current_player'], 'X')
        
        # Test another move by X
        state = self.make_move('X', {'row': 0, 'col': 1})
        self.assertEqual(state['board'][0][1], 'X')
        self.assertEqual(state['current_player'], 'O')
    
    def test_invalid_moves(self):
        """Test invalid moves."""
        # Move out of bounds
        with self.assertRaises(ValueError):
            self.make_move('X', {'row': -1, 'col': 0})
        with self.assertRaises(ValueError):
            self.make_move('X', {'row': 3, 'col': 0})
        with self.assertRaises(ValueError):
            self.make_move('X', {'row': 0, 'col': -1})
        with self.assertRaises(ValueError):
            self.make_move('X', {'row': 0, 'col': 3})
    
        # Test occupied cell
        self.make_move('X', {'row': 0, 'col': 0})
        with self.assertRaises(ValueError):
            self.make_move('O', {'row': 0, 'col': 0})  # Cell already occupied
    
        # Test wrong player's turn
        # Current state: X at (0,0), O's turn
        with self.assertRaises(ValueError):
            # X tries to go again, but it's O's turn
            self.make_move('X', {'row': 0, 'col': 1})
    
    def test_row_win(self):
        """Test winning by row."""
        # X | X | X
        # O | O |
        #   |   |
        moves = [
            ('X', {'row': 0, 'col': 0}),  # X
            ('O', {'row': 1, 'col': 0}),  # O
            ('X', {'row': 0, 'col': 1}),  # X
            ('O', {'row': 1, 'col': 1}),  # O
            ('X', {'row': 0, 'col': 2}),  # X wins
        ]
        
        for player, move in moves:
            state = self.make_move(player, move)
        
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'X')
    
    def test_column_win(self):
        """Test winning by column."""
        # O | X |
        # O | X |
        #   | X |
        moves = [
            ('X', {'row': 0, 'col': 1}),  # X
            ('O', {'row': 0, 'col': 0}),  # O
            ('X', {'row': 1, 'col': 1}),  # X
            ('O', {'row': 1, 'col': 0}),  # O
            ('X', {'row': 2, 'col': 1}),  # X wins
        ]
        
        for player, move in moves:
            state = self.make_move(player, move)
        
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'X')
    
    def test_diagonal_win(self):
        """Test winning by diagonal."""
        # X | O |
        #   | X | O
        #   |   | X
        moves = [
            ('X', {'row': 0, 'col': 0}),  # X
            ('O', {'row': 0, 'col': 1}),  # O
            ('X', {'row': 1, 'col': 1}),  # X
            ('O', {'row': 1, 'col': 2}),  # O
            ('X', {'row': 2, 'col': 2}),  # X wins
        ]
        
        for player, move in moves:
            state = self.make_move(player, move)
        
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'X')
    
    def test_anti_diagonal_win(self):
        """Test winning by anti-diagonal."""
        #   | O | X
        #   | X |
        # X |   |
        moves = [
            ('X', {'row': 0, 'col': 2}),  # X
            ('O', {'row': 0, 'col': 1}),  # O
            ('X', {'row': 1, 'col': 1}),  # X
            ('O', {'row': 1, 'col': 0}),  # O - not in the winning path
            ('X', {'row': 2, 'col': 0}),  # X - wins (0,2), (1,1), (2,0)
        ]
        
        for player, move in moves:
            state = self.make_move(player, move)
        
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'X')
    
    def test_draw_condition(self):
        """Test a draw game."""
        # X | O | X
        # X | O | O
        # O | X | X
        moves = [
            ('X', {'row': 0, 'col': 0}),  # X
            ('O', {'row': 0, 'col': 1}),  # O
            ('X', {'row': 0, 'col': 2}),  # X
            ('O', {'row': 1, 'col': 1}),  # O
            ('X', {'row': 1, 'col': 0}),  # X
            ('O', {'row': 2, 'col': 0}),  # O
            ('X', {'row': 1, 'col': 2}),  # X
            ('O', {'row': 2, 'col': 2}),  # O
            ('X', {'row': 2, 'col': 1}),  # X - Draw
        ]
        
        for player, move in moves:
            state = self.make_move(player, move)
        
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'draw')
    
    def test_game_flow(self):
        """Test a complete game flow with X winning."""
        # X | O |
        # X | O |
        # X |   |
        moves = [
            ('X', {'row': 0, 'col': 0}),  # X
            ('O', {'row': 0, 'col': 1}),  # O
            ('X', {'row': 1, 'col': 0}),  # X
            ('O', {'row': 1, 'col': 1}),  # O
            ('X', {'row': 2, 'col': 0}),  # X - wins (vertical)
        ]
        
        for i, (player, move) in enumerate(moves):
            state = self.make_move(player, move)
            # Game should only be over after the last move
            if i < len(moves) - 1:
                self.assertFalse(state['game_over'])
                self.assertIsNone(state['winner'])
            else:
                self.assertTrue(state['game_over'])
                self.assertEqual(state['winner'], 'X')
    
    def test_move_after_game_over(self):
        """Test that moves can't be made after game is over."""
        # X | X | X
        #   |   |
        #   |   |
        moves = [
            ('X', {'row': 0, 'col': 0}),  # X
            ('O', {'row': 1, 'col': 0}),  # O
            ('X', {'row': 0, 'col': 1}),  # X
            ('O', {'row': 1, 'col': 1}),  # O
            ('X', {'row': 0, 'col': 2}),  # X - wins
        ]
        
        for player, move in moves:
            self.make_move(player, move)
        
        # Try to make another move after game is over
        with self.assertRaises(ValueError):
            self.make_move('O', {'row': 2, 'col': 2})
