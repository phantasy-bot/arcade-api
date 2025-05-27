from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time

class TTT3DPiece(Enum):
    EMPTY = 0
    X = 1
    O = 2

class TTT3DGame(AbstractGame):
    def __init__(self, game_id: str, board_size: int = 4):
        super().__init__(game_id)
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size, board_size), dtype=int)
        self.current_player = TTT3DPiece.X
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.board = np.zeros((self.board_size, self.board_size, self.board_size), dtype=int)
        self.current_player = TTT3DPiece.X

    def _is_valid_position(self, x: int, y: int, z: int) -> bool:
        """Check if position is on board and empty"""
        return (0 <= x < self.board_size and 
                0 <= y < self.board_size and 
                0 <= z < self.board_size and 
                self.board[x, y, z] == TTT3DPiece.EMPTY.value)

    def _check_line(self, x: int, y: int, z: int, dx: int, dy: int, dz: int) -> bool:
        """Check if there's a line of 4 pieces in a direction"""
        piece = self.board[x, y, z]
        if piece == TTT3DPiece.EMPTY.value:
            return False
            
        count = 1
        # Check forward direction
        nx, ny, nz = x + dx, y + dy, z + dz
        while (0 <= nx < self.board_size and 
               0 <= ny < self.board_size and 
               0 <= nz < self.board_size and 
               self.board[nx, ny, nz] == piece):
            count += 1
            nx += dx
            ny += dy
            nz += dz
            
        # Check backward direction
        nx, ny, nz = x - dx, y - dy, z - dz
        while (0 <= nx < self.board_size and 
               0 <= ny < self.board_size and 
               0 <= nz < self.board_size and 
               self.board[nx, ny, nz] == piece):
            count += 1
            nx -= dx
            ny -= dy
            nz -= dz
            
        return count >= 4

    def _check_win(self, x: int, y: int, z: int) -> bool:
        """Check if this move wins the game"""
        # Check all 26 directions (excluding [0,0,0])
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    if self._check_line(x, y, z, dx, dy, dz):
                        return True
        return False

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'position' not in move_data:
            return False
            
        position = move_data['position']
        if len(position) != 3:
            return False
            
        x, y, z = position
        return self._is_valid_position(x, y, z)

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        x, y, z = move_data['position']
        piece = self.current_player
        
        # Place piece
        self.board[x, y, z] = piece.value
        
        # Check if this move wins
        if self._check_win(x, y, z):
            return self.get_game_state()
            
        # Switch player
        self.current_player = TTT3DPiece.O if piece == TTT3DPiece.X else TTT3DPiece.X
        
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board': self.board.tolist(),
            'current_player': self.current_player.name,
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.get_winner() is not None

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        # Check if there's any line of 4 pieces
        for x in range(self.board_size):
            for y in range(self.board_size):
                for z in range(self.board_size):
                    if self.board[x, y, z] != TTT3DPiece.EMPTY.value:
                        if self._check_win(x, y, z):
                            return self.current_player.name
        return None
