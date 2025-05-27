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
            '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7,
            '10': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12, '2': 13,
            'joker': 14, 'Joker': 15
        }
        return rank_order[self.rank]

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash((self.suit, self.rank))

    def to_dict(self) -> Dict[str, str]:
        return {'suit': self.suit, 'rank': self.rank}

class CardType(Enum):
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    STRAIGHT = 4
    FULL_HOUSE = 5
    FOUR_OF_A_KIND = 6
    STRAIGHT_FLUSH = 7

class TienLenGame(AbstractGame):
    def __init__(self, game_id: str, num_players: int = 4):
        super().__init__(game_id)
        self.num_players = num_players
        self.current_player = 0
        self.hands = defaultdict(list)
        self.last_play = None
        self.last_player = None
        self.active_players = set(range(num_players))
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.hands = defaultdict(list)
        self.current_player = 0
        self.last_play = None
        self.last_player = None
        self.active_players = set(range(self.num_players))
        
        # Create deck
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
        deck = [Card(suit, rank) for suit in suits for rank in ranks]
        deck.append(Card('', 'joker'))  # Small joker
        deck.append(Card('', 'Joker'))  # Big joker
        random.shuffle(deck)
        
        # Deal cards
        for i, card in enumerate(deck):
            self.hands[i % self.num_players].append(card)

    def _get_card_type(self, cards: List[Card]) -> Optional[Tuple[CardType, int]]:
        """Determine the type of card combination"""
        if not cards:
            return None
            
        cards.sort()
        count = len(cards)
        
        # Check for special cases
        if count == 1:
            return CardType.SINGLE, cards[0].value
        if count == 2 and cards[0].rank == cards[1].rank:
            return CardType.PAIR, cards[0].value
        if count == 3 and cards[0].rank == cards[1].rank == cards[2].rank:
            return CardType.TRIPLE, cards[0].value
        if count == 4 and cards[0].rank == cards[1].rank == cards[2].rank == cards[3].rank:
            return CardType.FOUR_OF_A_KIND, cards[0].value
            
        # Check for straight
        if count >= 3:
            straight = True
            for i in range(1, count):
                if cards[i].value != cards[i-1].value + 1:
                    straight = False
                    break
            if straight:
                return CardType.STRAIGHT, cards[0].value
                
        # Check for full house
        if count == 5:
            counts = defaultdict(int)
            for card in cards:
                counts[card.rank] += 1
            values = list(counts.values())
            if sorted(values) == [2, 3]:
                return CardType.FULL_HOUSE, max(cards[0].value, cards[1].value)
                
        # Check for straight flush
        if count >= 3:
            straight = True
            flush = True
            for i in range(1, count):
                if cards[i].value != cards[i-1].value + 1:
                    straight = False
                if cards[i].suit != cards[0].suit:
                    flush = False
            if straight and flush:
                return CardType.STRAIGHT_FLUSH, cards[0].value
                
        return None

    def _is_valid_play(self, cards: List[Card]) -> bool:
        """Check if a play is valid"""
        if not cards:
            return False
            
        # First play must be 3 of spades
        if self.last_play is None:
            return cards[0].rank == '3' and cards[0].suit == '♠'
            
        # Check card combination type
        card_type = self._get_card_type(cards)
        if not card_type:
            return False
            
        # Check if it beats last play
        if self.last_play:
            last_type = self._get_card_type(self.last_play)
            if card_type[0] != last_type[0]:
                return False
            if card_type[1] <= last_type[1]:
                return False
                
        return True

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'cards' not in move_data:
            return False
            
        cards = [Card(card['suit'], card['rank']) for card in move_data['cards']]
        player_hand = self.hands[self.current_player]
        
        # Check if player has these cards
        if not all(card in player_hand for card in cards):
            return False
            
        return self._is_valid_play(cards)

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        cards = [Card(card['suit'], card['rank']) for card in move_data['cards']]
        player_hand = self.hands[self.current_player]
        
        # Remove cards from player's hand
        for card in cards:
            player_hand.remove(card)
            
        # Update game state
        self.last_play = cards
        self.last_player = self.current_player
        
        # Check if player has finished
        if not player_hand:
            self.active_players.remove(self.current_player)
            
        # Move to next player
        if self.last_play is None:
            # First play, go to next player
            self.current_player = (self.current_player + 1) % self.num_players
        else:
            # Find next player who can play
            found = False
            while not found:
                self.current_player = (self.current_player + 1) % self.num_players
                if self.current_player in self.active_players:
                    found = True
                    
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'hands': {str(k): [card.to_dict() for card in v] for k, v in self.hands.items()},
            'current_player': self.current_player,
            'last_play': [card.to_dict() for card in self.last_play] if self.last_play else None,
            'last_player': self.last_player,
            'active_players': list(self.active_players),
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return len(self.active_players) <= 1

    def get_winner(self) -> Optional[int]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None
            
        # First player to finish wins
        for i in range(self.num_players):
            if i in self.active_players:
                return i
        return None
