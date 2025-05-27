from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict

class Card:
    def __init__(self, value: str, is_face_up: bool = False):
        self.value = value
        self.is_face_up = is_face_up

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value,
            'is_face_up': self.is_face_up
        }

class ConcentrationGame(AbstractGame):
    def __init__(self, game_id: str, board_size: int = 4):
        super().__init__(game_id)
        self.board_size = board_size
        self.current_player = 0
        self.board = []
        self.flipped_cards = set()
        self.matches = set()
        self.scores = defaultdict(int)
        self.phase = "setup"  # setup, play, end
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.current_player = 0
        self.phase = "setup"
        self.board = []
        self.flipped_cards = set()
        self.matches = set()
        self.scores = defaultdict(int)
        
        # Create pairs of cards
        values = list(range(1, (self.board_size * self.board_size) // 2 + 1))
        cards = values + values
        random.shuffle(cards)
        
        # Create board
        self.board = [[Card(str(cards[i * self.board_size + j])) 
                      for j in range(self.board_size)]
                      for i in range(self.board_size)]

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'action' not in move_data:
            return False
            
        action = move_data['action']
        
        if action == "flip":
            if 'position' not in move_data:
                return False
                
            x, y = move_data['position']
            
            # Check if position is valid
            if not (0 <= x < self.board_size and 0 <= y < self.board_size):
                return False
                
            # Check if card is already matched
            if (x, y) in self.matches:
                return False
                
            # Check if card is already flipped
            if (x, y) in self.flipped_cards:
                return False
                
            # Check if we have more than 2 flipped cards
            if len(self.flipped_cards) >= 2:
                return False
                
            return True
            
        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        action = move_data['action']
        x, y = move_data['position']
        
        if action == "flip":
            # Flip the card
            self.board[x][y].is_face_up = True
            self.flipped_cards.add((x, y))
            
            # If this is the second card flipped
            if len(self.flipped_cards) == 2:
                # Check if they match
                card1 = self.board[self.flipped_cards.pop()]
                card2 = self.board[(x, y)]
                
                if card1.value == card2.value:
                    # Match found!
                    self.matches.add((x, y))
                    self.matches.add(self.flipped_cards.pop())
                    self.scores[self.current_player] += 1
                    
                    # Check if game is over
                    if len(self.matches) == (self.board_size * self.board_size) // 2:
                        self.phase = "end"
                else:
                    # No match, flip cards back
                    card1.is_face_up = False
                    card2.is_face_up = False
                    
                # Move to next player
                self.current_player = (self.current_player + 1) % 2
            
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board': [[card.to_dict() for card in row] for row in self.board],
            'current_player': self.current_player,
            'phase': self.phase,
            'flipped_cards': list(self.flipped_cards),
            'matches': list(self.matches),
            'scores': self.scores,
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
            
        # Player with most matches wins
        return max(self.scores.items(), key=lambda x: x[1])[0]
