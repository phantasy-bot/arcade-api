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

def test_king_promotion():
    # Create a game instance
    game = CheckersGame("test")
    
    # Set up a board with a white piece one move from promotion
    board = np.zeros((8, 8), dtype=int)
    board[1, 1] = CheckersPiece.WHITE.value  # White piece at (1,1)
    
    print("=== Initial Board ===")
    print_board(board)
    
    # Set the board and current player
    game._set_board(board)
    game.current_player = CheckersPiece.WHITE
    
    print("\n=== After _set_board ===")
    print_board(game.board)
    
    # Check the piece type and possible moves
    print(f"\nPiece at (1,1): {game.board[1,1]}")
    print("Getting possible moves for (1,1):")
    moves = game._get_possible_moves(1, 1)
    print(f"Possible moves: {moves}")
    
    # Try to make the promotion move
    move = {"move": {"from": (1, 1), "to": (0, 0)}}
    print("\n=== Validating move ===")
    is_valid = game.validate_move(move)
    print(f"Is move valid? {is_valid}")
    
    if is_valid:
        print("\n=== Making move ===")
        game.make_move(move)
        print("\n=== After move ===")
        print_board(game.board)
        print(f"Piece at (0,0): {game.board[0,0]}")
        print(f"Is king? {game.board[0,0] == CheckersPiece.WHITE_KING.value}")
    
    return is_valid

if __name__ == '__main__':
    result = test_king_promotion()
    print(f"\nTest result: {'PASSED' if result else 'FAILED'}")
