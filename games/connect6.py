from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time

class Connect6Piece(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

class Connect6Game(AbstractGame):
    def __init__(self, game_id: str, board_size: int = 19):
        super().__init__(game_id)
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = Connect6Piece.BLACK
        self.turn = 1  # First turn (Black places two stones)
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = Connect6Piece.BLACK
        self.turn = 1

    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is on board and empty"""
        return (0 <= x < self.board_size and 
                0 <= y < self.board_size and 
                self.board[x, y] == Connect6Piece.EMPTY.value)

    def _check_line(self, x: int, y: int, dx: int, dy: int) -> bool:
        """Check if there's a line of 6 pieces in a direction"""
        piece = self.board[x, y]
        if piece == Connect6Piece.EMPTY.value:
            return False
            
        count = 1
        # Check forward direction
        nx, ny = x + dx, y + dy
        while (0 <= nx < self.board_size and 
               0 <= ny < self.board_size and 
               self.board[nx, ny] == piece):
            count += 1
            nx += dx
            ny += dy
            
        # Check backward direction
        nx, ny = x - dx, y - dy
        while (0 <= nx < self.board_size and 
               0 <= ny < self.board_size and 
               self.board[nx, ny] == piece):
            count += 1
            nx -= dx
            ny -= dy
            
        return count >= 6

    def _check_win(self, x: int, y: int) -> bool:
        """Check if this move wins the game"""
        # Check all 8 directions
        for dx, dy in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            if self._check_line(x, y, dx, dy):
                return True
        return False

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'positions' not in move_data:
            return False
            
        positions = move_data['positions']
        
        # First turn must be exactly 2 positions
        if self.turn == 1 and len(positions) != 2:
            return False
            
        # All other turns must be exactly 1 position
        if self.turn > 1 and len(positions) != 1:
            return False
            
        # Check each position
        for x, y in positions:
            if not self._is_valid_position(x, y):
                return False
                
        return True

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        positions = move_data['positions']
        piece = self.current_player
        
        # Place pieces
        for x, y in positions:
            self.board[x, y] = piece.value
            
            # Check if this move wins
            if self._check_win(x, y):
                return self.get_game_state()
                
        # Update turn
        self.turn += 1
        self.current_player = Connect6Piece.WHITE if self.current_player == Connect6Piece.BLACK else Connect6Piece.BLACK
        
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board': self.board.tolist(),
            'current_player': self.current_player.name,
            'turn': self.turn,
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.get_winner() is not None

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        # Check if there are any lines of 6
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x, y] != Connect6Piece.EMPTY.value:
                    if self._check_win(x, y):
                        return self.current_player.name
        return None
