from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from enum import Enum
import time

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

    def _init_game(self):
        """Initialize a new game"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = CheckersPiece.BLACK
        self.selected_piece = None
        self.must_capture = False
        self.captured_pieces = {CheckersPiece.BLACK: 0, CheckersPiece.WHITE: 0}
        
        # Place initial pieces
        for row in range(self.board_size):
            for col in range(self.board_size):
                if (row + col) % 2 == 0:  # Only place pieces on dark squares
                    if row < 3:
                        self.board[row, col] = CheckersPiece.WHITE.value
                    elif row >= 5:
                        self.board[row, col] = CheckersPiece.BLACK.value

    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is on board and on a dark square"""
        return (0 <= x < self.board_size and 
                0 <= y < self.board_size and 
                (x + y) % 2 == 0)

    def _get_possible_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all possible moves for a piece"""
        piece = self.board[x, y]
        if piece == 0:
            return []
            
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        # Regular moves
        for dx, dy in directions:
            if piece in [CheckersPiece.BLACK, CheckersPiece.BLACK_KING]:
                if dx == 1:  # Black pieces can only move forward unless king
                    continue
            if piece in [CheckersPiece.WHITE, CheckersPiece.WHITE_KING]:
                if dx == -1:  # White pieces can only move forward unless king
                    continue
                    
            nx, ny = x + dx, y + dy
            if self._is_valid_position(nx, ny) and self.board[nx, ny] == 0:
                moves.append((nx, ny))
                
        # Capture moves
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not self._is_valid_position(nx, ny):
                continue
                
            if self.board[nx, ny] != 0 and self.board[nx, ny] % 2 != piece % 2:
                # Enemy piece found
                nx2, ny2 = nx + dx, ny + dy
                if self._is_valid_position(nx2, ny2) and self.board[nx2, ny2] == 0:
                    moves.append((nx2, ny2))
                    
        return moves

    def _get_all_captures(self, piece_type: CheckersPiece) -> List[Tuple[int, int, int, int]]:
        """Get all possible capture moves for a player"""
        captures = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x, y] in [piece_type, piece_type + 1]:  # Check both regular and king pieces
                    moves = self._get_possible_moves(x, y)
                    for nx, ny in moves:
                        if abs(nx - x) == 2:  # Only consider capture moves
                            captures.append((x, y, nx, ny))
        return captures

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'select' in move_data:
            x, y = move_data['select']
            piece = self.board[x, y]
            if piece == 0:
                return False
            if piece % 2 != self.current_player.value % 2:
                return False
            return True
            
        if 'move' not in move_data:
            return False
            
        sx, sy = move_data['move']['from']
        dx, dy = move_data['move']['to']
        
        # Check if piece exists and belongs to current player
        piece = self.board[sx, sy]
        if piece == 0 or piece % 2 != self.current_player.value % 2:
            return False
            
        # Check if destination is valid
        if not self._is_valid_position(dx, dy):
            return False
            
        # Check if destination is empty
        if self.board[dx, dy] != 0:
            return False
            
        # Check if move is possible
        moves = self._get_possible_moves(sx, sy)
        if (dx, dy) not in moves:
            return False
            
        # Check if must capture
        if self.must_capture:
            if abs(dx - sx) != 2:  # Not a capture move
                return False
                
        return True

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        if 'select' in move_data:
            self.selected_piece = move_data['select']
            return self.get_game_state()
            
        sx, sy = move_data['move']['from']
        dx, dy = move_data['move']['to']
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
        if piece in [CheckersPiece.BLACK, CheckersPiece.WHITE] and dy in [0, self.board_size - 1]:
            self.board[dx, dy] += 1
            
        # Switch player
        self.current_player = CheckersPiece.BLACK if self.current_player == CheckersPiece.WHITE else CheckersPiece.WHITE
        self.selected_piece = None
        self.must_capture = False
        
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board': self.board.tolist(),
            'current_player': self.current_player.name,
            'selected_piece': self.selected_piece,
            'must_capture': self.must_capture,
            'captured_pieces': self.captured_pieces,
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        # Check if current player has any moves
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x, y] in [self.current_player, self.current_player + 1]:
                    if self._get_possible_moves(x, y):
                        return False
        return True

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None
            
        # Count remaining pieces
        black_pieces = sum(1 for x in range(self.board_size) 
                          for y in range(self.board_size) 
                          if self.board[x, y] in [CheckersPiece.BLACK, CheckersPiece.BLACK_KING])
        white_pieces = sum(1 for x in range(self.board_size) 
                          for y in range(self.board_size) 
                          if self.board[x, y] in [CheckersPiece.WHITE, CheckersPiece.WHITE_KING])
        
        if black_pieces == 0:
            return 'white'
        elif white_pieces == 0:
            return 'black'
        else:
            # If both players have pieces but no moves, it's a draw
            return 'draw'
