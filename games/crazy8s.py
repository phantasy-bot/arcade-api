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
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
            '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
        suit_order = {'♣': 0, '♦': 1, '♥': 2, '♠': 3}
        return rank_order[self.rank] * 4 + suit_order[self.suit]

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash((self.suit, self.rank))

    def to_dict(self) -> Dict[str, str]:
        return {'suit': self.suit, 'rank': self.rank}

class CrazyEightsGame(AbstractGame):
    def __init__(self, game_id: str, num_players: int = 4):
        super().__init__(game_id)
        self.num_players = num_players
        self.current_player = 0
        self.hands = defaultdict(list)
        self.deck = []
        self.discard_pile = []
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.hands = defaultdict(list)
        self.current_player = 0
        self.deck = []
        self.discard_pile = []
        
        # Create deck
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.deck)
        
        # Deal cards (5 cards to each player)
        for i in range(self.num_players):
            for _ in range(5):
                self.hands[i].append(self.deck.pop())
        
        # Place first card on discard pile
        self.discard_pile.append(self.deck.pop())
        
    def _is_valid_play(self, card: Card) -> bool:
        """Check if a card can be played on the discard pile"""
        if not self.discard_pile:
            return True
            
        top_card = self.discard_pile[-1]
        
        # Can always play an 8
        if card.rank == '8':
            return True
            
        # Must match suit or rank
        return (card.suit == top_card.suit or 
                card.rank == top_card.rank)

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'action' not in move_data:
            return False
            
        action = move_data['action']
        
        if action == 'play':
            if 'card' not in move_data:
                return False
                
            card = Card(move_data['card']['suit'], move_data['card']['rank'])
            if card not in self.hands[self.current_player]:
                return False
                
            return self._is_valid_play(card)
            
        elif action == 'draw':
            return True
            
        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        action = move_data['action']
        
        if action == 'play':
            card = Card(move_data['card']['suit'], move_data['card']['rank'])
            self.hands[self.current_player].remove(card)
            self.discard_pile.append(card)
            
            # If playing an 8, allow suit change
            if card.rank == '8' and 'new_suit' in move_data:
                self.discard_pile[-1].suit = move_data['new_suit']
                
        elif action == 'draw':
            if not self.deck:
                # Shuffle discard pile (except top card) back into deck
                self.deck = self.discard_pile[:-1]
                random.shuffle(self.deck)
                self.discard_pile = [self.discard_pile[-1]]
                
            self.hands[self.current_player].append(self.deck.pop())
            
        # Move to next player
        self.current_player = (self.current_player + 1) % self.num_players
        
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'hands': {str(k): [card.to_dict() for card in v] for k, v in self.hands.items()},
            'current_player': self.current_player,
            'discard_pile_top': self.discard_pile[-1].to_dict() if self.discard_pile else None,
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
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
