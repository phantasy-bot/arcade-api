from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, cast
import numpy as np
from enum import Enum
import time
import json


class CheckersPiece(Enum):
    EMPTY = 0
    BLACK = 1
    BLACK_KING = 2
    WHITE = 3
    WHITE_KING = 4


class CheckersGame(AbstractGame):
    def __init__(self, game_id: str, board_size: int = 8):
        super().__init__(game_id)
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = CheckersPiece.BLACK
        self.selected_piece = None
        self.must_capture = False
        self.captured_pieces = {CheckersPiece.BLACK: 0, CheckersPiece.WHITE: 0}
        self._init_game()

    def _set_board(self, board):
        """Set the board to a custom state (for testing)"""
        for row in board:
            pass
        
        self.board = board.copy()
        
        for row in self.board:
            pass
        
    def _init_game(self):
        """Initialize a new game"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = CheckersPiece.BLACK
        self.selected_piece = None
        self.must_capture = False
        self.captured_pieces = {CheckersPiece.BLACK: 0, CheckersPiece.WHITE: 0}
        self.game_over = False
        self.winner = None

        # Place initial pieces
        # Standard Checkers: Black at top (rows 0,1,2), White at bottom (rows 5,6,7 for 8x8)
        # Pieces are on dark squares. If (0,0) is a light square, then (row + col) % 2 != 0 are dark squares.
        for row in range(self.board_size):
            for col in range(self.board_size):
                if (row + col) % 2 != 0:  # Playable dark squares
                    if row < 3: # Top rows for Black pieces
                        self.board[row, col] = CheckersPiece.BLACK.value
                    elif row >= self.board_size - 3: # Bottom rows for White pieces (e.g., rows 5, 6, 7 on 8x8)
                        self.board[row, col] = CheckersPiece.WHITE.value

    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is on board and on a dark square
        
        In checkers, pieces are placed on dark squares. Assuming (0,0) is a light square,
    dark squares are where (x + y) is odd (i.e., (x + y) % 2 != 0).
    For example:
    - (0,1), (0,3), (1,0), (1,2) are dark squares
    - (0,0), (0,2), (1,1), (1,3) are light squares
    """
        is_on_board = 0 <= x < self.board_size and 0 <= y < self.board_size
        is_dark_square = (x + y) % 2 != 0  # Dark squares are where (x + y) is odd
        result = is_on_board and is_dark_square
        return result

    def _get_possible_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all possible moves for a piece"""
        piece = self.board[x, y]
        if piece == 0:
            return []
            
        is_king = piece in [CheckersPiece.BLACK_KING.value, CheckersPiece.WHITE_KING.value]
        is_black = piece in [CheckersPiece.BLACK.value, CheckersPiece.BLACK_KING.value]
        moves = []
        capture_moves = []
        
        # Directions: (dx, dy) where dx is row change, dy is column change
        # Determine possible move directions based on piece type and color
        directions = []
        if is_king:
            directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])  # Kings move in all 4 diagonal directions
        elif is_black:  # Black non-king
            directions.extend([(1, -1), (1, 1)])  # Black moves "down" the board (increasing row index)
        else:  # White non-king (not is_black and not is_king)
            directions.extend([(-1, -1), (-1, 1)])  # White moves "up" the board (decreasing row index)
            
        
        # Check for capture moves first (mandatory capture rule)
        capture_moves = []
        for dx, dy in directions:
            # Check for capture move (two squares away)
            nx, ny = x + 2*dx, y + 2*dy
            jumped_x, jumped_y = x + dx, y + dy
            
            
            # Check if the landing position is valid and empty
            if not self._is_valid_position(nx, ny):
                continue
                
            if self.board[nx, ny] != 0:
                continue
                
            # Check if there's a piece to jump over
            if not self._is_valid_position(jumped_x, jumped_y):
                continue
                
            if self.board[jumped_x, jumped_y] == 0:
                continue
                
            # Check if the piece to jump is an opponent's piece
            jumped_piece = self.board[jumped_x, jumped_y]
            # Black pieces are 1 (BLACK) or 2 (BLACK_KING)
            # White pieces are 3 (WHITE) or 4 (WHITE_KING)
            is_black_piece = piece in [CheckersPiece.BLACK.value, CheckersPiece.BLACK_KING.value]
            is_jumped_white = jumped_piece in [CheckersPiece.WHITE.value, CheckersPiece.WHITE_KING.value]
            is_jumped_black = jumped_piece in [CheckersPiece.BLACK.value, CheckersPiece.BLACK_KING.value]
            is_opponent = (is_black_piece and is_jumped_white) or (not is_black_piece and is_jumped_black)
            
            
            if is_opponent:
                capture_moves.append((nx, ny))
        
        # If there are capture moves, return only those (mandatory capture rule)
        if capture_moves:
            return capture_moves
            
        
        # If no capture moves, check regular moves
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Check if the position is valid and empty
            if not self._is_valid_position(nx, ny):
                continue
                
            if self.board[nx, ny] != 0:
                continue
                
            # The directions list now correctly handles forward moves for non-kings,
            # so no additional directional filtering is needed here for regular moves.
                
                
            moves.append((nx, ny))
        
        return moves

    def _get_all_captures(
        self, piece_type: CheckersPiece
    ) -> List[Tuple[int, int, int, int]]:
        """Get all possible capture moves for a player"""
        captures = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x, y] in [
                    piece_type,
                    piece_type + 1,
                ]:  # Check both regular and king pieces
                    moves = self._get_possible_moves(x, y)
                    for nx, ny in moves:
                        if abs(nx - x) == 2:  # Only consider capture moves
                            captures.append((x, y, nx, ny))
        return captures


    def get_valid_moves(self) -> List[Dict[str, Any]]:
        """
        Get all valid moves for the current player.
        If a capture is available, only capture moves are valid.
        """
        player_captures = self._get_all_captures(self.current_player)

        if player_captures:
            self.must_capture = True
            return player_captures

        self.must_capture = False
        regular_moves = []
        for r_idx in range(self.board_size):
            for c_idx in range(self.board_size):
                piece_val = self.board[r_idx, c_idx]
                
                is_current_player_piece = False
                if self.current_player == CheckersPiece.BLACK:
                    if piece_val in [CheckersPiece.BLACK.value, CheckersPiece.BLACK_KING.value]:
                        is_current_player_piece = True
                elif self.current_player == CheckersPiece.WHITE:
                    if piece_val in [CheckersPiece.WHITE.value, CheckersPiece.WHITE_KING.value]:
                        is_current_player_piece = True
                
                if is_current_player_piece:
                    piece_moves = self._get_possible_moves(r_idx, c_idx)
                    for move in piece_moves:
                        if 'capture' not in move:
                            regular_moves.append(move)
        return regular_moves

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        # print(f"\n=== validate_move called with: {move_data} ===")
        # print(f"Current player: {self.current_player}")
        
        if "select" in move_data:
            x, y = move_data["select"]
            # print(f"Selecting piece at ({x},{y})")
            piece = self.board[x, y]
            # print(f"Piece at ({x},{y}): {piece}")
            if piece == 0:
                # print("No piece at selected position")
                return False
            if piece % 2 != self.current_player.value % 2:
                # print(f"Piece at ({x},{y}) does not belong to current player")
                return False
            # print("Selection is valid")
            return True

        if "move" not in move_data:
            # print("No 'move' in move_data")
            return False

        sx, sy = move_data["move"]["from"]
        dx, dy = move_data["move"]["to"]
        # print(f"Attempting move from ({sx},{sy}) to ({dx},{dy})")

        # Check if piece exists and belongs to current player
        piece = self.board[sx, sy]
        # print(f"Piece at source ({sx},{sy}): {piece}")
        
        if piece == 0:
            # print("No piece at source position")
            return False
            
        piece_is_black = piece in [CheckersPiece.BLACK.value, CheckersPiece.BLACK_KING.value]
        current_player_is_black = self.current_player in [CheckersPiece.BLACK, CheckersPiece.BLACK_KING]
        
        if piece_is_black != current_player_is_black:
            # print(f"Piece at ({sx},{sy}) does not belong to current player")
            return False

        # Check if destination is valid
        if not self._is_valid_position(dx, dy):
            # print(f"Destination position ({dx},{dy}) is not valid")
            return False

        # Check if destination is empty
        if self.board[dx, dy] != 0:
            # print(f"Destination position ({dx},{dy}) is not empty")
            return False

        # Check if move is possible
        moves = self._get_possible_moves(sx, sy)
        
        # Check if the destination (dx, dy) is a valid landing spot from the generated moves
        found_target_in_possible_moves = False
        for move_tuple in moves:
            if len(move_tuple) == 2:  # Simple move (to_x, to_y)
                if move_tuple == (dx, dy):
                    found_target_in_possible_moves = True
                    break
            elif len(move_tuple) == 4:  # Capture move (jump_x, jump_y, intermediate_x, intermediate_y)
                if (move_tuple[0], move_tuple[1]) == (dx, dy):  # Compare landing spot
                    found_target_in_possible_moves = True
                    break
        
        if not found_target_in_possible_moves:
            return False

        # Check if must capture (enforce capture rule)
        if self.must_capture:
            if abs(dx - sx) != 2:  # Not a capture move
                # print("Must capture but move is not a capture")
                return False

        # print("Move is valid")
        return True

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        if "select" in move_data:
            self.selected_piece = move_data["select"]
            return self.get_game_state()

        sx, sy = move_data["move"]["from"]
        dx, dy = move_data["move"]["to"]
        piece = self.board[sx, sy]

        # Move piece
        self.board[sx, sy] = 0
        self.board[dx, dy] = piece

        # Check for capture
        if abs(dx - sx) == 2:
            cx = (sx + dx) // 2
            cy = (sy + dy) // 2
            captured_piece = self.board[cx, cy]
            self.board[cx, cy] = 0
            self.captured_pieces[CheckersPiece(captured_piece)] += 1

            # Check for multiple captures
            moves = self._get_possible_moves(dx, dy)
            capture_moves = [(nx, ny) for nx, ny in moves if abs(nx - dx) == 2]
            if capture_moves:
                self.selected_piece = (dx, dy)
                self.must_capture = True
                return self.get_game_state()

        # Check for king promotion
        if piece == CheckersPiece.BLACK.value and dx == self.board_size - 1:  # Black piece reaches bottom row
            # print(f"Promoting black piece at ({dx},{dy}) to king")
            self.board[dx, dy] = CheckersPiece.BLACK_KING.value
        elif piece == CheckersPiece.WHITE.value and dx == 0:  # White piece reaches top row
            # print(f"Promoting white piece at ({dx},{dy}) to king")
            self.board[dx, dy] = CheckersPiece.WHITE_KING.value

        # Switch player
        self.current_player = (
            CheckersPiece.BLACK
            if self.current_player == CheckersPiece.WHITE
            else CheckersPiece.WHITE
        )
        self.selected_piece = None
        self.must_capture = False

        return self.get_game_state()

    def initialize_game(self) -> Dict[str, Any]:
        """Initialize a new game instance"""
        self._init_game()
        return self.get_game_state()

    def _init_game_state(self):
        """Initialize game state"""
        self._init_game()

    def _update_game_state(self, move_data: Dict[str, Any]):
        """Update game state after a move"""
        # The move is already applied in make_move
        pass

    def _restore_game_state(self):
        """Restore game state from history"""
        if not self.history_state:
            return

        self._init_game()  # Reset to initial state
        
        # Replay all moves
        for move_data in self.history_state:
            move = GameMove(**move_data)
            self.make_move(move.move_data)

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        if self.game_over:
            return True
            
        # Check if either player has no pieces left
        black_has_pieces = False
        white_has_pieces = False
        
        for x in range(self.board_size):
            for y in range(self.board_size):
                piece = self.board[x, y]
                if piece in [CheckersPiece.BLACK.value, CheckersPiece.BLACK_KING.value]:
                    black_has_pieces = True
                elif piece in [CheckersPiece.WHITE.value, CheckersPiece.WHITE_KING.value]:
                    white_has_pieces = True
                
                if black_has_pieces and white_has_pieces:
                    break
            if black_has_pieces and white_has_pieces:
                break
        
        if not black_has_pieces or not white_has_pieces:
            self.game_over = True
            return True
                
        # Check if current player has any valid moves
        if not self.get_valid_moves(): 
            self.game_over = True
            return True
                
        return False
    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        # Convert board to string representation
        board = []
        for row in self.board.tolist():
            board_row = []
            for cell in row:
                if cell == 0:
                    board_row.append(None)
                elif cell == CheckersPiece.BLACK.value:
                    board_row.append('B')
                elif cell == CheckersPiece.BLACK_KING.value:
                    board_row.append('B_KING')
                elif cell == CheckersPiece.WHITE.value:
                    board_row.append('W')
                elif cell == CheckersPiece.WHITE_KING.value:
                    board_row.append('W_KING')
            board.append(board_row)
            
        return {
            "board": board,
            "current_player": 'B' if self.current_player in [CheckersPiece.BLACK, CheckersPiece.BLACK_KING] else 'W',
            "selected_piece": self.selected_piece,
            "game_over": self.game_over,
            "winner": self.winner,
            "must_capture": self.must_capture,
            "captured_pieces": {k.name: v for k, v in self.captured_pieces.items()}
        }



    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None

        # Count remaining pieces
        black_pieces = sum(
            1
            for x in range(self.board_size)
            for y in range(self.board_size)
            if self.board[x, y] in [CheckersPiece.BLACK, CheckersPiece.BLACK_KING]
        )
        white_pieces = sum(
            1
            for x in range(self.board_size)
            for y in range(self.board_size)
            if self.board[x, y] in [CheckersPiece.WHITE, CheckersPiece.WHITE_KING]
        )

        if black_pieces == 0:
            return "white"
        elif white_pieces == 0:
            return "black"
        else:
            # If both players have pieces but no moves, it's a draw
            return "draw"
