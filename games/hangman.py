from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict

class HangmanGame(AbstractGame):
    def __init__(self, game_id: str, word_list: Optional[List[str]] = None):
        super().__init__(game_id)
        self.word_list = word_list or self._get_default_word_list()
        self.current_word = ""
        self.guesses = set()
        self.incorrect_guesses = set()
        self.max_incorrect = 6
        self.phase = "setup"  # setup, play, end
        self._init_game()

    def _get_default_word_list(self) -> List[str]:
        """Get default word list"""
        return [
            "python", "hangman", "computer", "programming", "developer",
            "algorithm", "variable", "function", "class", "object",
            "inheritance", "polymorphism", "encapsulation", "abstraction",
            "interface", "implementation", "framework", "library", "package",
            "module", "dictionary", "list", "tuple", "set"
        ]

    def _init_game(self):
        """Initialize a new game"""
        self.phase = "setup"
        self.guesses = set()
        self.incorrect_guesses = set()
        
        # Choose a random word
        self.current_word = random.choice(self.word_list).lower()
        
        # Make sure word doesn't have duplicate letters
        while len(set(self.current_word)) != len(self.current_word):
            self.current_word = random.choice(self.word_list).lower()

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'action' not in move_data:
            return False
            
        action = move_data['action']
        
        if action == "guess":
            if 'letter' not in move_data:
                return False
                
            letter = move_data['letter'].lower()
            
            # Check if valid letter
            if not letter.isalpha() or len(letter) != 1:
                return False
                
            # Check if letter hasn't been guessed
            if letter in self.guesses:
                return False
                
            return True
            
        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        action = move_data['action']
        letter = move_data['letter'].lower()
        
        if action == "guess":
            self.guesses.add(letter)
            
            # Check if letter is in word
            if letter in self.current_word:
                # Check if word is solved
                if all(c in self.guesses for c in self.current_word):
                    self.phase = "end"
            else:
                self.incorrect_guesses.add(letter)
                
                # Check if too many incorrect guesses
                if len(self.incorrect_guesses) >= self.max_incorrect:
                    self.phase = "end"
            
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        # Create masked word
        masked_word = ''.join(
            c if c in self.guesses else '_' 
            for c in self.current_word
        )
        
        return {
            'current_word': masked_word,
            'guesses': list(self.guesses),
            'incorrect_guesses': list(self.incorrect_guesses),
            'max_incorrect': self.max_incorrect,
            'phase': self.phase,
            'game_over': self.phase == "end",
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.phase == "end"

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None
            
        # Player wins if word is solved
        if all(c in self.guesses for c in self.current_word):
            return "player"
            
        # Computer wins if too many incorrect guesses
        return "computer"
