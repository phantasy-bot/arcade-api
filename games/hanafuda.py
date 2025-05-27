from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict

class HanafudaCard:
    def __init__(self, month: int, rank: str, points: int, suit: str):
        self.month = month
        self.rank = rank
        self.points = points
        self.suit = suit
        self.value = self._get_card_value()

    def _get_card_value(self) -> int:
        """Get the card's value for comparison"""
        return self.month * 100 + self.points

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash((self.month, self.rank, self.points, self.suit))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'month': self.month,
            'rank': self.rank,
            'points': self.points,
            'suit': self.suit
        }

class HanafudaGame(AbstractGame):
    def __init__(self, game_id: str, num_players: int = 2):
        super().__init__(game_id)
        self.num_players = num_players
        self.current_player = 0
        self.hands = defaultdict(list)
        self.deck = []
        self.field = []
        self.scores = defaultdict(int)
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.hands = defaultdict(list)
        self.current_player = 0
        self.deck = []
        self.field = []
        self.scores = defaultdict(int)
        
        # Create deck (48 Hanafuda cards)
        hanafuda_cards = [
            # Bright cards (20 points)
            HanafudaCard(1, "Pine", 20, "Bright"),  # January
            HanafudaCard(2, "Plum", 20, "Bright"), # February
            HanafudaCard(3, "Cherry", 20, "Bright"), # March
            HanafudaCard(4, "Wisteria", 20, "Bright"), # April
            HanafudaCard(5, "Iris", 20, "Bright"), # May
            HanafudaCard(6, "Peony", 20, "Bright"), # June
            HanafudaCard(7, "Bush Clover", 20, "Bright"), # July
            HanafudaCard(8, "Autumn Grass", 20, "Bright"), # August
            HanafudaCard(9, "Chrysanthemum", 20, "Bright"), # September
            HanafudaCard(10, "Maple", 20, "Bright"), # October
            HanafudaCard(11, "Willow", 20, "Bright"), # November
            HanafudaCard(12, "Paulownia", 20, "Bright"), # December
            
            # Animals (10 points)
            HanafudaCard(1, "Crane", 10, "Animal"),
            HanafudaCard(2, "Nightingale", 10, "Animal"),
            HanafudaCard(3, "Kite", 10, "Animal"),
            HanafudaCard(4, "Cuckoo", 10, "Animal"),
            HanafudaCard(5, "Butterfly", 10, "Animal"),
            HanafudaCard(6, "Boar", 10, "Animal"),
            HanafudaCard(7, "Mandarin Duck", 10, "Animal"),
            HanafudaCard(8, "Geese", 10, "Animal"),
            HanafudaCard(9, "Swallow", 10, "Animal"),
            HanafudaCard(10, "Deer", 10, "Animal"),
            HanafudaCard(11, "Wild Goose", 10, "Animal"),
            HanafudaCard(12, "Pheasant", 10, "Animal"),
            
            # Ribbons (5 points)
            HanafudaCard(1, "Red Ribbon", 5, "Ribbon"),
            HanafudaCard(2, "Blue Ribbon", 5, "Ribbon"),
            HanafudaCard(3, "Purple Ribbon", 5, "Ribbon"),
            HanafudaCard(4, "Green Ribbon", 5, "Ribbon"),
            HanafudaCard(5, "Yellow Ribbon", 5, "Ribbon"),
            HanafudaCard(6, "Red Ribbon", 5, "Ribbon"),
            HanafudaCard(7, "Blue Ribbon", 5, "Ribbon"),
            HanafudaCard(8, "Purple Ribbon", 5, "Ribbon"),
            HanafudaCard(9, "Green Ribbon", 5, "Ribbon"),
            HanafudaCard(10, "Yellow Ribbon", 5, "Ribbon"),
            HanafudaCard(11, "Red Ribbon", 5, "Ribbon"),
            HanafudaCard(12, "Blue Ribbon", 5, "Ribbon"),
            
            # Plain cards (1 point)
            HanafudaCard(1, "Plain", 1, "Plain"),
            HanafudaCard(2, "Plain", 1, "Plain"),
            HanafudaCard(3, "Plain", 1, "Plain"),
            HanafudaCard(4, "Plain", 1, "Plain"),
            HanafudaCard(5, "Plain", 1, "Plain"),
            HanafudaCard(6, "Plain", 1, "Plain"),
            HanafudaCard(7, "Plain", 1, "Plain"),
            HanafudaCard(8, "Plain", 1, "Plain"),
            HanafudaCard(9, "Plain", 1, "Plain"),
            HanafudaCard(10, "Plain", 1, "Plain"),
            HanafudaCard(11, "Plain", 1, "Plain"),
            HanafudaCard(12, "Plain", 1, "Plain")
        ]
        
        # Shuffle deck
        random.shuffle(hanafuda_cards)
        self.deck = hanafuda_cards
        
        # Deal cards (8 cards to each player)
        for i in range(self.num_players):
            for _ in range(8):
                self.hands[i].append(self.deck.pop())
        
        # Place 8 cards on the field
        for _ in range(8):
            self.field.append(self.deck.pop())

    def _can_capture(self, card1: HanafudaCard, card2: HanafudaCard) -> bool:
        """Check if card1 can capture card2"""
        # Same month capture
        if card1.month == card2.month:
            return True
            
        # Bright card capture
        if card1.suit == "Bright" and card2.points == 1:
            return True
            
        # Animal capture
        if card1.suit == "Animal" and card2.suit == "Animal" and card1.month == card2.month:
            return True
            
        # Ribbon capture
        if card1.suit == "Ribbon" and card2.suit == "Ribbon" and card1.month == card2.month:
            return True
            
        return False

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'action' not in move_data:
            return False
            
        action = move_data['action']
        
        if action == 'play':
            if 'card' not in move_data:
                return False
                
            card = HanafudaCard(
                move_data['card']['month'],
                move_data['card']['rank'],
                move_data['card']['points'],
                move_data['card']['suit']
            )
            if card not in self.hands[self.current_player]:
                return False
                
            # Check if we can capture any field cards
            if any(self._can_capture(card, field_card) for field_card in self.field):
                return True
                
            # If no capture, must place on field
            return True
            
        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        action = move_data['action']
        
        if action == 'play':
            card = HanafudaCard(
                move_data['card']['month'],
                move_data['card']['rank'],
                move_data['card']['points'],
                move_data['card']['suit']
            )
            
            # Remove card from hand
            self.hands[self.current_player].remove(card)
            
            # Check for captures
            captured = []
            for field_card in self.field:
                if self._can_capture(card, field_card):
                    captured.append(field_card)
            
            # If captured cards, add to score
            if captured:
                for captured_card in captured:
                    self.scores[self.current_player] += captured_card.points
                    self.field.remove(captured_card)
                self.scores[self.current_player] += card.points
            else:
                # If no capture, place on field
                self.field.append(card)
            
        # Draw a card if possible
        if self.deck:
            self.hands[self.current_player].append(self.deck.pop())
            
        # Move to next player
        self.current_player = (self.current_player + 1) % self.num_players
        
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'hands': {str(k): [card.to_dict() for card in v] for k, v in self.hands.items()},
            'current_player': self.current_player,
            'field': [card.to_dict() for card in self.field],
            'scores': self.scores,
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return not self.deck and all(len(hand) == 0 for hand in self.hands.values())

    def get_winner(self) -> Optional[int]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None
            
        # Player with highest score wins
        return max(self.scores.items(), key=lambda x: x[1])[0]
