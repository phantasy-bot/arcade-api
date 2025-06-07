from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict


class UnoCard:
    def __init__(self, color: str, value: str, special: bool = False):
        self.color = color
        self.value = value
        self.special = special
        self.wild = color == "wild"

    def can_play_on(self, other: "UnoCard") -> bool:
        """Check if this card can be played on another card"""
        if self.wild:
            return True
        if other.wild:
            return False
        return self.color == other.color or self.value == other.value

    def to_dict(self) -> Dict[str, str]:
        return {
            "color": self.color,
            "value": self.value,
            "special": self.special,
            "wild": self.wild,
        }


class UnoAction(Enum):
    PLAY = 1
    DRAW = 2
    CHOOSE_COLOR = 3


class UnoGame(AbstractGame):
    def __init__(self, game_id: str, num_players: int = 4):
        super().__init__(game_id)
        self.num_players = num_players
        self.current_player = 0
        self.hands = defaultdict(list)
        self.deck = []
        self.discard_pile = []
        self.direction = 1  # 1 for clockwise, -1 for counterclockwise
        self.draw_count = 0
        self.skip_count = 0
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.hands = defaultdict(list)
        self.current_player = 0
        self.deck = []
        self.discard_pile = []
        self.direction = 1
        self.draw_count = 0
        self.skip_count = 0

        # Create deck
        colors = ["red", "yellow", "green", "blue"]
        values = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "skip",
            "reverse",
            "draw2",
        ]

        # Create regular cards
        for color in colors:
            self.deck.append(UnoCard(color, "0"))
            for value in values[1:]:
                self.deck.append(
                    UnoCard(color, value, value in ["skip", "reverse", "draw2"])
                )
                self.deck.append(
                    UnoCard(color, value, value in ["skip", "reverse", "draw2"])
                )

        # Create wild cards
        for _ in range(4):
            self.deck.append(UnoCard("wild", "wild", True))
            self.deck.append(UnoCard("wild", "wild4", True))

        random.shuffle(self.deck)

        # Deal cards (7 cards to each player)
        for i in range(self.num_players):
            for _ in range(7):
                self.hands[i].append(self.deck.pop())

        # Place first card on discard pile
        # Make sure it's not a wild card
        while self.deck[-1].wild:
            random.shuffle(self.deck)
        self.discard_pile.append(self.deck.pop())

    def _process_special_cards(self, card: UnoCard) -> None:
        """Process special card effects"""
        if card.value == "skip":
            self.skip_count = 1
        elif card.value == "reverse":
            self.direction *= -1
        elif card.value == "draw2":
            self.draw_count += 2
        elif card.value == "wild4":
            self.draw_count += 4

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if "action" not in move_data:
            return False

        action = move_data["action"]

        if action == UnoAction.PLAY.name:
            if "card" not in move_data:
                return False

            card = UnoCard(
                move_data["card"]["color"],
                move_data["card"]["value"],
                move_data["card"]["special"],
            )
            if card not in self.hands[self.current_player]:
                return False

            top_card = self.discard_pile[-1]
            if not card.can_play_on(top_card):
                return False

            # If playing a wild card, must choose color
            if card.wild and "new_color" not in move_data:
                return False

            return True

        elif action == UnoAction.DRAW.name:
            return True

        elif action == UnoAction.CHOOSE_COLOR.name:
            if "color" not in move_data:
                return False

            # Must be after playing a wild card
            if not self.discard_pile[-1].wild:
                return False

            color = move_data["color"]
            return color in ["red", "yellow", "green", "blue"]

        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        action = move_data["action"]

        if action == UnoAction.PLAY.name:
            card = UnoCard(
                move_data["card"]["color"],
                move_data["card"]["value"],
                move_data["card"]["special"],
            )

            # Remove card from hand
            self.hands[self.current_player].remove(card)

            # Process special card effects
            self._process_special_cards(card)

            # Place on discard pile
            self.discard_pile.append(card)

            # If playing a wild card, choose color
            if card.wild:
                if "new_color" in move_data:
                    self.discard_pile[-1].color = move_data["new_color"]
                else:
                    # Must choose color next turn
                    return self.get_game_state()

        elif action == UnoAction.DRAW.name:
            # Draw cards
            for _ in range(self.draw_count + 1):
                if self.deck:
                    self.hands[self.current_player].append(self.deck.pop())
                else:
                    # Reshuffle discard pile except top card
                    self.deck = self.discard_pile[:-1]
                    random.shuffle(self.deck)
                    self.discard_pile = [self.discard_pile[-1]]
                    self.hands[self.current_player].append(self.deck.pop())

            # Reset draw count
            self.draw_count = 0

        elif action == UnoAction.CHOOSE_COLOR.name:
            self.discard_pile[-1].color = move_data["color"]

        # Process skip and draw effects
        if self.skip_count > 0:
            self.skip_count -= 1
            self.current_player = (
                self.current_player + self.direction
            ) % self.num_players
            return self.get_game_state()

        if self.draw_count > 0:
            return self.get_game_state()

        # Move to next player
        self.current_player = (self.current_player + self.direction) % self.num_players

        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "hands": {
                str(k): [card.to_dict() for card in v] for k, v in self.hands.items()
            },
            "current_player": self.current_player,
            "discard_pile_top": (
                self.discard_pile[-1].to_dict() if self.discard_pile else None
            ),
            "direction": self.direction,
            "draw_count": self.draw_count,
            "skip_count": self.skip_count,
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return any(not self.hands[i] for i in range(self.num_players))

    def get_winner(self) -> Optional[int]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None

        # First player to finish wins
        for i in range(self.num_players):
            if not self.hands[i]:
                return i
        return None
