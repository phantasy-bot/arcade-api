from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict
import json

class Tile:
    def __init__(self, letter: str, points: int, is_blank: bool = False):
        self.letter = letter
        self.points = points
        self.is_blank = is_blank

    def to_dict(self) -> Dict[str, Any]:
        return {
            'letter': self.letter,
            'points': self.points,
            'is_blank': self.is_blank
        }

class ScrabbleGame(AbstractGame):
    def __init__(self, game_id: str, num_players: int = 2):
        super().__init__(game_id)
        self.num_players = num_players
        self.current_player = 0
        self.board = np.zeros((15, 15), dtype=object)
        self.rack = defaultdict(list)
        self.bag = []
        self.score = defaultdict(int)
        self.turns = 0
        self.phase = "setup"  # setup, play, end
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.current_player = 0
        self.phase = "setup"
        self.board = np.zeros((15, 15), dtype=object)
        self.rack = defaultdict(list)
        self.score = defaultdict(int)
        self.turns = 0
        
        # Initialize bag with tiles
        self.bag = []
        tile_distribution = {
            'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12, 'F': 2, 'G': 3,
            'H': 2, 'I': 9, 'J': 1, 'K': 1, 'L': 4, 'M': 2, 'N': 6,
            'O': 8, 'P': 2, 'Q': 1, 'R': 6, 'S': 4, 'T': 6, 'U': 4,
            'V': 2, 'W': 2, 'X': 1, 'Y': 2, 'Z': 1, 'BLANK': 2
        }
        
        # Add tiles to bag with their point values
        tile_points = {
            'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2,
            'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1,
            'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1,
            'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10, 'BLANK': 0
        }
        
        for letter, count in tile_distribution.items():
            for _ in range(count):
                self.bag.append(Tile(
                    letter if letter != 'BLANK' else '',
                    tile_points[letter],
                    letter == 'BLANK'
                ))
        
        random.shuffle(self.bag)
        
        # Give each player 7 tiles
        for player in range(self.num_players):
            self._draw_tiles(player, 7)

    def _draw_tiles(self, player: int, count: int) -> List[Tile]:
        """Draw tiles from the bag"""
        drawn = []
        for _ in range(count):
            if self.bag:
                tile = self.bag.pop()
                self.rack[player].append(tile)
                drawn.append(tile)
        return drawn

    def _calculate_word_score(self, word: List[Tuple[int, int, str]], is_first_move: bool = False) -> int:
        """Calculate the score for a word"""
        word_multiplier = 1
        word_score = 0
        
        for x, y, letter in word:
            tile = self.rack[self.current_player][0] if letter == '' else None
            points = tile.points if tile else 1
            
            # Check for special squares
            if (x, y) == (7, 7):  # Center square
                word_multiplier *= 2 if not is_first_move else 1
            
            # Calculate letter score
            word_score += points
            
        return word_score * word_multiplier

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'action' not in move_data:
            return False
            
        action = move_data['action']
        
        if action == "place_word":
            if 'word' not in move_data or 'start' not in move_data or 'direction' not in move_data:
                return False
                
            word = move_data['word']
            start = move_data['start']
            direction = move_data['direction']
            
            # Check if word is valid
            if not self._is_valid_word(word):
                return False
                
            # Check if position is valid
            if not self._is_valid_position(start, direction, word):
                return False
                
            # Check if player has the tiles
            if not self._has_tiles(word):
                return False
                
            return True
            
        elif action == "exchange":
            if 'tiles' not in move_data:
                return False
                
            tiles = move_data['tiles']
            
            # Check if player has these tiles
            if not self._has_tiles(tiles):
                return False
                
            return True
            
        return False

    def _is_valid_word(self, word: str) -> bool:
        """Check if a word is valid (simple implementation, would use dictionary in real game)"""
        return len(word) >= 2 and all(c.isalpha() or c == '' for c in word)

    def _is_valid_position(self, start: Tuple[int, int], direction: str, word: str) -> bool:
        """Check if word can be placed at the given position"""
        x, y = start
        length = len(word)
        
        if direction == "horizontal":
            # Check if word fits horizontally
            if x + length > 15:
                return False
                
            # Check if position is empty
            for i in range(length):
                if self.board[x+i][y] is not None:
                    return False
                    
            # Check if adjacent spaces are empty
            if y > 0:
                for i in range(length):
                    if self.board[x+i][y-1] is not None:
                        return False
            if y < 14:
                for i in range(length):
                    if self.board[x+i][y+1] is not None:
                        return False
                        
        else:  # vertical
            # Check if word fits vertically
            if y + length > 15:
                return False
                
            # Check if position is empty
            for i in range(length):
                if self.board[x][y+i] is not None:
                    return False
                    
            # Check if adjacent spaces are empty
            if x > 0:
                for i in range(length):
                    if self.board[x-1][y+i] is not None:
                        return False
            if x < 14:
                for i in range(length):
                    if self.board[x+1][y+i] is not None:
                        return False
                        
        return True

    def _has_tiles(self, word: str) -> bool:
        """Check if player has the required tiles"""
        required = defaultdict(int)
        for letter in word:
            if letter == '':
                continue
            required[letter.lower()] += 1
            
        available = defaultdict(int)
        for tile in self.rack[self.current_player]:
            if tile.letter:
                available[tile.letter.lower()] += 1
            else:
                available['blank'] += 1
                
        for letter, count in required.items():
            if available[letter] + available['blank'] < count:
                return False
                
        return True

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        action = move_data['action']
        
        if action == "place_word":
            word = move_data['word']
            start = move_data['start']
            direction = move_data['direction']
            
            # Place word on board
            x, y = start
            for letter in word:
                if direction == "horizontal":
                    self.board[x][y] = letter
                    x += 1
                else:
                    self.board[x][y] = letter
                    y += 1
                    
            # Calculate score
            score = self._calculate_word_score(word, self.turns == 0)
            self.score[self.current_player] += score
            
            # Remove used tiles from rack
            for letter in word:
                if letter == '':
                    continue
                    
                # Find and remove tile
                for i, tile in enumerate(self.rack[self.current_player]):
                    if tile.letter.lower() == letter.lower():
                        del self.rack[self.current_player][i]
                        break
                        
            # Draw new tiles
            self._draw_tiles(self.current_player, 7 - len(self.rack[self.current_player]))
            
            # Check if game is over
            if not self.bag and all(len(self.rack[p]) == 0 for p in range(self.num_players)):
                self.phase = "end"
                
        elif action == "exchange":
            tiles = move_data['tiles']
            
            # Remove tiles from rack
            for letter in tiles:
                for i, tile in enumerate(self.rack[self.current_player]):
                    if tile.letter.lower() == letter.lower():
                        del self.rack[self.current_player][i]
                        break
                        
            # Add tiles back to bag
            for letter in tiles:
                self.bag.append(Tile(letter, 1))
                
            # Draw new tiles
            self._draw_tiles(self.current_player, len(tiles))
            
        # Move to next player
        self.current_player = (self.current_player + 1) % self.num_players
        self.turns += 1
        
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board': [[tile.letter if tile else None for tile in row] for row in self.board],
            'current_player': self.current_player,
            'phase': self.phase,
            'rack': {str(k): [tile.to_dict() for tile in v] for k, v in self.rack.items()},
            'score': self.score,
            'turns': self.turns,
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
            
        # Player with highest score wins
        return max(self.score.items(), key=lambda x: x[1])[0]
