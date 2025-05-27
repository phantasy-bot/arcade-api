from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict

class Card:
    def __init__(self, type: str, value: int = 1):
        self.type = type
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'value': self.value
        }

class JaipurGame(AbstractGame):
    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.current_player = 0
        self.camel_count = 0
        self.market = []
        self.camel_market = []
        self.players = [{}, {}]  # player 0 and player 1
        self.camel_herd = []
        self.tokens = defaultdict(list)
        self.phase = "setup"  # setup, play, end
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.current_player = 0
        self.phase = "setup"
        self.camel_count = 0
        self.market = []
        self.camel_market = []
        self.players = [{}, {}]
        self.camel_herd = []
        self.tokens = defaultdict(list)
        
        # Initialize tokens
        token_values = [1, 2, 3, 4, 5, 7]
        for good in ['diamond', 'gold', 'silver', 'cloth', 'spice']:
            self.tokens[good] = token_values[:]
        self.tokens['camel'] = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5]
        
        # Create deck
        goods = {
            'diamond': 6,
            'gold': 6,
            'silver': 6,
            'cloth': 8,
            'spice': 8,
            'camel': 11
        }
        
        deck = []
        for good, count in goods.items():
            deck.extend([Card(good) for _ in range(count)])
        
        random.shuffle(deck)
        
        # Deal cards
        for _ in range(5):
            self.players[0][deck.pop().type] = self.players[0].get(deck.pop().type, 0) + 1
            self.players[1][deck.pop().type] = self.players[1].get(deck.pop().type, 0) + 1
            
        # Place camels in market
        while deck[-1].type == 'camel':
            self.camel_herd.append(deck.pop())
        
        # Place initial market cards
        for _ in range(5):
            card = deck.pop()
            if card.type == 'camel':
                self.camel_market.append(card)
            else:
                self.market.append(card)
        
        self.deck = deck

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'action' not in move_data:
            return False
            
        action = move_data['action']
        player = self.players[self.current_player]
        
        if action == "take":
            if 'card' not in move_data:
                return False
                
            card_type = move_data['card']
            
            # Check if card exists in market
            if card_type not in [card.type for card in self.market]:
                return False
                
            # Check if player can take card
            if card_type == 'camel':
                return True
                
            # Check if player has room for card
            if sum(player.values()) >= 7:
                return False
                
            # Check if taking multiple cards of same type
            if len([c for c in self.market if c.type == card_type]) > 1:
                return True
                
            return False
            
        elif action == "sell":
            if 'type' not in move_data:
                return False
                
            good_type = move_data['type']
            
            # Check if player has enough cards to sell
            if player.get(good_type, 0) < 2:
                return False
                
            # Check if tokens are available
            if not self.tokens[good_type]:
                return False
                
            return True
            
        elif action == "exchange":
            if 'give' not in move_data or 'take' not in move_data:
                return False
                
            give = move_data['give']
            take = move_data['take']
            
            # Check if player has cards to give
            if not all(player.get(card.type, 0) >= 1 for card in give):
                return False
                
            # Check if taking cards from market
            if not all(card.type in [c.type for c in self.market] for card in take):
                return False
                
            # Check if number of cards matches
            if len(give) != len(take):
                return False
                
            return True
            
        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        action = move_data['action']
        player = self.players[self.current_player]
        
        if action == "take":
            card_type = move_data['card']
            
            # Find card in market
            card = next(card for card in self.market if card.type == card_type)
            self.market.remove(card)
            
            # Add card to player's hand
            player[card_type] = player.get(card_type, 0) + 1
            
            # Take all camels if taking a camel
            if card_type == 'camel':
                player['camel'] = player.get('camel', 0) + len(self.camel_market)
                self.camel_market.clear()
            
            # Draw new card from deck
            if self.deck:
                new_card = self.deck.pop()
                if new_card.type == 'camel':
                    self.camel_market.append(new_card)
                else:
                    self.market.append(new_card)
            
        elif action == "sell":
            good_type = move_data['type']
            
            # Calculate bonus tokens
            bonus = 0
            if good_type == 'diamond' and player[good_type] >= 3:
                bonus = 5
            elif good_type == 'gold' and player[good_type] >= 3:
                bonus = 3
            elif good_type == 'silver' and player[good_type] >= 3:
                bonus = 2
            
            # Take tokens
            tokens_taken = self.tokens[good_type][-player[good_type]:]
            del self.tokens[good_type][-player[good_type]:]
            
            # Remove cards from player's hand
            player[good_type] = 0
            
        elif action == "exchange":
            give = move_data['give']
            take = move_data['take']
            
            # Remove cards from player's hand
            for card in give:
                player[card.type] -= 1
            
            # Add cards to player's hand
            for card in take:
                player[card.type] = player.get(card.type, 0) + 1
                self.market.remove(card)
            
            # Draw new cards from deck
            for _ in range(len(take)):
                if self.deck:
                    new_card = self.deck.pop()
                    if new_card.type == 'camel':
                        self.camel_market.append(new_card)
                    else:
                        self.market.append(new_card)
            
        # Move to next player
        self.current_player = 1 - self.current_player
        
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'current_player': self.current_player,
            'phase': self.phase,
            'market': [card.to_dict() for card in self.market],
            'camel_market': [card.to_dict() for card in self.camel_market],
            'camel_herd': [card.to_dict() for card in self.camel_herd],
            'players': [
                {k: v for k, v in player.items() if v > 0}
                for player in self.players
            ],
            'tokens': {k: [t for t in v] for k, v in self.tokens.items()},
            'game_over': self.phase == "end",
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        # Game ends when any of these conditions are met:
        # 1. All diamond tokens are taken
        # 2. All gold tokens are taken
        # 3. All silver tokens are taken
        # 4. Market is empty
        return (not self.tokens['diamond'] or
                not self.tokens['gold'] or
                not self.tokens['silver'] or
                not self.market)

    def get_winner(self) -> Optional[int]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None
            
        # Calculate scores
        scores = [0, 0]
        for i in range(2):
            # Goods score
            for good, count in self.players[i].items():
                if good != 'camel':
                    scores[i] += sum(self.tokens[good][-count:])
            
            # Camel bonus
            if self.players[i].get('camel', 0) > self.players[1 - i].get('camel', 0):
                scores[i] += 5
            
        # Return player with highest score
        return 0 if scores[0] > scores[1] else 1
