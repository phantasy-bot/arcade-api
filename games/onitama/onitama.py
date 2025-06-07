from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time


class OnitamaPiece(Enum):
    EMPTY = 0
    BLUE = 1
    RED = 2
    BLUE_MASTER = 3
    RED_MASTER = 4


class OnitamaCard:
    def __init__(self, name: str, moves: List[Tuple[int, int]], active: bool = False):
        self.name = name
        self.moves = moves
        self.active = active

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "moves": self.moves, "active": self.active}


class OnitamaGame(AbstractGame):
    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.board_size = 5
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = OnitamaPiece.BLUE
        self.cards = []
        self.blue_cards = []
        self.red_cards = []
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = OnitamaPiece.BLUE

        # Place pieces
        for i in range(self.board_size):
            self.board[0, i] = OnitamaPiece.BLUE.value
            self.board[4, i] = OnitamaPiece.RED.value
        self.board[0, 2] = OnitamaPiece.BLUE_MASTER.value
        self.board[4, 2] = OnitamaPiece.RED_MASTER.value

        # Initialize cards
        self._init_cards()

    def _init_cards(self):
        """Initialize the deck of cards"""
        self.cards = [
            OnitamaCard("Dragon", [(0, 2), (0, -2), (-1, 0), (1, 0)]),
            OnitamaCard("Crab", [(0, 2), (0, -1), (0, -2)]),
            OnitamaCard("Monkey", [(1, 1), (1, -1), (-1, 1), (-1, -1)]),
            OnitamaCard("Rooster", [(1, 1), (1, -1), (-1, 0)]),
            OnitamaCard("Crane", [(1, 1), (1, 0), (1, -1)]),
            OnitamaCard("Boar", [(0, 1), (1, 0), (0, -1)]),
            OnitamaCard("Frog", [(1, 1), (-1, -1), (-2, 0)]),
            OnitamaCard("Rabbit", [(1, 1), (-1, 1), (-1, -1)]),
            OnitamaCard("Tiger", [(0, 2), (-2, 0)]),
            OnitamaCard("Elephant", [(0, 1), (0, -1), (-1, 0)]),
        ]

        # Shuffle cards and deal
        random.shuffle(self.cards)
        self.blue_cards = self.cards[:2]
        self.red_cards = self.cards[2:4]
        self.cards = self.cards[4:]

    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is on board"""
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def _get_possible_moves(
        self, x: int, y: int, card: OnitamaCard
    ) -> List[Tuple[int, int]]:
        """Get all possible moves for a piece with a card"""
        moves = []
        piece = self.board[x, y]

        # Determine direction based on player
        direction = 1 if piece in [OnitamaPiece.BLUE, OnitamaPiece.BLUE_MASTER] else -1

        for dx, dy in card.moves:
            nx, ny = x + dx * direction, y + dy

            if not self._is_valid_position(nx, ny):
                continue

            if self.board[nx, ny] == 0:
                moves.append((nx, ny))
            elif self.board[nx, ny] % 2 != piece % 2:  # Can capture opponent's piece
                moves.append((nx, ny))

        return moves

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if "card" not in move_data or "x" not in move_data or "y" not in move_data:
            return False

        card_name = move_data["card"]
        x, y = move_data["x"], move_data["y"]

        # Check if card exists and is active
        if self.current_player == OnitamaPiece.BLUE:
            card = next((c for c in self.blue_cards if c.name == card_name), None)
        else:
            card = next((c for c in self.red_cards if c.name == card_name), None)

        if not card or not card.active:
            return False

        # Check if position has valid piece
        piece = self.board[x, y]
        if piece == 0 or piece % 2 != self.current_player.value % 2:
            return False

        # Check if move is valid with card
        moves = self._get_possible_moves(x, y, card)
        if (move_data.get("nx", None), move_data.get("ny", None)) not in moves:
            return False

        return True

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        card_name = move_data["card"]
        x, y = move_data["x"], move_data["y"]
        nx, ny = move_data["nx"], move_data["ny"]

        # Move piece
        piece = self.board[x, y]
        captured_piece = self.board[nx, ny]
        self.board[x, y] = 0
        self.board[nx, ny] = piece

        # Get card
        if self.current_player == OnitamaPiece.BLUE:
            card = next(c for c in self.blue_cards if c.name == card_name)
            self.blue_cards.remove(card)
            self.red_cards.append(card)
        else:
            card = next(c for c in self.red_cards if c.name == card_name)
            self.red_cards.remove(card)
            self.blue_cards.append(card)

        # Draw new card
        if self.cards:
            if self.current_player == OnitamaPiece.BLUE:
                self.blue_cards.append(self.cards.pop(0))
            else:
                self.red_cards.append(self.cards.pop(0))

        # Switch player
        self.current_player = (
            OnitamaPiece.BLUE
            if self.current_player == OnitamaPiece.RED
            else OnitamaPiece.RED
        )

        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "board": self.board.tolist(),
            "current_player": self.current_player.name,
            "blue_cards": [card.to_dict() for card in self.blue_cards],
            "red_cards": [card.to_dict() for card in self.red_cards],
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        # Check if master has reached opponent's side
        if (
            self.board[0, 2] == OnitamaPiece.RED_MASTER.value
            or self.board[4, 2] == OnitamaPiece.BLUE_MASTER.value
        ):
            return True

        # Check if current player has any valid moves
        if self.current_player == OnitamaPiece.BLUE:
            cards = self.blue_cards
        else:
            cards = self.red_cards

        for card in cards:
            if card.active:
                for x in range(self.board_size):
                    for y in range(self.board_size):
                        piece = self.board[x, y]
                        if piece % 2 == self.current_player.value % 2:
                            if self._get_possible_moves(x, y, card):
                                return False
        return True

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None

        # Check if master has reached opponent's side
        if self.board[0, 2] == OnitamaPiece.RED_MASTER.value:
            return "red"
        if self.board[4, 2] == OnitamaPiece.BLUE_MASTER.value:
            return "blue"

        # If no valid moves, opponent wins
        return "red" if self.current_player == OnitamaPiece.BLUE else "blue"
