from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple
import random
import time

# Card ranks and their values
CARD_RANKS = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}

SUITES = ["♠", "♥", "♦", "♣"]


class WarCard:
    def __init__(self, rank: str, suite: str):
        self.rank = rank
        self.suite = suite
        self.value = CARD_RANKS[rank]

    def __str__(self):
        return f"{self.rank}{self.suite}"

    def __repr__(self):
        return str(self)

    def to_dict(self) -> Dict[str, Any]:
        return {"rank": self.rank, "suite": self.suite, "value": self.value}


class WarGame(AbstractGame):
    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.deck = []
        self.player_deck = []
        self.computer_deck = []
        self.current_battle = []
        self.war_cards = []  # Cards played during war
        self.round = 0
        self.max_rounds = 1000  # Prevent infinite games
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self._create_deck()
        self._deal_cards()
        self.current_battle = []
        self.war_cards = []
        self.round = 0

    def _create_deck(self):
        """Create a standard 52-card deck"""
        self.deck = []
        for rank in CARD_RANKS:
            for suite in SUITES:
                self.deck.append(WarCard(rank, suite))
        random.shuffle(self.deck)

    def _deal_cards(self):
        """Deal cards to players"""
        self.player_deck = self.deck[:26]
        self.computer_deck = self.deck[26:]

    def _play_card(self, player: str) -> WarCard:
        """Play a card from the specified player's deck"""
        if player == "player":
            return self.player_deck.pop(0)
        else:
            return self.computer_deck.pop(0)

    def _resolve_battle(self) -> str:
        """Resolve a battle between played cards"""
        if not self.current_battle:
            return None

        player_card = self.current_battle[0]
        computer_card = self.current_battle[1]

        if player_card.value > computer_card.value:
            return "player"
        elif player_card.value < computer_card.value:
            return "computer"
        else:
            return "war"

    def _handle_war(self) -> None:
        """Handle a war situation"""
        # Each player places three cards face down
        for _ in range(3):
            if self.player_deck:
                self.war_cards.append(self.player_deck.pop(0))
            if self.computer_deck:
                self.war_cards.append(self.computer_deck.pop(0))

        # Then each player places one card face up
        if self.player_deck and self.computer_deck:
            self.current_battle = [self.player_deck.pop(0), self.computer_deck.pop(0)]
        else:
            # If either player can't play, the other wins
            if not self.player_deck:
                return "computer"
            else:
                return "player"

    def _resolve_war(self) -> str:
        """Resolve a war situation"""
        winner = self._resolve_battle()
        if winner == "war":
            return self._handle_war()
        return winner

    def _distribute_cards(self, winner: str) -> None:
        """Distribute cards to the winner"""
        if winner == "player":
            self.player_deck.extend(self.current_battle + self.war_cards)
        else:
            self.computer_deck.extend(self.current_battle + self.war_cards)

        self.current_battle = []
        self.war_cards = []

    def make_move(self) -> Dict[str, Any]:
        """Play a round of War"""
        if self.round >= self.max_rounds:
            raise ValueError("Maximum number of rounds reached")

        self.round += 1

        # Check if game is over
        if not self.player_deck or not self.computer_deck:
            return self.get_game_state()

        # Play cards
        self.current_battle = [self._play_card("player"), self._play_card("computer")]

        # Resolve battle
        winner = self._resolve_battle()

        # Handle war
        while winner == "war":
            winner = self._resolve_war()

        # Distribute cards
        self._distribute_cards(winner)

        # Add move to history
        move = GameMove(
            player=winner,
            move_data={
                "round": self.round,
                "player_card": self.current_battle[0].to_dict(),
                "computer_card": self.current_battle[1].to_dict(),
                "war_cards": [card.to_dict() for card in self.war_cards],
                "winner": winner,
            },
            timestamp=time.time(),
        )
        self.history.add_move(move)

        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "round": self.round,
            "player_cards": len(self.player_deck),
            "computer_cards": len(self.computer_deck),
            "current_battle": (
                [card.to_dict() for card in self.current_battle]
                if self.current_battle
                else None
            ),
            "war_cards": [card.to_dict() for card in self.war_cards],
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return (
            not self.player_deck
            or not self.computer_deck
            or self.round >= self.max_rounds
        )

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        if self.is_game_over():
            if len(self.player_deck) > len(self.computer_deck):
                return "player"
            elif len(self.computer_deck) > len(self.player_deck):
                return "computer"
            else:
                return "draw"
        return None
