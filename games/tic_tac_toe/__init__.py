from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List
import time
import copy


class TicTacToeGame(AbstractGame):
    """Implementation of Tic-Tac-Toe game."""

    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.board: List[List[Optional[str]]] = [[None] * 3 for _ in range(3)]
        self.current_player: str = "X"

    def initialize_game(self) -> Dict[str, Any]:
        """Reset the board and start a new game"""
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = "X"
        self.history = GameHistory(self.game_id)
        return self.get_game_state()

    def _init_game_state(self):
        """Initialize game state"""
        self.initialize_game()

    def _update_game_state(self, move_data: Dict[str, Any]):
        """Update game state after a move"""
        # The actual move is already applied in make_move
        # This method is kept for compatibility with the base class
        pass

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """
        Validate if a move is legal.

        Args:
            move_data: A dictionary containing 'player', 'row', and 'col' keys

        Returns:
            bool: True if the move is valid, False otherwise
        """
        # If game is already over, no more moves are allowed
        if self.is_game_over():
            return False
            
        try:
            # Extract move data
            move_data = move_data.get("move_data", move_data)  # Handle nested move_data
            player = move_data.get("player", self.current_player)

            # Convert string coordinates to integers if needed
            row = int(move_data["row"])
            col = int(move_data["col"])


            # Check if the move is within bounds
            if not (0 <= row < 3 and 0 <= col < 3):
                return False

            # Check if the cell is empty
            if self.board[row][col] is not None:
                return False

            # The player making the move must be the current player
            # Convert to string to handle both 'X' and 'x' or 'O' and 'o'
            if str(player).upper() != str(self.current_player).upper():
                return False

            return True

        except (KeyError, ValueError, TypeError) as e:
            print(f"Validation error: {e}")
            return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a move and update game state.

        Args:
            move_data: A dictionary containing 'player' and 'move_data' with 'row' and 'col'

        Returns:
            Dict containing the updated game state

        Raises:
            ValueError: If the move is invalid
        """
        # If game is already over, raise an error
        if self.is_game_over():
            raise ValueError("Game is already over")
            
        # Extract move data and player
        player = move_data.get("player", self.current_player)
        move = move_data.get("move_data", move_data)

        # Add player to move if not present
        if "player" not in move:
            move = move.copy()  # Create a copy to avoid modifying the input
            move["player"] = player

        if not self.validate_move(move):
            raise ValueError(f"Invalid move: {move}")

        # Apply the move
        row = int(move["row"])
        col = int(move["col"])
        self.board[row][col] = player

        # Create and add move to history
        game_move = GameMove(
            player=player, move_data={"row": row, "col": col}, timestamp=time.time()
        )
        self.history.add_move(game_move)

        # Switch players if game is not over
        if not self.is_game_over():
            self.current_player = "O" if self.current_player == "X" else "X"

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
        return self.get_winner() is not None or all(
            all(cell is not None for cell in row) for row in self.board
        )

    def get_winner(self) -> Optional[str]:
        """
        Get the winner if the game is over.

        Returns:
            'X' if X wins, 'O' if O wins, 'draw' if the game is a draw,
            or None if the game is not over yet.
        """
        # Check rows
        for row in range(3):
            if (self.board[row][0] == self.board[row][1] == self.board[row][2] and 
                self.board[row][0] is not None):
                return self.board[row][0]

        # Check columns
        for col in range(3):
            if (self.board[0][col] == self.board[1][col] == self.board[2][col] and 
                self.board[0][col] is not None):
                return self.board[0][col]

        # Check diagonals
        if (self.board[0][0] == self.board[1][1] == self.board[2][2] and 
            self.board[0][0] is not None):
            return self.board[0][0]
            
        if (self.board[0][2] == self.board[1][1] == self.board[2][0] and 
            self.board[0][2] is not None):
            return self.board[0][2]

        # Check for draw (board full)
        if all(cell is not None for row in self.board for cell in row):
            return "draw"

        # Game is not over yet
        return None
