from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple
import time

class ConnectFourGame(AbstractGame):
    ROWS = 6
    COLUMNS = 7
    WIN_LENGTH = 4

    def __init__(self):
        super().__init__()
        self.board = [[None] * self.COLUMNS for _ in range(self.ROWS)]
        self.current_player = 'R'  # Red player starts
        self.game_id = None

    def initialize_game(self) -> Dict[str, Any]:
        """Reset the board and start a new game"""
        self.board = [[None] * self.COLUMNS for _ in range(self.ROWS)]
        self.current_player = 'R'
        self.history = GameHistory()
        return self.get_game_state()

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        try:
            col = int(move_data['column'])
            
            if not (0 <= col < self.COLUMNS):
                return False
                
            if self.board[0][col] is not None:  # Column is full
                return False
                
            if move_data.get('player') != self.current_player:
                return False
                
            return True
        except (KeyError, ValueError):
            return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a move and update game state"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move: Column is full or invalid")
            
        col = int(move_data['column'])
        
        # Find the lowest empty row in the column
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][col] is None:
                self.board[row][col] = self.current_player
                break
        
        # Add move to history
        move = GameMove(
            player=self.current_player,
            move_data={'column': col},
            timestamp=time.time()
        )
        self.history.add_move(move)
        
        # Switch players
        self.current_player = 'Y' if self.current_player == 'R' else 'R'
        
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.get_winner() is not None or all(
            all(cell is not None for cell in row) for row in self.board
        )

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        # Check horizontal
        for row in range(self.ROWS):
            for col in range(self.COLUMNS - self.WIN_LENGTH + 1):
                if self._check_sequence(row, col, (0, 1)):
                    return self.board[row][col]

        # Check vertical
        for col in range(self.COLUMNS):
            for row in range(self.ROWS - self.WIN_LENGTH + 1):
                if self._check_sequence(row, col, (1, 0)):
                    return self.board[row][col]

        # Check diagonal (bottom-left to top-right)
        for row in range(self.ROWS - self.WIN_LENGTH + 1):
            for col in range(self.COLUMNS - self.WIN_LENGTH + 1):
                if self._check_sequence(row, col, (-1, 1)):
                    return self.board[row][col]

        # Check diagonal (top-left to bottom-right)
        for row in range(self.ROWS - self.WIN_LENGTH + 1):
            for col in range(self.COLUMNS - self.WIN_LENGTH + 1):
                if self._check_sequence(row, col, (1, 1)):
                    return self.board[row][col]

        return None

    def _check_sequence(self, start_row: int, start_col: int, direction: Tuple[int, int]) -> bool:
        """Check if there's a winning sequence in the given direction"""
        dr, dc = direction
        player = self.board[start_row][start_col]
        if player is None:
            return False

        for i in range(1, self.WIN_LENGTH):
            r = start_row + dr * i
            c = start_col + dc * i
            if not (0 <= r < self.ROWS and 0 <= c < self.COLUMNS):
                return False
            if self.board[r][c] != player:
                return False
        return True
