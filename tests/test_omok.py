"""
Test cases for Omok (Gomoku) game.
"""
import unittest
from games.omok import OmokGame
from tests.base_test import BaseGameTest


class TestOmokGame(BaseGameTest):
    """Test cases for Omok game."""
    
    GAME_CLASS = OmokGame
    
    def test_initial_state(self):
        """Test the initial game state."""
        state = self.game.get_game_state()
        
        # Check basic game state
        self.assertValidGameState(state)
        self.assertEqual(state['current_player'], 'B')  # Black starts first
        self.assertIsNone(state['winner'])
        self.assertFalse(state['game_over'])
        
        # Check board size (15x15)
        self.assertEqual(len(state['board']), 15)
        self.assertEqual(len(state['board'][0]), 15)
        
        # Check board is empty
        for row in state['board']:
            self.assertTrue(all(cell is None for cell in row))
    
    def test_valid_moves(self):
        """Test making valid moves."""
        # First move by Black
        state = self.make_move('B', {'row': 7, 'col': 7})
        self.assertValidGameState(state)
        self.assertEqual(state['board'][7][7], 'B')
        self.assertEqual(state['current_player'], 'W')  # Should switch to White
        
        # Second move by White
        state = self.make_move('W', {'row': 7, 'col': 8})
        self.assertValidGameState(state)
        self.assertEqual(state['board'][7][8], 'W')
        self.assertEqual(state['current_player'], 'B')  # Back to Black
    
    def test_invalid_moves(self):
        """Test making invalid moves."""
        # Test 1: Out of bounds (negative row)
        try:
            self.make_move('B', {'row': -1, 'col': 0})
            self.fail("Expected ValueError for out of bounds row")
        except ValueError as e:
            print(f"Test 1: Got expected error: {e}")
            self.assertIn("out of bounds", str(e).lower())
        
        # Test 2: Out of bounds (row too large)
        try:
            self.make_move('B', {'row': 15, 'col': 0})
            self.fail("Expected ValueError for out of bounds row")
        except ValueError as e:
            print(f"Test 2: Got expected error: {e}")
            self.assertIn("out of bounds", str(e).lower())
        
        # Test 3: Out of bounds (negative column)
        try:
            self.make_move('B', {'row': 0, 'col': -1})
            self.fail("Expected ValueError for out of bounds column")
        except ValueError as e:
            print(f"Test 3: Got expected error: {e}")
            self.assertIn("out of bounds", str(e).lower())
        
        # Test 4: Out of bounds (column too large)
        try:
            self.make_move('B', {'row': 0, 'col': 15})
            self.fail("Expected ValueError for out of bounds column")
        except ValueError as e:
            print(f"Test 4: Got expected error: {e}")
            self.assertIn("out of bounds", str(e).lower())
        
        # Test 5: Occupied position
        print("\nTest 5: Making initial valid move")
        state = self.make_move('B', {'row': 0, 'col': 0})
        print(f"Board after move: {state['board'][0][0]}")
        
        print("Test 5: Attempting to make move on occupied position")
        try:
            self.make_move('W', {'row': 0, 'col': 0})  # Same position
            self.fail("Expected ValueError for occupied position")
        except ValueError as e:
            print(f"Test 5: Got expected error: {e}")
            self.assertIn("already taken", str(e).lower())
        
        # Test 6: Wrong player
        print("\nTest 6: Attempting to play out of turn")
        # First, make a move with the correct player (W)
        self.make_move('W', {'row': 1, 'col': 1})
        
        # Now try to make another move with W (should be B's turn)
        try:
            self.make_move('W', {'row': 1, 'col': 2})  # Should be B's turn
            self.fail("Expected ValueError for wrong player turn")
        except ValueError as e:
            print(f"Test 6: Got expected error: {e}")
            self.assertIn("turn", str(e).lower())
    
    def test_horizontal_win(self):
        """Test horizontal win condition."""
        # Set up a horizontal win for Black
        moves = [
            (0, 0), (1, 0),  # B, W
            (0, 1), (1, 1),  # B, W
            (0, 2), (1, 2),  # B, W
            (0, 3), (1, 3),  # B, W
            (0, 4),          # B - wins
        ]
        
        for i, (row, col) in enumerate(moves):
            player = 'B' if i % 2 == 0 else 'W'
            state = self.make_move(player, {'row': row, 'col': col})
            
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'B')
    
    def test_vertical_win(self):
        """Test vertical win condition."""
        # Set up a vertical win for White
        moves = [
            (0, 0), (0, 1),  # B, W
            (1, 0), (1, 1),  # B, W
            (2, 0), (2, 1),  # B, W
            (3, 0), (3, 1),  # B, W
            (5, 5), (4, 1),  # B, W - wins
        ]
        
        for i, (row, col) in enumerate(moves):
            player = 'B' if i % 2 == 0 else 'W'
            state = self.make_move(player, {'row': row, 'col': col})
            
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'W')
    
    def test_diagonal_win(self):
        """Test diagonal win condition."""
        # Set up a diagonal win for Black
        moves = [
            (0, 0), (1, 0),  # B, W
            (1, 1), (2, 0),  # B, W
            (2, 2), (3, 0),  # B, W
            (3, 3), (4, 0),  # B, W
            (4, 4),          # B - wins diagonally
        ]
        
        for i, (row, col) in enumerate(moves):
            player = 'B' if i % 2 == 0 else 'W'
            state = self.make_move(player, {'row': row, 'col': col})
            
        self.assertTrue(state['game_over'])
        self.assertEqual(state['winner'], 'B')
    
    def test_win_priority(self):
        """Test that the first player to get 5 in a row wins, even if moves remain."""
        # Create a test game with a smaller board for testing
        class TestOmok(OmokGame):
            BOARD_SIZE = 10
            WIN_LENGTH = 5
            
        game = TestOmok(game_id="test_win_priority")
        
        # Make moves where Black gets 5 in a row first
        # Black will win on move (0,4)
        moves = [
            # Black's winning line (horizontal)
            (0, 0),  # B
            (1, 0),  # W
            (0, 1),  # B
            (1, 1),  # W
            (0, 2),  # B
            (1, 2),  # W
            (0, 3),  # B
            (1, 3),  # W
            (0, 4),  # B - wins here
            # These moves should not be possible
            (1, 4),  # W - would win if game continued
            (0, 5),  # B
            (1, 5),  # W
        ]
        
        # Make the moves and track game state
        game_over = False
        winner = None
        
        for i, (row, col) in enumerate(moves):
            if game_over:
                # Should not be able to make more moves after game is over
                with self.assertRaises(ValueError) as cm:
                    game.make_move({'row': row, 'col': col, 'player': game.current_player})
                self.assertIn("game is already over", str(cm.exception).lower())
                break
                
            player = game.current_player
            state = game.make_move({'row': row, 'col': col, 'player': player})
            
            # Check if game is over after this move
            if state['game_over']:
                game_over = True
                winner = state['winner']
                # Should be Black's win on the 5th move
                self.assertEqual(winner, 'B')
        
        # Verify the game is marked as over
        self.assertTrue(game_over)
        self.assertEqual(winner, 'B')
    
    def test_draw_condition(self):
        """Test draw condition when board is full with no winner."""
        # Create a small 3x3 board for testing draw condition
        class TestOmok(OmokGame):
            BOARD_SIZE = 3
            
        game = TestOmok(game_id="test_draw")
        
        # Fill the board with no winner
        # B W B
        # W B W
        # W B W  (last move by B)
        moves = [
            (0, 0), (0, 1),  # B, W
            (0, 2), (1, 0),  # B, W
            (1, 1), (1, 2),  # B, W
            (2, 0), (2, 1),  # W, B
            (2, 2),           # B - last move, board is full with no winner
        ]
        
        for i, (row, col) in enumerate(moves):
            player = 'B' if i % 2 == 0 else 'W'
            state = game.make_move({'row': row, 'col': col, 'player': player})
            
            # Only check the final state
            if i == len(moves) - 1:
                self.assertTrue(state['game_over'])
                self.assertEqual(state['winner'], 'draw')
