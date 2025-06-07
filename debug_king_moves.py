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

def test_king_moves():
    # Create a game instance
    game = CheckersGame("test")
    
    # Set up a board with a white king
    board = np.zeros((8, 8), dtype=int)
    board[0, 0] = CheckersPiece.WHITE_KING.value  # White king at (0,0)
    
    print("=== Initial Board ===")
    print_board(board)
    
    # Set the board and current player
    game._set_board(board)
    game.current_player = CheckersPiece.WHITE
    
    print("\n=== After _set_board ===")
    print_board(game.board)
    
    # Check the piece type and possible moves
    print(f"\nPiece at (0,0): {game.board[0,0]}")
    print("Getting valid moves for current player:")
    valid_moves = game.get_valid_moves()
    print(f"Valid moves: {valid_moves}")
    
    # Check if the king can move to (1,1)
    move = {"move": {"from": (0, 0), "to": (1, 1)}}
    print("\n=== Validating move ===")
    is_valid = game.validate_move(move)
    print(f"Is move valid? {is_valid}")
    
    if is_valid:
        print("\n=== Making move ===")
        game.make_move(move)
        print("\n=== After move ===")
        print_board(game.board)
    
    return is_valid

if __name__ == '__main__':
    result = test_king_moves()
    print(f"\nTest result: {'PASSED' if result else 'FAILED'}")
