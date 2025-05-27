from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time

class OthelloPiece(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

class OthelloGame(AbstractGame):
    def __init__(self, game_id: str, board_size: int = 8):
        super().__init__(game_id)
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = OthelloPiece.BLACK
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = OthelloPiece.BLACK
        
        # Set up initial pieces
        center = self.board_size // 2
        self.board[center-1, center-1] = OthelloPiece.WHITE.value
        self.board[center-1, center] = OthelloPiece.BLACK.value
        self.board[center, center-1] = OthelloPiece.BLACK.value
        self.board[center, center] = OthelloPiece.WHITE.value

    def _get_opposite_color(self, color: OthelloPiece) -> OthelloPiece:
        """Get the opposite color"""
        return OthelloPiece.WHITE if color == OthelloPiece.BLACK else OthelloPiece.BLACK

    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is on board"""
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def _get_flips(self, x: int, y: int, dx: int, dy: int) -> List[Tuple[int, int]]:
        """Get all pieces that would be flipped in a given direction"""
        if not self._is_valid_position(x, y):
            return []
            
        # Must be empty to place a piece
        if self.board[x, y] != OthelloPiece.EMPTY.value:
            return []
            
        color = self.current_player
        opposite = self._get_opposite_color(color)
        flips = []
        
        # Move in the given direction
        nx, ny = x + dx, y + dy
        while self._is_valid_position(nx, ny):
            if self.board[nx, ny] == opposite.value:
                flips.append((nx, ny))
                nx += dx
                ny += dy
            elif self.board[nx, ny] == color.value:
                return flips
            else:
                return []
        return []

    def _get_all_flips(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all pieces that would be flipped by placing a piece at (x, y)"""
        all_flips = []
        
        # Check all 8 directions
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1),
                       (0, -1),         (0, 1),
                       (1, -1),  (1, 0),  (1, 1)]:
            all_flips.extend(self._get_flips(x, y, dx, dy))
            
        return all_flips

    def _get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get all valid moves for the current player"""
        moves = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x, y] == OthelloPiece.EMPTY.value:
                    if self._get_all_flips(x, y):
                        moves.append((x, y))
        return moves

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'pass' in move_data and move_data['pass']:
            # Only valid if no valid moves
            return not self._get_valid_moves()
            
        if 'x' not in move_data or 'y' not in move_data:
            return False
            
        x, y = move_data['x'], move_data['y']
        
        # Check if position is on board
        if not self._is_valid_position(x, y):
            return False
            
        # Check if position is empty
        if self.board[x, y] != OthelloPiece.EMPTY.value:
            return False
            
        # Check if move would flip any pieces
        return bool(self._get_all_flips(x, y))

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        if 'pass' in move_data and move_data['pass']:
            # Switch player
            self.current_player = self._get_opposite_color(self.current_player)
            return self.get_game_state()
            
        x, y = move_data['x'], move_data['y']
        
        # Place piece
        self.board[x, y] = self.current_player.value
        
        # Flip pieces
        flips = self._get_all_flips(x, y)
        for fx, fy in flips:
            self.board[fx, fy] = self.current_player.value
            
        # Switch player
        self.current_player = self._get_opposite_color(self.current_player)
        
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board': self.board.tolist(),
            'current_player': self.current_player.name,
            'valid_moves': self._get_valid_moves(),
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        # Check if current player has any moves
        if self._get_valid_moves():
            return False
            
        # Check if other player has any moves
        self.current_player = self._get_opposite_color(self.current_player)
        if self._get_valid_moves():
            return False
            
        return True

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None
            
        # Count pieces
        black_count = np.sum(self.board == OthelloPiece.BLACK.value)
        white_count = np.sum(self.board == OthelloPiece.WHITE.value)
        
        if black_count > white_count:
            return 'black'
        elif white_count > black_count:
            return 'white'
        else:
            return 'draw'
