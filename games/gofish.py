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
        return {'suit': self.suit, 'rank': self.rank}

class GoFishGame(AbstractGame):
    def __init__(self, game_id: str, num_players: int = 4):
        super().__init__(game_id)
        self.num_players = num_players
        self.current_player = 0
        self.deck = []
        self.hands = defaultdict(list)
        self.fish_pile = []
        self.book_count = defaultdict(int)
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.deck = []
        self.hands = defaultdict(list)
        self.fish_pile = []
        self.book_count = defaultdict(int)
        self.current_player = 0
        
        # Create deck (4 suits, ranks 1-13)
        suits = ['♠', '♥', '♦', '♣']
        for suit in suits:
            for rank in range(1, 14):
                self.deck.append(Card(suit, rank))
        random.shuffle(self.deck)
        
        # Deal initial cards
        for i in range(self.num_players):
            self.hands[i] = [self.deck.pop() for _ in range(7)]
            self._check_books(i)
            
        # Place remaining cards in fish pile
        self.fish_pile = self.deck

    def _check_books(self, player: int) -> None:
        """Check player's hand for books (4 of a kind)"""
        if player not in self.hands:
            return
            
        hand = self.hands[player]
        counts = defaultdict(int)
        
        # Count cards
        for card in hand:
            counts[card.rank] += 1
            
        # Find books
        books = [rank for rank, count in counts.items() if count == 4]
        if not books:
            return
            
        # Remove books from hand
        for rank in books:
            self.book_count[player] += 1
            self.hands[player] = [card for card in hand if card.rank != rank]
            
        # Draw cards to replace books
        while len(self.hands[player]) < 7 and self.fish_pile:
            self.hands[player].append(self.fish_pile.pop())

    def _has_rank(self, player: int, rank: int) -> bool:
        """Check if player has cards of the given rank"""
        return any(card.rank == rank for card in self.hands[player])

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'target_player' not in move_data or 'rank' not in move_data:
            return False
            
        target_player = move_data['target_player']
        rank = move_data['rank']
        
        # Check if target player is valid
        if target_player < 0 or target_player >= self.num_players or target_player == self.current_player:
            return False
            
        # Check if player has the rank in their hand
        if not self._has_rank(self.current_player, rank):
            return False
            
        return True

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        target_player = move_data['target_player']
        rank = move_data['rank']
        
        # Check if target player has the rank
        if self._has_rank(target_player, rank):
            # Take cards from target player
            self.hands[target_player] = [card for card in self.hands[target_player] if card.rank != rank]
            self.hands[self.current_player] = [card for card in self.hands[self.current_player] 
                                             if card.rank != rank]
            
            # Add cards to current player's hand
            self.hands[self.current_player].extend(
                card for card in self.hands[target_player] if card.rank == rank
            )
            
            # Check for books
            self._check_books(self.current_player)
            
            # Player gets another turn
            return self.get_game_state()
            
        else:
            # Go fish
            if self.fish_pile:
                self.hands[self.current_player].append(self.fish_pile.pop())
                self._check_books(self.current_player)
            
            # Move to next player
            self.current_player = (self.current_player + 1) % self.num_players
            
            return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'hands': {str(k): [card.to_dict() for card in v] for k, v in self.hands.items()},
            'current_player': self.current_player,
            'fish_pile_size': len(self.fish_pile),
            'book_count': dict(self.book_count),
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return not self.fish_pile and all(not self.hands[i] for i in range(self.num_players))

    def get_winner(self) -> Optional[int]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None
            
        max_books = max(self.book_count.values())
        winners = [player for player, count in self.book_count.items() if count == max_books]
        
        if len(winners) == 1:
            return winners[0]
        return None  # Draw if multiple players have same number of books
