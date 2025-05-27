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
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'suit': self.suit,
            'rank': self.rank
        }

class GinRummyGame(AbstractGame):
    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.current_player = 0
        self.deck = []
        self.discard_pile = []
        self.hands = defaultdict(list)
        self.deadwood = defaultdict(int)
        self.phase = "setup"  # setup, play, end
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.current_player = 0
        self.phase = "setup"
        self.deck = []
        self.discard_pile = []
        self.hands = defaultdict(list)
        self.deadwood = defaultdict(int)
        
        # Create deck (52 cards)
        suits = ['♠', '♥', '♦', '♣']
        for suit in suits:
            for rank in range(1, 14):
                self.deck.append(Card(suit, rank))
        
        random.shuffle(self.deck)
        
        # Deal 10 cards to each player
        for _ in range(10):
            self.hands[0].append(self.deck.pop())
            self.hands[1].append(self.deck.pop())
        
        # Place first card on discard pile
        self.discard_pile.append(self.deck.pop())

    def _is_meld(self, cards: List[Card]) -> bool:
        """Check if cards form a meld (set or run)"""
        if len(cards) < 3:
            return False
            
        # Check for set (same rank)
        if len(set(card.rank for card in cards)) == 1:
            return True
            
        # Check for run (consecutive ranks)
        cards = sorted(cards, key=lambda x: x.rank)
        if len(set(card.suit for card in cards)) != 1:
            return False
            
        for i in range(len(cards) - 1):
            if cards[i].rank + 1 != cards[i+1].rank:
                return False
                
        return True

    def _calculate_deadwood(self, hand: List[Card]) -> int:
        """Calculate deadwood points"""
        # Find all possible melds
        melds = []
        for i in range(len(hand)):
            for j in range(i + 1, len(hand)):
                for k in range(j + 1, len(hand)):
                    if self._is_meld([hand[i], hand[j], hand[k]]):
                        melds.append([hand[i], hand[j], hand[k]])
                        
        # Find best combination of melds
        best_deadwood = float('inf')
        for i in range(1 << len(hand)):
            used = set()
            meld_count = 0
            deadwood = 0
            
            # Count melds
            for meld in melds:
                if all(card not in used for card in meld):
                    meld_count += 1
                    used.update(meld)
                    
            # Calculate deadwood
            for card in hand:
                if card not in used:
                    deadwood += card.rank if card.rank <= 10 else 10
                    
            if meld_count >= 1 and deadwood < best_deadwood:
                best_deadwood = deadwood
                
        return best_deadwood

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'action' not in move_data:
            return False
            
        action = move_data['action']
        
        if action == "draw":
            if 'source' not in move_data:
                return False
                
            source = move_data['source']
            if source not in ["deck", "discard"]:
                return False
                
            return True
            
        elif action == "discard":
            if 'card' not in move_data:
                return False
                
            card = Card(move_data['card']['suit'], move_data['card']['rank'])
            if card not in self.hands[self.current_player]:
                return False
                
            return True
            
        elif action == "knock":
            # Check if player can knock
            self.deadwood[self.current_player] = self._calculate_deadwood(self.hands[self.current_player])
            return self.deadwood[self.current_player] <= 10
            
        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        action = move_data['action']
        
        if action == "draw":
            source = move_data['source']
            if source == "deck":
                if self.deck:
                    self.hands[self.current_player].append(self.deck.pop())
                else:
                    # Reshuffle discard pile except top card
                    self.deck = self.discard_pile[:-1]
                    random.shuffle(self.deck)
                    self.hands[self.current_player].append(self.deck.pop())
            else:  # discard
                self.hands[self.current_player].append(self.discard_pile.pop())
                
        elif action == "discard":
            card = Card(move_data['card']['suit'], move_data['card']['rank'])
            self.hands[self.current_player].remove(card)
            self.discard_pile.append(card)
            
        elif action == "knock":
            # Calculate scores
            self.deadwood[self.current_player] = self._calculate_deadwood(self.hands[self.current_player])
            opponent = 1 - self.current_player
            self.deadwood[opponent] = self._calculate_deadwood(self.hands[opponent])
            
            # Check if knock is valid
            if self.deadwood[self.current_player] <= self.deadwood[opponent]:
                self.phase = "end"
            else:
                # Undercut - opponent wins
                self.phase = "end"
                
        # Move to next player unless game is over
        if self.phase != "end":
            self.current_player = 1 - self.current_player
            
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'current_player': self.current_player,
            'phase': self.phase,
            'hands': {str(k): [card.to_dict() for card in v] for k, v in self.hands.items()},
            'discard_pile': [card.to_dict() for card in self.discard_pile],
            'deadwood': self.deadwood,
            'game_over': self.phase == "end",
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.phase == "end"

    def get_winner(self) -> Optional[int]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None
            
        # Player with lower deadwood wins
        if self.deadwood[0] <= self.deadwood[1]:
            return 0
        return 1
