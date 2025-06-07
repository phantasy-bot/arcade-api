from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple
import time


class OmokGame(AbstractGame):
    BOARD_SIZE = 15  # Standard Omok board size
    WIN_LENGTH = 5

    def __init__(self):
        super().__init__()
        self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player = "B"  # Black player starts
        self.game_id = None

    def initialize_game(self) -> Dict[str, Any]:
        """Reset the board and start a new game"""
        self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player = "B"
        return super().initialize_game()

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
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        row = int(move_data["row"])
        col = int(move_data["col"])

        self.board[row][col] = self.current_player

        # Add move to history
        move = GameMove(
            player=self.current_player,
            move_data={"row": row, "col": col},
            timestamp=time.time(),
        )
        self.history.add_move(move)

        # Switch players
        self.current_player = "W" if self.current_player == "B" else "B"

        return self.get_game_state()

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
        return self.get_winner() is not None

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        # Check all directions from each point
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                if self.board[row][col] is None:
                    continue

                # Check horizontal
                if self._check_sequence(row, col, (0, 1)):
                    return self.board[row][col]

                # Check vertical
                if self._check_sequence(row, col, (1, 0)):
                    return self.board[row][col]

                # Check diagonal (bottom-left to top-right)
                if self._check_sequence(row, col, (-1, 1)):
                    return self.board[row][col]

                # Check diagonal (top-left to bottom-right)
                if self._check_sequence(row, col, (1, 1)):
                    return self.board[row][col]
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
