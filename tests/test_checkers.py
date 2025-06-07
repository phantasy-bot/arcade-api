"""
Tests for Checkers game.
"""
import unittest
import numpy as np
from games.checkers.checkers import CheckersGame, CheckersPiece
from .base_test import BaseGameTest, GameMove

class TestCheckersGame(BaseGameTest):
    """Test cases for Checkers game."""
    
    GAME_CLASS = CheckersGame

    def assert_piece_at(self, board, row, col, expected_piece_val):
        """Helper to assert a specific piece is at a board location."""
        actual_piece = board[row][col]
        if expected_piece_val is None:
            self.assertIsNone(actual_piece, f"Expected no piece at ({row},{col}), found {actual_piece}")
        elif isinstance(expected_piece_val, CheckersPiece):
            # In game logic, board stores integer values. In get_game_state, it's string representations.
            # This test suite primarily interacts with get_game_state output.
            if actual_piece == expected_piece_val.value: # Comparing int to int (raw board value)
                return
            # Map enum to string representation for comparison with get_game_state output
            expected_str = None
            if expected_piece_val == CheckersPiece.BLACK:
                expected_str = 'B'
            elif expected_piece_val == CheckersPiece.WHITE:
                expected_str = 'W'
            elif expected_piece_val == CheckersPiece.BLACK_KING:
                expected_str = 'B_KING'
            elif expected_piece_val == CheckersPiece.WHITE_KING:
                expected_str = 'W_KING'
            self.assertEqual(actual_piece, expected_str, f"Expected {expected_str} at ({row},{col}), found {actual_piece}")
        else: # Comparing string to string (get_game_state output)
            self.assertEqual(actual_piece, expected_piece_val, f"Expected {expected_piece_val} at ({row},{col}), found {actual_piece}")

    def test_initial_state(self):
        """Test the initial game state."""
        state = self.game.get_game_state()
        
        # Check basic game state structure
        self.assertValidGameState(state) # From BaseGameTest
        self.assertIn('board', state)
        self.assertIn('current_player', state)
        self.assertIn('game_over', state)
        self.assertIn('winner', state)
        self.assertIn('must_capture', state)
        self.assertIn('selected_piece', state)
        
        # Check initial board dimensions (8x8 for standard checkers)
        self.assertEqual(len(state['board']), self.game.board_size)
        for r in range(self.game.board_size):
            self.assertEqual(len(state['board'][r]), self.game.board_size, f"Row {r} has incorrect length.")
        
        # Check initial player (Black typically starts)
        self.assertEqual(state['current_player'], 'B') # 'B' for Black
        self.assertFalse(state['game_over'])
        self.assertIsNone(state['winner'])
        self.assertFalse(state['must_capture'])
        self.assertIsNone(state['selected_piece'])

        # Verify initial piece setup based on CheckersGame.INITIAL_BOARD_SETUP_STRING
        # Assuming (0,0) is top-left. Black pieces at the 'top' (lower indices for standard array representation).
        # White pieces at the 'bottom' (higher indices).
        # Dark squares are (row + col) % 2 != 0 for traditional boards, or == 0 if (0,0) is dark.
        # The game logic uses (row + col) % 2 == 0 for playable squares if (0,0) is considered dark.
        # Let's check a few key positions based on standard setup.
        # Black pieces rows 0, 1, 2. White pieces rows 5, 6, 7.
        
        # Black pieces
        for r in range(3):
            for c in range(self.game.board_size):
                if (r + c) % 2 != 0: # Playable dark square
                    self.assert_piece_at(state['board'], r, c, 'B')
                else: # Light square, should be empty
                    self.assert_piece_at(state['board'], r, c, None)
        
        # Empty middle rows
        for r in range(3, 5):
            for c in range(self.game.board_size):
                self.assert_piece_at(state['board'], r, c, None)
                
        # White pieces
        for r in range(5, self.game.board_size):
            for c in range(self.game.board_size):
                if (r + c) % 2 != 0: # Playable dark square
                    self.assert_piece_at(state['board'], r, c, 'W')
                else: # Light square, should be empty
                    self.assert_piece_at(state['board'], r, c, None)

    def test_valid_simple_move(self):
        """Test a valid simple (non-capture) move for Black and White."""
        # Black's first move
        initial_state = self.game.get_game_state()
        self.assertEqual(initial_state['current_player'], 'B')

        # Black moves from (2,1) to (3,0)
        move_data_black = {'move': {'from': (2, 1), 'to': (3, 0)}}
        state_after_black_move = self.make_move('B', move_data_black)
        
        self.assert_piece_at(state_after_black_move['board'], 2, 1, None)
        self.assert_piece_at(state_after_black_move['board'], 3, 0, 'B')
        self.assertEqual(state_after_black_move['current_player'], 'W')
        self.assertFalse(state_after_black_move['game_over'])

        # White's turn, respond to Black's move
        move_data_white = {'move': {'from': (5, 0), 'to': (4, 1)}}
        state_after_white_move = self.make_move('W', move_data_white) # Allow ValueError to propagate

        self.assert_piece_at(state_after_white_move['board'], 5, 0, None)
        self.assert_piece_at(state_after_white_move['board'], 4, 1, 'W')
        self.assertEqual(state_after_white_move['current_player'], 'B')
        self.assertFalse(state_after_white_move['game_over'])

    def test_invalid_move_occupied_square(self):
        """Test attempting to move to an already occupied square."""
        # Black moves from (2,1) to (3,0)
        self.make_move('B', {'move': {'from': (2, 1), 'to': (3, 0)}})
        # White moves from (5,0) to (4,1) - a valid response
        self.make_move('W', {'move': {'from': (5, 0), 'to': (4, 1)}})
        
        # Now it's Black's turn. Square (3,0) is occupied by a Black piece.
        # Attempt to move another Black piece from (2,3) to (3,0) - should fail.
        # First, ensure (2,3) has a black piece and (3,0) is a valid target square if empty.
        # (2,3) -> (3,2) or (2,3) -> (3,4)
        # Let's try to move Black piece from (2,3) to (4,1) which is occupied by White.
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.make_move('B', {'move': {'from': (2, 3), 'to': (4, 1)}})

        # Also try to move a Black piece to a square occupied by another Black piece
        # Black at (2,3) tries to move to (3,2). First move Black (2,1) to (3,2)
        # For this scenario, we need a fresh game instance, which setUp provides for each test.
        # However, to test this specific sequence within one test method, we'll manually re-initialize.
        # This is less ideal than separate tests but demonstrates the logic.
        self.game = self.GAME_CLASS(game_id=f"test_game_{id(self)}_reset") # Re-initialize for this specific scenario
        self.game.initialize_game()
        self.make_move('B', {'move': {'from': (2, 1), 'to': (3, 2)}})
        # White makes a non-interfering move
        self.make_move('W', {'move': {'from': (5, 0), 'to': (4, 1)}})
        # Black at (2,3) attempts to move to (3,2) which is occupied by another Black piece
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.make_move('B', {'move': {'from': (2, 3), 'to': (3, 2)}})

    def test_invalid_move_wrong_player(self):
        """Test attempting to move a piece when it's not that player's turn."""
        initial_state = self.game.get_game_state()
        self.assertEqual(initial_state['current_player'], 'B', "Initial player should be Black.")

        # Attempt to move a White piece when it's Black's turn
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.make_move('W', {'move': {'from': (5, 0), 'to': (4, 1)}})

        # Black makes a valid move
        self.make_move('B', {'move': {'from': (2, 1), 'to': (3, 0)}})
        state_after_black_move = self.game.get_game_state()
        self.assertEqual(state_after_black_move['current_player'], 'W', "Player should be White after Black's move.")

        # Attempt to move a Black piece when it's White's turn
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.make_move('B', {'move': {'from': (3, 0), 'to': (4, 1)}})

    def test_simple_capture_move(self):
        """Test a simple capture move by a Black piece."""
        # Custom board setup for a capture scenario
        # B . B . B . B .
        # . B . B . B . B
        # B . _ . _ . _ .
        # . _ . W . _ . _
        # _ . _ . _ . _ .
        # . W . W . W . W
        # W . W . W . W .
        # . W . W . W . W
        # Black at (2,1) wants to capture White at (3,2) and land on (4,3)
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[2, 1] = CheckersPiece.BLACK.value
        self.game.board[3, 2] = CheckersPiece.WHITE.value
        self.game.current_player = CheckersPiece.BLACK # Ensure it's Black's turn

        # Print board for debugging before move
        # print("\nBoard before capture:")
        # print(self.game.board)

        move_data_capture = {'move': {'from': (2, 1), 'to': (4, 3)}}
        state_after_capture = self.make_move('B', move_data_capture)

        # Print board for debugging after move
        # print("\nBoard after capture:")
        # print(self.game.board)

        # Assertions
        self.assert_piece_at(state_after_capture['board'], 2, 1, None)      # Original position is empty
        self.assert_piece_at(state_after_capture['board'], 3, 2, None)      # Captured piece is removed
        self.assert_piece_at(state_after_capture['board'], 4, 3, 'B')       # Black piece at new position
        self.assertEqual(state_after_capture['current_player'], 'W')
        self.assertFalse(state_after_capture['game_over'])
        # Optionally, check self.game.captured_pieces if implemented and relevant for the test
        # self.assertEqual(self.game.captured_pieces[CheckersPiece.WHITE], 1)

    def test_must_capture_rule(self):
        """Test that a player must make an available capture move."""
        # Custom board setup:
        # Black at (2,1) can capture White at (3,2) to land at (4,3).
        # Black also has a piece at (2,5) that could make a non-capture move to (3,4) or (3,6).
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[2, 1] = CheckersPiece.BLACK.value  # Capturing piece
        self.game.board[3, 2] = CheckersPiece.WHITE.value  # Piece to be captured
        self.game.board[2, 5] = CheckersPiece.BLACK.value  # Piece with non-capture move
        self.game.current_player = CheckersPiece.BLACK

        # Update internal state regarding available captures (sets self.game.must_capture)
        self.game.get_valid_moves()
        self.assertTrue(self.game.must_capture, "Game should register that a capture is mandatory.")

        # Attempt to make a non-capture move with piece at (2,5) to (3,4)
        non_capture_move_data = {'move': {'from': (2, 5), 'to': (3, 4)}}
        with self.assertRaisesRegex(ValueError, "Invalid move"):
            self.make_move('B', non_capture_move_data)

        # Now, make the mandatory capture move with piece at (2,1) to (4,3)
        capture_move_data = {'move': {'from': (2, 1), 'to': (4, 3)}}
        state_after_capture = self.make_move('B', capture_move_data)

        # Assertions for the successful capture
        self.assert_piece_at(state_after_capture['board'], 2, 1, None)      # Original position of capturer is empty
        self.assert_piece_at(state_after_capture['board'], 3, 2, None)      # Captured piece is removed
        self.assert_piece_at(state_after_capture['board'], 4, 3, 'B')       # Capturer at new position
        self.assertEqual(state_after_capture['current_player'], 'W')
        self.assertFalse(state_after_capture['game_over'])

    def test_king_promotion(self):
        """Test that a piece is promoted to a king when it reaches the opponent's back rank."""
        # Test Black piece promotion
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[6, 1] = CheckersPiece.BLACK.value  # Black piece one step from king row
        self.game.current_player = CheckersPiece.BLACK

        move_data_black_to_king = {'move': {'from': (6, 1), 'to': (7, 0)}}
        state_after_black_kinged = self.make_move('B', move_data_black_to_king)

        self.assert_piece_at(state_after_black_kinged['board'], 6, 1, None)
        self.assert_piece_at(state_after_black_kinged['board'], 7, 0, 'B_KING') # Check for Black King
        self.assertEqual(state_after_black_kinged['current_player'], 'W', "Player should switch to White after Black's move.")
        self.assertFalse(state_after_black_kinged['game_over'])

        # Test White piece promotion
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[1, 0] = CheckersPiece.WHITE.value  # White piece one step from king row
        self.game.current_player = CheckersPiece.WHITE

        move_data_white_to_king = {'move': {'from': (1, 0), 'to': (0, 1)}}
        state_after_white_kinged = self.make_move('W', move_data_white_to_king)

        self.assert_piece_at(state_after_white_kinged['board'], 1, 0, None)
        self.assert_piece_at(state_after_white_kinged['board'], 0, 1, 'W_KING') # Check for White King
        self.assertEqual(state_after_white_kinged['current_player'], 'B', "Player should switch to Black after White's move.")
        self.assertFalse(state_after_white_kinged['game_over'])

    def test_king_movement_and_capture(self):
        """Test king's ability to move and capture in all diagonal directions."""
        # 1. King Forward Move
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[3, 3] = CheckersPiece.BLACK_KING.value
        self.game.current_player = CheckersPiece.BLACK

        move_data_fwd = {'move': {'from': (3, 3), 'to': (4, 4)}}
        state_fwd = self.make_move('B', move_data_fwd)
        self.assert_piece_at(state_fwd['board'], 3, 3, None)
        self.assert_piece_at(state_fwd['board'], 4, 4, 'B_KING')
        self.assertEqual(state_fwd['current_player'], 'W')

        # 2. King Backward Move (reset board for clarity)
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[3, 3] = CheckersPiece.BLACK_KING.value
        self.game.current_player = CheckersPiece.BLACK

        move_data_bwd = {'move': {'from': (3, 3), 'to': (2, 2)}}
        state_bwd = self.make_move('B', move_data_bwd)
        self.assert_piece_at(state_bwd['board'], 3, 3, None)
        self.assert_piece_at(state_bwd['board'], 2, 2, 'B_KING')
        self.assertEqual(state_bwd['current_player'], 'W')

        # 3. King Forward Capture
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[3, 3] = CheckersPiece.BLACK_KING.value
        self.game.board[4, 4] = CheckersPiece.WHITE.value # Piece to be captured
        self.game.current_player = CheckersPiece.BLACK
        self.game.get_valid_moves() # Update must_capture state

        move_data_cap_fwd = {'move': {'from': (3, 3), 'to': (5, 5)}}
        state_cap_fwd = self.make_move('B', move_data_cap_fwd)
        self.assert_piece_at(state_cap_fwd['board'], 3, 3, None)
        self.assert_piece_at(state_cap_fwd['board'], 4, 4, None) # Captured piece removed
        self.assert_piece_at(state_cap_fwd['board'], 5, 5, 'B_KING')
        self.assertEqual(state_cap_fwd['current_player'], 'W')

        # 4. King Backward Capture
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[3, 3] = CheckersPiece.BLACK_KING.value
        self.game.board[2, 2] = CheckersPiece.WHITE.value # Piece to be captured
        self.game.current_player = CheckersPiece.BLACK
        self.game.get_valid_moves() # Update must_capture state

        move_data_cap_bwd = {'move': {'from': (3, 3), 'to': (1, 1)}}
        state_cap_bwd = self.make_move('B', move_data_cap_bwd)
        self.assert_piece_at(state_cap_bwd['board'], 3, 3, None)
        self.assert_piece_at(state_cap_bwd['board'], 2, 2, None) # Captured piece removed
        self.assert_piece_at(state_cap_bwd['board'], 1, 1, 'B_KING')
        self.assertEqual(state_cap_bwd['current_player'], 'W')

    def test_multi_jump_capture(self):
        """Test a multi-jump capture scenario."""
        # Setup: Black at (2,1), White at (3,2), White at (5,4)
        # Black jumps (3,2) to (4,3), then jumps (5,4) to (6,5)
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[2, 1] = CheckersPiece.BLACK.value
        self.game.board[3, 2] = CheckersPiece.WHITE.value
        self.game.board[5, 4] = CheckersPiece.WHITE.value # Second piece to be captured
        self.game.current_player = CheckersPiece.BLACK

        # Ensure must_capture is evaluated based on this setup
        self.game.get_valid_moves()
        self.assertTrue(self.game.must_capture, "Game should register an initial mandatory capture.")

        # First capture: (2,1) -> (4,3), capturing (3,2)
        move_data_jump1 = {'move': {'from': (2, 1), 'to': (4, 3)}}
        state_after_jump1 = self.make_move('B', move_data_jump1)

        self.assert_piece_at(state_after_jump1['board'], 2, 1, None)  # Original spot empty
        self.assert_piece_at(state_after_jump1['board'], 3, 2, None)  # First capture removed
        self.assert_piece_at(state_after_jump1['board'], 4, 3, 'B')   # Piece at intermediate spot
        self.assertEqual(state_after_jump1['current_player'], 'B', "Player should still be Black for multi-jump.")
        self.assertTrue(self.game.must_capture, "Must_capture should remain true for multi-jump.")
        self.assertEqual(self.game.selected_piece, (4,3), "Selected piece should be the one that just jumped.")

        # Second capture: (4,3) -> (6,5), capturing (5,4)
        move_data_jump2 = {'move': {'from': (4, 3), 'to': (6, 5)}}
        state_after_jump2 = self.make_move('B', move_data_jump2)

        self.assert_piece_at(state_after_jump2['board'], 4, 3, None)  # Intermediate spot empty
        self.assert_piece_at(state_after_jump2['board'], 5, 4, None)  # Second capture removed
        self.assert_piece_at(state_after_jump2['board'], 6, 5, 'B')   # Piece at final spot
        self.assertEqual(state_after_jump2['current_player'], 'W', "Player should switch to White after multi-jump is complete.")
        # self.game.must_capture will be re-evaluated for White's turn by get_valid_moves if called by White
        # For now, after Black's turn, it might be True or False depending on game logic, but selected_piece should be None.
        self.assertIsNone(self.game.selected_piece, "Selected piece should be None after turn completion.")

    def test_game_over_no_pieces(self):
        """Test game over when a player has no pieces left."""
        # Setup: Black has one piece, White has no pieces.
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[0, 1] = CheckersPiece.BLACK.value
        self.game.current_player = CheckersPiece.BLACK # Irrelevant for this check, but set for consistency

        # Force re-evaluation of game over state by calling is_game_over or get_game_state
        # The game.make_move() usually updates this, but here we set board directly.
        game_is_over = self.game.is_game_over()
        state = self.game.get_game_state()

        self.assertTrue(game_is_over, "Game should be over as White has no pieces.")
        self.assertTrue(state['game_over'], "State should reflect game over.")
        self.assertEqual(state['winner'], 'B', "Black should be the winner.")

        # Setup: White has one piece, Black has no pieces.
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[7, 0] = CheckersPiece.WHITE.value
        self.game.current_player = CheckersPiece.WHITE

        game_is_over_w = self.game.is_game_over()
        state_w = self.game.get_game_state()

        self.assertTrue(game_is_over_w, "Game should be over as Black has no pieces.")
        self.assertTrue(state_w['game_over'], "State should reflect game over.")
        self.assertEqual(state_w['winner'], 'W', "White should be the winner.")

    def test_game_over_no_valid_moves(self):
        """Test game over when a player has pieces but no valid moves."""
        # Setup: Black piece at (6,1) is blocked by White pieces at (7,0) and (7,2).
        # No jumps possible for Black from (6,1) as they would go off-board.
        # No simple moves possible as (7,0) and (7,2) are occupied by opponent.
        # . . . . . . . .
        # . . . . . . . .
        # . . . . . . . .
        # . . . . . . . .
        # . W . . . . . .  (Extra White piece at (5,0) to ensure White has pieces)
        # . . . . . . . .
        # . B . . . . . .  (Black at (6,1))
        # W . W . . . . .  (White at (7,0), White at (7,2))
        self.game.board = np.zeros((8, 8), dtype=int)
        self.game.board[6, 1] = CheckersPiece.BLACK.value
        self.game.board[7, 0] = CheckersPiece.WHITE.value
        self.game.board[7, 2] = CheckersPiece.WHITE.value
        self.game.board[5, 0] = CheckersPiece.WHITE.value # Ensure White has pieces
        self.game.current_player = CheckersPiece.BLACK # It's Black's turn, but Black cannot move.

        # Explicitly update valid moves and must_capture state before checking game_over
        self.game.get_valid_moves()

        # is_game_over checks for current player's valid moves.
        game_is_over = self.game.is_game_over()
        state = self.game.get_game_state()

        self.assertTrue(game_is_over, "Game should be over as Black has no valid moves.")
        self.assertTrue(state['game_over'], "State should reflect game over.")
        self.assertEqual(state['winner'], 'W', "White should be the winner as Black cannot move.")

    # More tests will be added here for moves, captures, kinging, game over, etc.
