"""
Test template for Shogi game.
"""
import unittest
from games.shogi import ShogiGame, ShogiPiece
from tests.base_test import BaseGameTest


class TestShogiGame(BaseGameTest):
    """Test cases for Shogi game."""
    
    GAME_CLASS = ShogiGame
    
    def test_initial_state(self):
        """Test the initial game state."""
        state = self.game.get_game_state()
        self.assertValidGameState(state)
        
        # Add game-specific assertions here
        # Example:
        # self.assertEqual(state['current_player'], 'player1')
        # self.assertIsNone(state['winner'])
    
    def test_valid_moves(self):
        """Test valid moves."""
        # Initial state: white's turn
        self.assertEqual(self.game.current_player, "w")

        # 1. White pawn moves one step forward (6,0) -> (5,0)
        move_pawn_fwd = {"from_row": 6, "from_col": 0, "to_row": 5, "to_col": 0}
        state = self.game.make_move(move_pawn_fwd)
        self.assertValidGameState(state)
        self.assertIsNotNone(state['board'][5][0])
        self.assertEqual(state['board'][5][0]['type'], 'p')
        self.assertEqual(state['board'][5][0]['color'], 'w')
        self.assertIsNone(state['board'][6][0])
        self.assertEqual(state['current_player'], "b")

        # 2. Black pawn moves one step forward (2,0) -> (3,0)
        self.game.current_player = "b" # Set turn for testing
        move_black_pawn_fwd = {"from_row": 2, "from_col": 0, "to_row": 3, "to_col": 0}
        state = self.game.make_move(move_black_pawn_fwd)
        self.assertValidGameState(state)
        self.assertEqual(state['current_player'], "w")

        # 3. White pawn captures black piece (e.g. lance at (0,0) by white pawn at (1,0))
        # Setup: Place a black lance at (0,0) and white pawn at (1,0)
        self.game.initialize_game() # Reset to initial board
        self.game.board[0][0] = ShogiPiece("l", "b")
        self.game.board[1][0] = ShogiPiece("p", "w")
        self.game.board[6] = [None] * self.game.FILES # Clear white pawns for this test
        self.game.current_player = "w"
        
        capture_move = {"from_row": 1, "from_col": 0, "to_row": 0, "to_col": 0}
        state = self.game.make_move(capture_move)
        self.assertValidGameState(state)
        self.assertEqual(state['board'][0][0]['type'], 'p')
        self.assertEqual(state['board'][0][0]['color'], 'w')
        self.assertTrue(state['board'][0][0]['promoted']) # Pawn promotes on entering last rank
        self.assertIn('l', state['hands']['w']) # White captured a lance
        self.assertEqual(state['hands']['w'].count('l'), 1) # Check count of 'l' in hand

        # 4. Test promotion: White pawn moves from (1,1) to (0,1) (promotion zone for white)
        self.game.initialize_game()
        self.game.board[1][1] = ShogiPiece("p", "w")
        self.game.current_player = "w"
        promote_move = {"from_row": 1, "from_col": 1, "to_row": 0, "to_col": 1, "promoted": True}
        state = self.game.make_move(promote_move)
        self.assertValidGameState(state)
        self.assertTrue(state['board'][0][1]['promoted'])
        self.assertEqual(state['board'][0][1]['type'], 'p') # type remains 'p', promoted status changes

        # 5. Test valid drop: White drops a captured pawn
        self.game.initialize_game()
        self.game.board[6][4] = None # Remove white pawn from (6,4) to avoid Nifu in column 4
        self.game.hands['w'].append('p') # Give white a pawn in hand
        self.game.current_player = "w"
        drop_move = {"to_row": 4, "to_col": 4, "piece_type": "p", "is_drop": True}
        state = self.game.make_move(drop_move)
        self.assertValidGameState(state)
        self.assertEqual(state['board'][4][4]['type'], 'p')
        self.assertEqual(state['board'][4][4]['color'], 'w')
        self.assertNotIn('p', state['hands']['w']) # Check 'p' is no longer in hand
    
    def test_invalid_moves(self):
        """Test invalid moves."""
        # 1. White pawn moves backward (6,0) -> (7,0)
        self.game.initialize_game()
        self.game.current_player = "w"
        invalid_pawn_move_bw = {"from_row": 6, "from_col": 0, "to_row": 7, "to_col": 0}
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.game.make_move(invalid_pawn_move_bw)

        # 2. Moving opponent's piece (white tries to move black pawn at (2,0))
        self.game.initialize_game()
        self.game.current_player = "w"
        move_opponent_piece = {"from_row": 2, "from_col": 0, "to_row": 3, "to_col": 0}
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.game.make_move(move_opponent_piece)

        # 3. Nifu (two pawns in the same file for white)
        self.game.initialize_game()
        self.game.hands['w'].append('p') # White has a pawn in hand
        self.game.board[5][0] = ShogiPiece("p", "w") # White already has a pawn in file 0
        self.game.current_player = "w"
        nifu_drop_move = {"to_row": 4, "to_col": 0, "piece_type": "p", "is_drop": True}
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.game.make_move(nifu_drop_move)
        
        # 4. Pawn drop for checkmate (Uchi-fu-dzume - illegal in Shogi)
        # This is complex to set up. For now, we'll test a simpler illegal drop.
        # Test dropping a piece on an_occupied square
        self.game.initialize_game()
        self.game.hands['w'].append('p')
        self.game.board[4][4] = ShogiPiece("r", "b") # Occupied by black rook
        self.game.current_player = "w"
        drop_on_occupied = {"to_row": 4, "to_col": 4, "piece_type": "p", "is_drop": True}
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.game.make_move(drop_on_occupied)

        # 5. Move into check (White king at (8,4), Black rook at (0,4), White moves pawn from (6,0) to (5,0) exposing king)
        # This requires _is_in_check to be robust. Let's simplify: king moves into attack path of a rook.
        self.game.initialize_game()
        self.game.board[8][4] = ShogiPiece("k", "w") # White King
        self.game.board[0][3] = ShogiPiece("r", "b") # Black Rook
        # Clear other pieces for simplicity
        for r in range(self.game.RANKS):
            for c in range(self.game.FILES):
                if not ((r == 8 and c == 4) or (r == 0 and c == 3)):
                    self.game.board[r][c] = None
        self.game.current_player = "w"
        move_king_into_check = {"from_row": 8, "from_col": 4, "to_row": 8, "to_col": 3}
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.game.make_move(move_king_into_check)
    
    def test_game_flow(self):
        """Test a game flow leading to a draw by repetition (Sennichite)."""
        self.game.initialize_game()

        moves = [
        # White Rook at (7,7), Black Rook at (1,1)
        # Cycle 1
        {"from_row": 7, "from_col": 7, "to_row": 7, "to_col": 6},  # 1. W: R (7,7) -> (7,6)
        {"from_row": 1, "from_col": 1, "to_row": 1, "to_col": 2},  # 2. B: R (1,1) -> (1,2)
        {"from_row": 7, "from_col": 6, "to_row": 7, "to_col": 7},  # 3. W: R (7,6) -> (7,7)
        {"from_row": 1, "from_col": 2, "to_row": 1, "to_col": 1},  # 4. B: R (1,2) -> (1,1) (Pos1 repeated for W)
        # Cycle 2
        {"from_row": 7, "from_col": 7, "to_row": 7, "to_col": 6},  # 5. W: R (7,7) -> (7,6)
        {"from_row": 1, "from_col": 1, "to_row": 1, "to_col": 2},  # 6. B: R (1,1) -> (1,2)
        {"from_row": 7, "from_col": 6, "to_row": 7, "to_col": 7},  # 7. W: R (7,6) -> (7,7)
        {"from_row": 1, "from_col": 2, "to_row": 1, "to_col": 1},  # 8. B: R (1,2) -> (1,1) (Pos1 repeated for W)
        # Cycle 3
        {"from_row": 7, "from_col": 7, "to_row": 7, "to_col": 6},  # 9. W: R (7,7) -> (7,6)
        {"from_row": 1, "from_col": 1, "to_row": 1, "to_col": 2},  # 10. B: R (1,1) -> (1,2)
        {"from_row": 7, "from_col": 6, "to_row": 7, "to_col": 7},  # 11. W: R (7,6) -> (7,7)
        {"from_row": 1, "from_col": 2, "to_row": 1, "to_col": 1},  # 12. B: R (1,2) -> (1,1) (Pos1 repeated for W - Draw)
    ]

        for i, move_data in enumerate(moves):
            state = self.game.make_move(move_data)
            if state.get("game_over"):
                self.assertEqual(state.get("winner"), "draw", f"Game ended on move {i+1} but not by draw, or wrong winner.")
                self.assertEqual(i, 11, f"Draw declared on move {i+1}, expected move 12 (index 11)") # Draw after 12th move
                return # Test passed

        self.fail("Game did not end in a draw by repetition as expected after 12 moves.")
    
    def test_win_condition(self):
        """Test win conditions."""
        # Add test cases for win conditions
        pass
    
    def test_draw_condition(self):
        """Test draw conditions."""
        # Add test cases for draw conditions if applicable
        pass
