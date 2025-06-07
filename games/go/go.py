from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time


class GoStone(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2


class GoGroup:
    def __init__(self, color: GoStone, stones: Set[Tuple[int, int]]):
        self.color = color
        self.stones = stones
        self.liberties = set()

    def add_liberty(self, pos: Tuple[int, int]) -> None:
        self.liberties.add(pos)

    def remove_liberty(self, pos: Tuple[int, int]) -> None:
        self.liberties.discard(pos)

    def is_captured(self) -> bool:
        return len(self.liberties) == 0

    def merge(self, other: "GoGroup") -> None:
        self.stones.update(other.stones)
        self.liberties.update(other.liberties)


class GoGame(AbstractGame):
    def __init__(self, game_id: str, board_size: int = 19):
        super().__init__(game_id)
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = GoStone.BLACK
        self.groups = []
        self.ko_position = None
        self.history = []
        self.captured_stones = {GoStone.BLACK: 0, GoStone.WHITE: 0}
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = GoStone.BLACK
        self.groups = []
        self.ko_position = None
        self.history = []
        self.captured_stones = {GoStone.BLACK: 0, GoStone.WHITE: 0}

    def _get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get all valid neighboring positions"""
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                neighbors.append((nx, ny))
        return neighbors

    def _find_group(self, pos: Tuple[int, int]) -> Optional[GoGroup]:
        """Find the group containing the given position"""
        for group in self.groups:
            if pos in group.stones:
                return group
        return None

    def _create_group(self, pos: Tuple[int, int], color: GoStone) -> GoGroup:
        """Create a new group with the given stone"""
        group = GoGroup(color, {pos})
        for neighbor in self._get_neighbors(pos):
            if self.board[neighbor] == 0:
                group.add_liberty(neighbor)
        return group

    def _merge_groups(self, group: GoGroup, pos: Tuple[int, int]) -> None:
        """Merge adjacent groups of the same color"""
        for neighbor in self._get_neighbors(pos):
            if self.board[neighbor] == group.color:
                neighbor_group = self._find_group(neighbor)
                if neighbor_group and neighbor_group != group:
                    group.merge(neighbor_group)
                    self.groups.remove(neighbor_group)

    def _capture_groups(self, pos: Tuple[int, int]) -> None:
        """Capture any groups that are surrounded"""
        for neighbor in self._get_neighbors(pos):
            if (
                self.board[neighbor] != 0
                and self.board[neighbor] != self.current_player.value
            ):
                group = self._find_group(neighbor)
                if group and group.is_captured():
                    self.captured_stones[GoStone(self.board[neighbor])] += len(
                        group.stones
                    )
                    for stone in group.stones:
                        self.board[stone] = 0
                    self.groups.remove(group)

    def _update_liberties(self, pos: Tuple[int, int]) -> None:
        """Update liberties for all groups affected by a move"""
        for neighbor in self._get_neighbors(pos):
            if self.board[neighbor] != 0:
                group = self._find_group(neighbor)
                if group:
                    group.remove_liberty(pos)
                    if self.board[pos] == 0:
                        group.add_liberty(pos)

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if "pass" in move_data and move_data["pass"]:
            return True

        x, y = move_data["x"], move_data["y"]

        # Check if position is on board
        if not (0 <= x < self.board_size and 0 <= y < self.board_size):
            return False

        # Check if position is empty
        if self.board[x, y] != 0:
            return False

        # Check for ko rule violation
        if (x, y) == self.ko_position:
            return False

        # Check for suicide
        test_board = np.copy(self.board)
        test_board[x, y] = self.current_player.value
        group = self._create_group((x, y), self.current_player)
        self._update_liberties((x, y))
        return not group.is_captured()

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        if "pass" in move_data and move_data["pass"]:
            self.history.append(None)
            self.current_player = (
                GoStone.WHITE if self.current_player == GoStone.BLACK else GoStone.BLACK
            )
            return self.get_game_state()

        x, y = move_data["x"], move_data["y"]

        # Place stone
        self.board[x, y] = self.current_player.value

        # Create new group
        group = self._create_group((x, y), self.current_player)
        self.groups.append(group)

        # Merge with adjacent groups
        self._merge_groups(group, (x, y))

        # Capture any surrounded groups
        self._capture_groups((x, y))

        # Update liberties
        self._update_liberties((x, y))

        # Check for ko
        if len(self.history) >= 2:
            last_state = self.history[-2]
            if last_state is not None and np.array_equal(last_state, self.board):
                self.ko_position = (x, y)
            else:
                self.ko_position = None

        # Switch player
        self.current_player = (
            GoStone.WHITE if self.current_player == GoStone.BLACK else GoStone.BLACK
        )

        # Add move to history
        self.history.append(np.copy(self.board))

        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "board": self.board.tolist(),
            "current_player": self.current_player.name,
            "captured_stones": self.captured_stones,
            "ko_position": self.ko_position,
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        # Game ends when both players pass consecutively
        if len(self.history) >= 2:
            last_two = self.history[-2:]
            return all(move is None for move in last_two)
        return False

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None

        # Calculate territory for each player
        territory = {GoStone.BLACK: 0, GoStone.WHITE: 0}
        visited = set()

        for x in range(self.board_size):
            for y in range(self.board_size):
                if (x, y) in visited or self.board[x, y] != 0:
                    continue

                # Find territory region
                region = set()
                frontier = [(x, y)]

                while frontier:
                    pos = frontier.pop()
                    if pos in visited:
                        continue

                    visited.add(pos)
                    region.add(pos)

                    for neighbor in self._get_neighbors(pos):
                        if neighbor not in visited and self.board[neighbor] == 0:
                            frontier.append(neighbor)

                # Determine territory ownership
                adjacent_colors = set()
                for pos in region:
                    for neighbor in self._get_neighbors(pos):
                        if self.board[neighbor] != 0:
                            adjacent_colors.add(GoStone(self.board[neighbor]))

                if len(adjacent_colors) == 1:
                    territory[list(adjacent_colors)[0]] += len(region)

        # Calculate total score for each player
        scores = {
            GoStone.BLACK: territory[GoStone.BLACK]
            + self.captured_stones[GoStone.BLACK],
            GoStone.WHITE: territory[GoStone.WHITE]
            + self.captured_stones[GoStone.WHITE]
            + 7.5,  # Komi
        }

        if scores[GoStone.BLACK] > scores[GoStone.WHITE]:
            return "black"
        elif scores[GoStone.WHITE] > scores[GoStone.BLACK]:
            return "white"
        else:
            return "draw"
