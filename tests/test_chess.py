"""
Test cases for Chess game.
"""
import unittest
from games.chess import ChessGame, ChessPiece
from tests.base_test import BaseGameTest
from typing import Dict, Any, List, Tuple
import copy


class TestChessGame(BaseGameTest):
    """Test cases for Chess game."""
    
    GAME_CLASS = ChessGame
    
    def test_initial_state(self):
        """Test the initial game state."""
        state = self.game.get_game_state()
        
        # Check basic structure
        self.assertIsInstance(state, dict)
        self.assertIn("board", state)
        self.assertIn("current_player", state)
        self.assertIn("game_over", state)
        self.assertIn("winner", state)
        
        # Check board structure
        self.assertEqual(len(state["board"]), 8)  # 8x8 board
        self.assertEqual(len(state["board"][0]), 8)
        
        # Check initial player is white
        self.assertEqual(state["current_player"], "w")
        
        # Game should not be over at start
        self.assertFalse(state["game_over"])
        self.assertIsNone(state["winner"])
    
    def test_valid_moves(self):
        """Test valid moves for each piece type."""
        # Clear the board for testing
        self.game.board = [[None] * 8 for _ in range(8)]
        self.game.current_player = 'w'
        
        # Place a white pawn at a2 and white knight at b1
        self.game.board[1][0] = ChessPiece('p', 'w')
        self.game.board[0][1] = ChessPiece('n', 'w')
        # Add a black king to prevent premature game over due to no king
        self.game.board[7][4] = ChessPiece('k', 'b') # Black king at e8
        
        # Test knight move first (before pawn moves)
        move_data = {
            'from_row': 0, 'from_col': 1,  # White knight at b1
            'to_row': 2, 'to_col': 0,     # Move to a3
            'piece': 'n',
            'player': 'w'
        }
        state = self.make_move('w', move_data)
        self.assertIsNotNone(state)
        self.assertEqual(state['board'][2][0]['type'], 'n')  # Knight moved to a3
        self.assertEqual(state['current_player'], 'b')  # Turn switched to black
        
        # Switch back to white's turn for pawn move
        self.game.current_player = 'w'
        
        # Test pawn move
        move_data = {
            'from_row': 1, 'from_col': 0,  # White pawn at a2
            'to_row': 2, 'to_col': 0,     # Try to move to a3 (blocked by knight)
            'piece': 'p',
            'player': 'w'
        }
        # This move should fail because the square is occupied
        with self.assertRaises(ValueError):
            self.make_move('w', move_data)
            
        # Debug: Print board state before pawn move
        print("\nBoard before pawn move:")
        for row in range(8):
            print([str(self.game.board[row][col]) if self.game.board[row][col] else '.' for col in range(8)])
        
        # The pawn at (1,0) can't move two squares to (3,0) because the path is blocked by the knight at (2,0)
        # So we'll test a one-square move instead
        move_data = {
            'from_row': 1, 'from_col': 0,  # White pawn at a2
            'to_row': 2, 'to_col': 0,     # Try to move to a3 (blocked by knight)
            'piece': 'p',
            'player': 'w'
        }
        
        # This move should fail because the destination is occupied by a friendly piece
        with self.assertRaises(ValueError):
            self.make_move('w', move_data)
            
        # Let's test a valid one-square pawn move in a different position
        # First, clear the board and place a pawn at a3
        self.game.board = [[None] * 8 for _ in range(8)]
        self.game.board[2][0] = ChessPiece('p', 'w')  # White pawn at a3
        self.game.current_player = 'w'
        
        # Move pawn from a3 to a4 (one square)
        move_data = {
            'from_row': 2, 'from_col': 0,  # White pawn at a3
            'to_row': 3, 'to_col': 0,     # Move to a4
            'piece': 'p',
            'player': 'w'
        }
        
        state = self.make_move('w', move_data)
        self.assertIsNotNone(state)
        self.assertEqual(state['board'][3][0]['type'], 'p')  # Pawn moved to a4
    
    def test_invalid_moves(self):
        """Test various invalid moves."""
        # Try to move opponent's piece
        move_data = {
            'from_row': 6, 'from_col': 0,  # Black pawn at a7
            'to_row': 5, 'to_col': 0,     # Try to move to a6
            'piece': 'p',
            'player': 'w'   # But it's white's turn
        }
        with self.assertRaises(ValueError):
            self.make_move('w', move_data)
            
        # Try to move to an invalid square
        move_data = {
            'from_row': 1, 'from_col': 0,  # White pawn at a2
            'to_row': 9, 'to_col': 0,     # Off the board
            'piece': 'p',
            'player': 'w'
        }
        with self.assertRaises(ValueError):
            self.make_move('w', move_data)
            
        # Try to move through a piece
        move_data = {
            'from_row': 0, 'from_col': 0,  # White rook at a1
            'to_row': 0, 'to_col': 7,     # Try to move to h1
            'piece': 'r',
            'player': 'w'
        }
        with self.assertRaises(ValueError):
            self.make_move('w', move_data)
    
    def test_game_flow(self):
        """Test a complete game flow with checkmate."""
        # This is a simple checkmate in 4 moves (Fool's mate)
        moves = [
            # White moves f3
            {'from_row': 1, 'from_col': 5, 'to_row': 2, 'to_col': 5, 'piece': 'p', 'player': 'w'},
            # Black moves e5
            {'from_row': 6, 'from_col': 4, 'to_row': 4, 'to_col': 4, 'piece': 'p', 'player': 'b'},
            # White moves g4
            {'from_row': 1, 'from_col': 6, 'to_row': 3, 'to_col': 6, 'piece': 'p', 'player': 'w'},
            # Black delivers checkmate Qh4#
            {'from_row': 7, 'from_col': 3, 'to_row': 3, 'to_col': 7, 'piece': 'q', 'player': 'b'},
        ]
        
        # Play all moves
        state = None
        for move in moves:
            state = self.make_move(move['player'], move)
            
        # Game should be over with black as winner
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'b')
        self.assertTrue(state['in_check'])
        self.assertEqual(state['current_player'], 'b')  # Game ends on black's move
    
    def test_win_condition(self):
        """Test checkmate win condition."""
        # Set up a checkmate position (Fool's mate)
        self.game.board = [[None] * 8 for _ in range(8)]
        self.game.current_player = 'w'
        
        # Place kings
        self.game.board[0][4] = ChessPiece('k', 'w')  # White king at e1
        self.game.board[7][4] = ChessPiece('k', 'b')  # Black king at e8
        
        # Add white pieces to make Fool's Mate a true checkmate in sparse setup
        self.game.board[0][3] = ChessPiece('r', 'w')  # White rook at d1 (blocks d1 for King)
        self.game.board[0][5] = ChessPiece('b', 'w')  # White bishop at f1 (blocks f1 for King)
        self.game.board[1][3] = ChessPiece('p', 'w')  # White pawn at d2 (blocks d2 for King)

        # Place white pawns that will move
        self.game.board[1][4] = ChessPiece('p', 'w')  # e2 (blocks e2 for King)
        self.game.board[1][5] = ChessPiece('p', 'w')  # f2 (moves to f3)
        self.game.board[1][6] = ChessPiece('p', 'w')  # g2 (moves to g4)
        
        # Place black pieces for checkmate
        self.game.board[6][4] = ChessPiece('p', 'b')  # e7
        self.game.board[6][3] = ChessPiece('p', 'b')  # d7
        self.game.board[7][3] = ChessPiece('q', 'b')  # Black queen at d8
        
        # Make moves to reach checkmate
        # White moves f3
        move_data = {'from_row': 1, 'from_col': 5, 'to_row': 2, 'to_col': 5, 'piece': 'p', 'player': 'w'}
        state = self.make_move('w', move_data)
        
        # Black moves e5
        self.game.current_player = 'b'
        move_data = {'from_row': 6, 'from_col': 4, 'to_row': 4, 'to_col': 4, 'piece': 'p', 'player': 'b'}
        state = self.make_move('b', move_data)
        
        # White moves g4
        self.game.current_player = 'w'
        move_data = {'from_row': 1, 'from_col': 6, 'to_row': 3, 'to_col': 6, 'piece': 'p', 'player': 'w'}
        state = self.make_move('w', move_data)
        
        # Black delivers checkmate Qh4#
        self.game.current_player = 'b'
        move_data = {'from_row': 7, 'from_col': 3, 'to_row': 3, 'to_col': 7, 'piece': 'q', 'player': 'b'}
        state = self.make_move('b', move_data)
        
        # The game should be over with black as the winner
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'b')
        self.assertTrue(state['in_check'])
        
        # Verify no valid moves for white
        with self.assertRaises(ValueError):
            self.make_move('w', {'from': (0, 4), 'to': (0, 3), 'piece': 'k'})
    
    def test_draw_condition(self):
        """Test draw by insufficient material and 50-move rule."""
        # Set up a position with only kings and bishops on the same color
        self.game.board = [[None] * 8 for _ in range(8)]
        self.game.current_player = 'w'
        
        # Place kings
        self.game.board[0][4] = ChessPiece('k', 'w')  # White king at e1
        self.game.board[7][4] = ChessPiece('k', 'b')  # Black king at e8
        
        # Place bishops on the same color (insufficient material to checkmate)
        self.game.board[0][0] = ChessPiece('b', 'w')  # White bishop at a1 (dark square)
        self.game.board[7][7] = ChessPiece('b', 'b')  # Black bishop at h8 (dark square)
        
        # Make 50 moves without a pawn move or capture to trigger the 50-move rule
        self.game.halfmove_clock = 50
        
        # Make one more move to trigger the draw
        move_data = {
            'from_row': 0, 'from_col': 0,  # White bishop at a1
            'to_row': 1, 'to_col': 1,     # Move to b2
            'piece': 'b',
            'player': 'w'
        }
        state = self.make_move('w', move_data)
        
        # The game should be a draw due to the 50-move rule
        self.assertTrue(state['game_over'])
        self.assertIsNone(state['winner'])  # Draw
        
    def test_castling(self):
        """Test castling move."""
        # Clear the board
        self.game.board = [[None] * 8 for _ in range(8)]
        self.game.current_player = 'w'
        
        # Place kings and rooks for castling
        self.game.board[0][4] = ChessPiece('k', 'w')  # White king at e1
        self.game.board[0][0] = ChessPiece('r', 'w')  # White rook at a1
        self.game.board[0][7] = ChessPiece('r', 'w')  # White rook at h1
        self.game.board[7][4] = ChessPiece('k', 'b')  # Black king at e8
        
        # Perform kingside castling
        move_data = {
            'from_row': 0, 'from_col': 4,  # White king at e1
            'to_row': 0, 'to_col': 6,     # Kingside castle (g1)
            'piece': 'k',
            'player': 'w',
            'castling': True
        }
        state = self.make_move('w', move_data)
        
        # Verify castling
        self.assertIsNone(state['board'][0][4])  # King moved from e1
        self.assertIsNone(state['board'][0][7])  # Rook moved from h1
        self.assertEqual(state['board'][0][6]['type'], 'k')  # King at g1
        self.assertEqual(state['board'][0][5]['type'], 'r')  # Rook at f1moved
        
    def test_en_passant(self):
        """Test en passant capture."""
        # Set up board for en passant
        self.game.board = [[None] * 8 for _ in range(8)]
        self.game.current_player = 'w'
        
        # Place pawns for en passant
        self.game.board[3][4] = ChessPiece('p', 'w')  # White pawn at e5
        self.game.board[3][3] = ChessPiece('p', 'b')  # Black pawn at d5 (just moved two squares)
        
        # Set up the en passant target (the square the black pawn passed through)
        self.game.en_passant_target = (2, 3)  # d6 (the square the black pawn passed through)
        
        # Perform en passant capture
        move_data = {
            'from_row': 3, 'from_col': 4,  # White pawn at e5
            'to_row': 2, 'to_col': 3,     # Captures black pawn en passant by moving to d6
            'piece': 'p',
            'player': 'w',
            'en_passant': True
        }
        state = self.make_move('w', move_data)
        
        # Verify en passant capture
        self.assertIsNone(state['board'][3][3])  # Black pawn should be captured
        self.assertIsNone(state['board'][3][4])  # White pawn should have moved from e5
        self.assertEqual(state['board'][2][3]['type'], 'p')  # White pawn should be at d6
        self.assertEqual(state['board'][2][3]['color'], 'w')  # It should still be a white pawn
