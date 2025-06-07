from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict


class Card:
    def __init__(self, suit: str, rank: int):
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        return self.rank == other.rank

    def __hash__(self):
        return hash(self.rank)

    def to_dict(self) -> Dict[str, Any]:
        return {"suit": self.suit, "rank": self.rank}


class BSGame(AbstractGame):
    def __init__(self, game_id: str, num_players: int = 4):
        super().__init__(game_id)
        self.num_players = num_players
        self.current_player = 0
        self.current_rank = 2  # Start with 2s
        self.deck = []
        self.hands = defaultdict(list)
        self.discard_pile = []
        self.last_claim = []
        self.last_player = None
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.deck = []
        self.hands = defaultdict(list)
        self.discard_pile = []
        self.last_claim = []
        self.last_player = None
        self.current_player = 0
        self.current_rank = 2

        # Create deck (4 suits, ranks 2-14)
        suits = ["♠", "♥", "♦", "♣"]
        for suit in suits:
            for rank in range(2, 15):  # 2-14 (2-A)
                self.deck.append(Card(suit, rank))
        random.shuffle(self.deck)

        # Deal cards
        for i in range(self.num_players):
            self.hands[i] = [
                self.deck.pop() for _ in range(len(self.deck) // self.num_players)
            ]

        # Place remaining cards in discard pile
        self.discard_pile = self.deck

    def _has_rank(self, player: int, rank: int) -> bool:
        """Check if player has cards of the given rank"""
        return any(card.rank == rank for card in self.hands[player])

    def _call_bs(self, player: int) -> bool:
        """Check if last play was BS"""
        if not self.last_claim or not self.last_player:
            return False

        # Check if last player had any cards of the claimed rank
        return not any(card.rank == self.current_rank for card in self.last_claim)

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if "type" not in move_data:
            return False

        move_type = move_data["type"]

        if move_type == "play":
            if "cards" not in move_data or "claim" not in move_data:
                return False

            cards = move_data["cards"]
            claim = move_data["claim"]

            # Check if player has cards
            if not cards:
                return False

            # Check if claim is valid
            if claim < 1:
                return False

            # Check if player has enough cards
            if len(cards) != claim:
                return False

            # Check if cards exist in player's hand
            hand = self.hands[self.current_player]
            if not all(Card(card["suit"], card["rank"]) in hand for card in cards):
                return False

            return True

        elif move_type == "call_bs":
            # Can only call BS if there was a previous play
            return bool(self.last_claim and self.last_player)

        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        move_type = move_data["type"]

        if move_type == "play":
            cards = [Card(card["suit"], card["rank"]) for card in move_data["cards"]]
            claim = move_data["claim"]

            # Remove cards from player's hand
            for card in cards:
                self.hands[self.current_player].remove(card)

            # Add cards to discard pile
            self.discard_pile.extend(cards)

            # Update game state
            self.last_claim = cards
            self.last_player = self.current_player

            # Move to next player
            self.current_player = (self.current_player + 1) % self.num_players

            return self.get_game_state()

        elif move_type == "call_bs":
            # Check if last play was BS
            is_bs = self._call_bs(self.current_player)

            if is_bs:
                # Last player takes all cards
                self.hands[self.last_player].extend(self.discard_pile)
                self.discard_pile = []
            else:
                # Calling player takes all cards
                self.hands[self.current_player].extend(self.discard_pile)
                self.discard_pile = []

            # Move to next player
            self.current_player = (self.current_player + 1) % self.num_players

            return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "hands": {
                str(k): [card.to_dict() for card in v] for k, v in self.hands.items()
            },
            "current_player": self.current_player,
            "current_rank": self.current_rank,
            "discard_pile_size": len(self.discard_pile),
            "last_claim": (
                [card.to_dict() for card in self.last_claim]
                if self.last_claim
                else None
            ),
            "last_player": self.last_player,
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

        # First player to run out of cards wins
        for i in range(self.num_players):
            if not self.hands[i]:
                return i
        return None
