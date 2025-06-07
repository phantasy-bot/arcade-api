from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple
import time


class OmokGame(AbstractGame):
    BOARD_SIZE = 15  # Standard Omok board size
    WIN_LENGTH = 5

    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player = "B"  # Black player starts
        self._initialize_board()
        
    def _initialize_board(self):
        """Initialize the game board."""
        self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player = "B"  # Black player starts

    def initialize_game(self) -> Dict[str, Any]:
        """Reset the board and start a new game"""
        self._initialize_board()
        self.history = GameHistory()
        return self.get_game_state()

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        try:
            row = int(move_data["row"])
            col = int(move_data["col"])

            if not (0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE):
                return False

            if self.board[row][col] is not None:
                return False

            if move_data.get("player") != self.current_player:
                return False

            return True
        except (KeyError, ValueError):
            return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a move and update game state"""
        try:
            row = int(move_data.get('row', -1))
            col = int(move_data.get('col', -1))
            player = move_data.get('player', self.current_player)
            
            # Validate move
            if not (0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE):
                raise ValueError("Invalid move: Position out of bounds")
                
            if self.board[row][col] is not None:
                raise ValueError("Invalid move: Position already taken")
                
            if player not in ['B', 'W']:
                raise ValueError("Invalid player. Must be 'B' or 'W'")
                
            if player != self.current_player:
                raise ValueError(f"Not {player}'s turn. Current player is {self.current_player}")
                
            if self.is_game_over():
                raise ValueError("Game is already over")
            
            # Make the move
            self.board[row][col] = player
            
            # Save move to history
            move = GameMove(
                player=player,
                move_data={'row': row, 'col': col},
                timestamp=time.time()
            )
            self.history.add_move(move)
            
            # Switch players if game is not over
            if not self.is_game_over():
                self.current_player = 'W' if player == 'B' else 'B'
            
            return self.get_game_state()
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid move: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error making move: {str(e)}")

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "board": self.board,
            "current_player": self.current_player,
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        # Game is over if there's a winner or the board is full
        if self.get_winner() is not None:
            return True
            
        # Check if board is full (draw)
        for row in self.board:
            if None in row:
                return False
        return True

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        # Check all directions from each point
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                if self.board[row][col] is None:
                    continue

                # Check horizontal (right)
                if self._check_sequence(row, col, (0, 1)):
                    return self.board[row][col]

                # Check vertical (down)
                if self._check_sequence(row, col, (1, 0)):
                    return self.board[row][col]

                # Check diagonal (down-right)
                if self._check_sequence(row, col, (1, 1)):
                    return self.board[row][col]
                    
                # Check diagonal (down-left)
                if self._check_sequence(row, col, (1, -1)):
                    return self.board[row][col]
                    
        # Check for draw (board is full)
        if all(cell is not None for row in self.board for cell in row):
            return "draw"
            
        return None

    def _check_sequence(
        self, start_row: int, start_col: int, direction: Tuple[int, int]
    ) -> bool:
        """Check if there's a winning sequence in the given direction"""
        dr, dc = direction
        player = self.board[start_row][start_col]
        if player is None:
            return False

        # Check in both directions
        count = 1
        for i in range(1, self.WIN_LENGTH):
            # Check forward
            r = start_row + dr * i
            c = start_col + dc * i
            if 0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE:
                if self.board[r][c] == player:
                    count += 1
                else:
                    break

        for i in range(1, self.WIN_LENGTH):
            # Check backward
            r = start_row - dr * i
            c = start_col - dc * i
            if 0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE:
                if self.board[r][c] == player:
                    count += 1
                else:
                    break

        return count >= self.WIN_LENGTH
