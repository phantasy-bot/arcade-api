from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from enum import Enum
import time


class MancalaPlayer(Enum):
    PLAYER1 = 0  # Left player
    PLAYER2 = 1  # Right player


class MancalaGame(AbstractGame):
    def __init__(self, game_id: str, holes: int = 6, seeds: int = 4):
        super().__init__(game_id)
        self.holes = holes
        self.seeds = seeds
        self.board = np.zeros(2 * holes + 2, dtype=int)  # 12 holes + 2 stores
        self.current_player = MancalaPlayer.PLAYER1
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.board = np.zeros(2 * self.holes + 2, dtype=int)
        self.current_player = MancalaPlayer.PLAYER1

        # Initialize holes with seeds
        for i in range(1, self.holes + 1):
            self.board[i] = self.seeds
            self.board[i + self.holes + 1] = self.seeds

    def _get_opposite_hole(self, hole: int) -> int:
        """Get the opposite hole index"""
        return 2 * self.holes + 1 - hole

    def _get_store(self, player: MancalaPlayer) -> int:
        """Get the store index for a player"""
        return 0 if player == MancalaPlayer.PLAYER1 else self.holes + 1

    def _get_player_holes(self, player: MancalaPlayer) -> List[int]:
        """Get the hole indices for a player"""
        start = 1 if player == MancalaPlayer.PLAYER1 else self.holes + 2
        return list(range(start, start + self.holes))

    def _is_valid_move(self, hole: int) -> bool:
        """Check if a move is valid"""
        # Check if hole belongs to current player
        player_holes = self._get_player_holes(self.current_player)
        if hole not in player_holes:
            return False

        # Check if hole has seeds
        return self.board[hole] > 0

    def _make_move(self, hole: int) -> bool:
        """Make a move and return if another turn is granted"""
        seeds = self.board[hole]
        self.board[hole] = 0

        # Distribute seeds
        current = hole
        while seeds > 0:
            current = (current + 1) % len(self.board)
            if current == self._get_store(self.current_player.other):
                continue
            self.board[current] += 1
            seeds -= 1

        # Check if last seed landed in own store
        if current == self._get_store(self.current_player):
            return True  # Take another turn

        # Check if last seed landed in own empty hole with seeds in opposite hole
        if (
            current in self._get_player_holes(self.current_player)
            and self.board[current] == 1
            and self.board[self._get_opposite_hole(current)] > 0
        ):
            # Capture opposite hole's seeds and add to store
            self.board[self._get_store(self.current_player)] += (
                self.board[self._get_opposite_hole(current)] + 1
            )
            self.board[current] = 0
            self.board[self._get_opposite_hole(current)] = 0

        return False

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if "hole" not in move_data:
            return False

        hole = move_data["hole"]
        return self._is_valid_move(hole)

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        hole = move_data["hole"]
        another_turn = self._make_move(hole)

        if not another_turn:
            self.current_player = self.current_player.other

        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "board": self.board.tolist(),
            "current_player": self.current_player.name,
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        # Check if either player has no seeds in their holes
        player1_holes = self.board[1 : self.holes + 1]
        player2_holes = self.board[self.holes + 2 :]

        return np.all(player1_holes == 0) or np.all(player2_holes == 0)

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None

        # Move remaining seeds to stores
        for i in range(1, self.holes + 1):
            self.board[0] += self.board[i]
            self.board[i] = 0

        for i in range(self.holes + 2, 2 * self.holes + 2):
            self.board[self.holes + 1] += self.board[i]
            self.board[i] = 0

        # Compare store counts
        if self.board[0] > self.board[self.holes + 1]:
            return "player1"
        elif self.board[self.holes + 1] > self.board[0]:
            return "player2"
        else:
            return "draw"

    @property
    def other(self) -> "MancalaPlayer":
        """Get the other player"""
        return (
            MancalaPlayer.PLAYER2
            if self.current_player == MancalaPlayer.PLAYER1
            else MancalaPlayer.PLAYER1
        )
