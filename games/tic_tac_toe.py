from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional
import time

class TicTacToeGame(AbstractGame):
    def __init__(self):
        super().__init__()
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = 'X'
        self.game_id = None

    def initialize_game(self) -> Dict[str, Any]:
        """Reset the board and start a new game"""
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = 'X'
        self.history = GameHistory()
        return self.get_game_state()

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        try:
            row = int(move_data['row'])
            col = int(move_data['col'])
            
            if not (0 <= row < 3 and 0 <= col < 3):
                return False
                
            if self.board[row][col] is not None:
                return False
                
            if move_data.get('player') != self.current_player:
                return False
                
            return True
        except (KeyError, ValueError):
            return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a move and update game state"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        row = int(move_data['row'])
        col = int(move_data['col'])
        
        self.board[row][col] = self.current_player
        
        # Add move to history
        move = GameMove(
            player=self.current_player,
            move_data={'row': row, 'col': col},
            timestamp=time.time()
        )
        self.history.add_move(move)
        
        # Switch players
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        
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
        return self.get_winner() is not None or all(all(cell is not None for cell in row) for row in self.board)

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] and row[0] is not None:
                return row[0]

        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] and self.board[0][col] is not None:
                return self.board[0][col]

        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] is not None:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] is not None:
            return self.board[0][2]

        return None
