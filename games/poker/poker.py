from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict


class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
        self.value = self._get_card_value()

    def _get_card_value(self) -> int:
        """Get the card's value for comparison"""
        rank_order = {
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
        suit_order = {"♣": 0, "♦": 1, "♥": 2, "♠": 3}
        return rank_order[self.rank] * 4 + suit_order[self.suit]

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash((self.suit, self.rank))

    def to_dict(self) -> Dict[str, str]:
        return {"suit": self.suit, "rank": self.rank}


class PokerHandType(Enum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9


class PokerAction(Enum):
    FOLD = 0
    CHECK = 1
    CALL = 2
    BET = 3
    RAISE = 4


class PokerGame(AbstractGame):
    def __init__(self, game_id: str, num_players: int = 4, small_blind: int = 10):
        super().__init__(game_id)
        self.num_players = num_players
        self.small_blind = small_blind
        self.big_blind = small_blind * 2
        self.current_player = 0
        self.hands = defaultdict(list)
        self.community_cards = []
        self.deck = []
        self.pot = 0
        self.bets = defaultdict(int)
        self.current_bet = 0
        self.round = 0
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.hands = defaultdict(list)
        self.current_player = 0
        self.community_cards = []
        self.deck = []
        self.pot = 0
        self.bets = defaultdict(int)
        self.current_bet = 0
        self.round = 0

        # Create deck
        suits = ["♠", "♥", "♦", "♣"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.deck = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.deck)

        # Deal cards (2 cards to each player)
        for i in range(self.num_players):
            for _ in range(2):
                self.hands[i].append(self.deck.pop())

        # Place blinds
        self.bets[0] = self.small_blind
        self.bets[1] = self.big_blind
        self.pot = self.small_blind + self.big_blind
        self.current_bet = self.big_blind

        # Start with player after big blind
        self.current_player = 2

    def _evaluate_hand(self, hand: List[Card]) -> Tuple[PokerHandType, List[int]]:
        """Evaluate a poker hand"""
        hand = sorted(hand, key=lambda x: x.value)

        # Count ranks and suits
        rank_counts = defaultdict(int)
        suit_counts = defaultdict(int)
        for card in hand:
            rank_counts[card.rank] += 1
            suit_counts[card.suit] += 1

        # Check for straight
        straight = False
        straight_high = None
        values = sorted([card.value for card in hand])
        if len(set(values)) == 5 and values[4] - values[0] == 4:
            straight = True
            straight_high = values[4]
        elif set(values) == {14, 2, 3, 4, 5}:
            straight = True
            straight_high = 5

        # Check for flush
        flush = any(count >= 5 for count in suit_counts.values())

        # Get rank counts
        rank_counts = sorted(rank_counts.items(), key=lambda x: x[1], reverse=True)

        # Determine hand type
        if straight and flush:
            if straight_high == 14:
                return PokerHandType.ROYAL_FLUSH, [14]
            return PokerHandType.STRAIGHT_FLUSH, [straight_high]

        if rank_counts[0][1] == 4:
            return PokerHandType.FOUR_OF_A_KIND, [rank_counts[0][0], rank_counts[1][0]]

        if rank_counts[0][1] == 3 and rank_counts[1][1] == 2:
            return PokerHandType.FULL_HOUSE, [rank_counts[0][0], rank_counts[1][0]]

        if flush:
            return PokerHandType.FLUSH, [card.value for card in reversed(hand)]

        if straight:
            return PokerHandType.STRAIGHT, [straight_high]

        if rank_counts[0][1] == 3:
            return PokerHandType.THREE_OF_A_KIND, [rank_counts[0][0]] + [
                card.value for card in reversed(hand) if card.rank != rank_counts[0][0]
            ]

        if rank_counts[0][1] == 2 and rank_counts[1][1] == 2:
            return PokerHandType.TWO_PAIR, [
                rank_counts[0][0],
                rank_counts[1][0],
                rank_counts[2][0],
            ]

        if rank_counts[0][1] == 2:
            return PokerHandType.PAIR, [rank_counts[0][0]] + [
                card.value for card in reversed(hand) if card.rank != rank_counts[0][0]
            ]

        return PokerHandType.HIGH_CARD, [card.value for card in reversed(hand)]

    def _get_best_hand(self, player: int) -> Tuple[PokerHandType, List[int]]:
        """Get the best possible hand for a player"""
        all_cards = self.hands[player] + self.community_cards
        best_hand = (PokerHandType.HIGH_CARD, [0])

        # Try all combinations of 5 cards
        for i in range(len(all_cards)):
            for j in range(i + 1, len(all_cards)):
                for k in range(j + 1, len(all_cards)):
                    for l in range(k + 1, len(all_cards)):
                        for m in range(l + 1, len(all_cards)):
                            hand = [
                                all_cards[i],
                                all_cards[j],
                                all_cards[k],
                                all_cards[l],
                                all_cards[m],
                            ]
                            evaluation = self._evaluate_hand(hand)
                            if evaluation[0].value > best_hand[0].value:
                                best_hand = evaluation
                            elif evaluation[0].value == best_hand[0].value:
                                if evaluation[1] > best_hand[1]:
                                    best_hand = evaluation

        return best_hand

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if "action" not in move_data:
            return False

        action = move_data["action"]

        if action == PokerAction.FOLD.name:
            return True

        if action == PokerAction.CHECK.name:
            return self.current_bet == self.bets[self.current_player]

        if action == PokerAction.CALL.name:
            return self.current_bet > self.bets[self.current_player]

        if action == PokerAction.BET.name:
            if "amount" not in move_data:
                return False
            amount = move_data["amount"]
            return amount >= self.big_blind

        if action == PokerAction.RAISE.name:
            if "amount" not in move_data:
                return False
            amount = move_data["amount"]
            return amount > self.current_bet

        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        action = move_data["action"]

        if action == PokerAction.FOLD.name:
            self.hands[self.current_player] = []

        elif action == PokerAction.CHECK.name:
            pass

        elif action == PokerAction.CALL.name:
            amount = self.current_bet - self.bets[self.current_player]
            self.bets[self.current_player] += amount
            self.pot += amount

        elif action == PokerAction.BET.name:
            amount = move_data["amount"]
            self.bets[self.current_player] += amount
            self.pot += amount
            self.current_bet = amount

        elif action == PokerAction.RAISE.name:
            amount = move_data["amount"]
            self.bets[self.current_player] += amount
            self.pot += amount
            self.current_bet = amount

        # Move to next player
        self.current_player = (self.current_player + 1) % self.num_players

        # Check if round is complete
        if all(
            self.bets[i] == self.current_bet
            for i in range(self.num_players)
            if self.hands[i]
        ):
            self._advance_round()

        return self.get_game_state()

    def _advance_round(self):
        """Advance to the next round of betting"""
        self.round += 1
        self.current_bet = 0
        self.bets = defaultdict(int)

        if self.round == 1:
            # Flop
            self.community_cards.extend([self.deck.pop() for _ in range(3)])
        elif self.round == 2:
            # Turn
            self.community_cards.append(self.deck.pop())
        elif self.round == 3:
            # River
            self.community_cards.append(self.deck.pop())
        elif self.round == 4:
            # Showdown
            self._determine_winner()

        # Reset to first player after big blind
        self.current_player = 2

    def _determine_winner(self):
        """Determine the winner of the round"""
        active_players = [i for i in range(self.num_players) if self.hands[i]]
        if len(active_players) == 1:
            self.scores[active_players[0]] += self.pot
            return

        # Evaluate hands
        best_hand = (PokerHandType.HIGH_CARD, [0])
        winners = []

        for player in active_players:
            hand = self._get_best_hand(player)
            if hand[0].value > best_hand[0].value:
                best_hand = hand
                winners = [player]
            elif hand[0].value == best_hand[0].value and hand[1] > best_hand[1]:
                best_hand = hand
                winners = [player]
            elif hand[0].value == best_hand[0].value and hand[1] == best_hand[1]:
                winners.append(player)

        # Split pot
        pot_per_winner = self.pot // len(winners)
        for winner in winners:
            self.scores[winner] += pot_per_winner

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "hands": {
                str(k): [card.to_dict() for card in v] for k, v in self.hands.items()
            },
            "community_cards": [card.to_dict() for card in self.community_cards],
            "current_player": self.current_player,
            "pot": self.pot,
            "bets": self.bets,
            "current_bet": self.current_bet,
            "round": self.round,
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.round == 4 and all(
            self.bets[i] == self.current_bet
            for i in range(self.num_players)
            if self.hands[i]
        )

    def get_winner(self) -> Optional[int]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None

        active_players = [i for i in range(self.num_players) if self.hands[i]]
        if len(active_players) == 1:
            return active_players[0]

        # Evaluate hands
        best_hand = (PokerHandType.HIGH_CARD, [0])
        winners = []

        for player in active_players:
            hand = self._get_best_hand(player)
            if hand[0].value > best_hand[0].value:
                best_hand = hand
                winners = [player]
            elif hand[0].value == best_hand[0].value and hand[1] > best_hand[1]:
                best_hand = hand
                winners = [player]
            elif hand[0].value == best_hand[0].value and hand[1] == best_hand[1]:
                winners.append(player)

        return winners[0] if len(winners) == 1 else None
