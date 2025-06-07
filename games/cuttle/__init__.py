from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import random
import time

# Define card values and suits
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

# Define special cards
SPECIAL_CARDS = {
    "J": "Jack",  # Jacks are wild
    "Q": "Queen",  # Queens are wild
    "K": "King",  # Kings are wild
    "A": "Ace",  # Aces are wild
}


class CuttleCard:
    def __init__(self, rank: str, suite: str):
        self.rank = rank
        self.suite = suite
        self.value = CARD_RANKS[rank]
        self.is_wild = rank in SPECIAL_CARDS

    def __str__(self):
        return f"{self.rank}{self.suite}"

    def __repr__(self):
        return str(self)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "suite": self.suite,
            "value": self.value,
            "is_wild": self.is_wild,
        }


class CuttleGame(AbstractGame):
    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.deck = []
        self.player_hand = []
        self.computer_hand = []
        self.table = []
        self.player_score = 0
        self.computer_score = 0
        self.current_turn = "player"
        self.round = 0
        self.max_rounds = 100  # Prevent infinite games
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self._create_deck()
        self._deal_initial_cards()
        self.table = []
        self.player_score = 0
        self.computer_score = 0
        self.current_turn = "player"
        self.round = 0

    def _create_deck(self):
        """Create a standard 52-card deck"""
        self.deck = []
        for rank in CARD_RANKS:
            for suite in SUITES:
                self.deck.append(CuttleCard(rank, suite))
        random.shuffle(self.deck)

    def _deal_initial_cards(self):
        """Deal initial cards to players"""
        # Deal 4 cards to each player
        self.player_hand = self.deck[:4]
        self.computer_hand = self.deck[4:8]
        self.deck = self.deck[8:]

    def _play_card(self, player: str, card_idx: int) -> CuttleCard:
        """Play a card from the specified player's hand"""
        if player == "player":
            return self.player_hand.pop(card_idx)
        else:
            return self.computer_hand.pop(card_idx)

    def _find_matches(self, card: CuttleCard) -> List[int]:
        """Find matching cards on the table"""
        matches = []
        for i, table_card in enumerate(self.table):
            # Check for exact match
            if card.rank == table_card.rank:
                matches.append(i)
                continue

            # Check for wild cards
            if card.is_wild or table_card.is_wild:
                matches.append(i)
                continue

            # Check for sequence (within 1)
            if abs(card.value - table_card.value) == 1:
                matches.append(i)

        return matches

    def _capture_cards(self, matches: List[int]) -> List[CuttleCard]:
        """Capture cards from the table"""
        captured = []
        for i in sorted(matches, reverse=True):
            captured.append(self.table.pop(i))
        return captured

    def _score_cards(self, cards: List[CuttleCard]) -> int:
        """Score captured cards"""
        score = 0
        for card in cards:
            if card.rank in SPECIAL_CARDS:
                score += 20  # Special cards worth 20 points
            else:
                score += card.value  # Regular cards worth face value
        return score

    def _computer_play(self) -> Dict[str, Any]:
        """Computer player's strategy"""
        best_score = -1
        best_move = None

        # Try each card
        for i, card in enumerate(self.computer_hand):
            matches = self._find_matches(card)
            if matches:
                captured = self._capture_cards(matches)
                score = self._score_cards([card] + captured)

                if score > best_score:
                    best_score = score
                    best_move = {"card_idx": i, "matches": matches, "score": score}

                # Return cards to table for next iteration
                self.table.extend(captured)

        if best_move:
            return best_move

        # If no matches, just play any card
        return {"card_idx": 0, "matches": [], "score": 0}

    def make_move(self, card_idx: int) -> Dict[str, Any]:
        """Make a move in the game"""
        if self.current_turn != "player":
            raise ValueError("It's not your turn")

        if self.round >= self.max_rounds:
            raise ValueError("Maximum number of rounds reached")

        self.round += 1

        # Play player's card
        player_card = self._play_card("player", card_idx)
        self.table.append(player_card)

        # Find matches
        matches = self._find_matches(player_card)

        # Capture cards if matches found
        if matches:
            captured = self._capture_cards(matches)
            captured.append(player_card)
            self.player_score += self._score_cards(captured)

        # Draw a new card if available
        if self.deck:
            self.player_hand.append(self.deck.pop(0))

        # Computer's turn
        computer_move = self._computer_play()
        computer_card = self._play_card("computer", computer_move["card_idx"])
        self.table.append(computer_card)

        # Capture cards if matches found
        matches = computer_move["matches"]
        if matches:
            captured = self._capture_cards(matches)
            captured.append(computer_card)
            self.computer_score += self._score_cards(captured)

        # Draw a new card if available
        if self.deck:
            self.computer_hand.append(self.deck.pop(0))

        # Add move to history
        move = GameMove(
            player="player",
            move_data={
                "round": self.round,
                "player_card": player_card.to_dict(),
                "computer_card": computer_card.to_dict(),
                "player_score": self.player_score,
                "computer_score": self.computer_score,
                "table": [card.to_dict() for card in self.table],
            },
            timestamp=time.time(),
        )
        self.history.add_move(move)

        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "round": self.round,
            "player_score": self.player_score,
            "computer_score": self.computer_score,
            "player_hand": [card.to_dict() for card in self.player_hand],
            "table": [card.to_dict() for card in self.table],
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return (
            not self.deck
            and not self.player_hand
            and not self.computer_hand
            or self.round >= self.max_rounds
        )

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        if self.is_game_over():
            if self.player_score > self.computer_score:
                return "player"
            elif self.computer_score > self.player_score:
                return "computer"
            else:
                return "draw"
        return None
