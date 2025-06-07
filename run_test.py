import sys
import numpy as np
from games.checkers.checkers import CheckersGame, CheckersPiece

def print_board(board):
    """Print the board with coordinates"""
    print("   " + " ".join(str(i) for i in range(8)))
    for i in range(8):
        row = []
        for j in range(8):
            piece = board[i, j]
            if piece == 0:
                row.append('.')
            elif piece == CheckersPiece.WHITE.value:
                row.append('W')
            elif piece == CheckersPiece.BLACK.value:
                row.append('B')
            elif piece == CheckersPiece.WHITE_KING.value:
                row.append('WK')
            elif piece == CheckersPiece.BLACK_KING.value:
                row.append('BK')
            else:
                row.append(str(piece))
        print(f"{i}: " + " ".join(row))

def test_simple_move():
    # Create a game instance
    game = CheckersGame("test")
    
    # Set up a simple board
    board = np.zeros((8, 8), dtype=int)
    board[2, 1] = CheckersPiece.WHITE.value  # White piece at (2,1)
    board[5, 0] = CheckersPiece.BLACK.value  # Black piece at (5,0)
    
    print("=== Initial Board ===")
    print_board(board)
    
    # Set the board
    game._set_board(board)
    
    print("\n=== After _set_board ===")
    print_board(game.board)
    
    # Test 1: Try to move white piece (2,1) to (3,0)
    print("\n=== Test 1: Move white piece (2,1) to (3,0) ===")
    game.current_player = CheckersPiece.WHITE
    
    print(f"Current player: {game.current_player}")
    print(f"Piece at (2,1): {game.board[2, 1]}")
    print(f"Piece at (3,0): {game.board[3, 0]}")
    
    # Get possible moves
    print("\nGetting possible moves for (2,1):")
    moves = game._get_possible_moves(2, 1)
    print(f"Possible moves: {moves}")
    
    # Validate the move - change destination to (3,2) which is a dark square
    move = {"move": {"from": (2, 1), "to": (3, 2)}}
    is_valid = game.validate_move(move)
    print(f"Is move valid? {is_valid}")
    
    if not is_valid:
        print("\n=== Debug Info ===")
        print(f"Current player: {game.current_player}")
        print(f"Piece at (2,1): {game.board[2, 1]}")
        print(f"Piece type: {'WHITE' if game.board[2, 1] == CheckersPiece.WHITE.value else 'BLACK'}")
        print(f"Is white turn: {game.current_player == CheckersPiece.WHITE}")
        
        # Check if the destination is a valid position
        print("\nChecking position (3,2):")
        print(f"Is valid position: {game._is_valid_position(3, 2)}")
        print(f"Is empty: {game.board[3, 2] == 0}")
    
    return is_valid

if __name__ == '__main__':
    result = test_simple_move()
    print(f"\nTest result: {'PASSED' if result else 'FAILED'}")
