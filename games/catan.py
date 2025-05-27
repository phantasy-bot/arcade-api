from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict

class Resource(Enum):
    WOOD = 1
    BRICK = 2
    SHEEP = 3
    WHEAT = 4
    ORE = 5

class BuildingType(Enum):
    SETTLEMENT = 1
    CITY = 2
    ROAD = 3

class CatanGame(AbstractGame):
    def __init__(self, game_id: str, num_players: int = 4):
        super().__init__(game_id)
        self.num_players = num_players
        self.current_player = 0
        self.phase = "setup"  # setup, play, end
        self.resources = defaultdict(int)
        self.buildings = defaultdict(list)
        self.roads = defaultdict(list)
        self.dev_cards = defaultdict(int)
        self.army_size = defaultdict(int)
        self.longest_road = defaultdict(int)
        self.victory_points = defaultdict(int)
        self.board = self._init_board()
        self._init_game()

    def _init_board(self):
        """Initialize the Catan board"""
        # Create hexagonal grid
        board = {}
        
        # Resource distribution
        resources = [
            Resource.WOOD, Resource.WOOD, Resource.WOOD,
            Resource.BRICK, Resource.BRICK, Resource.BRICK,
            Resource.SHEEP, Resource.SHEEP, Resource.SHEEP, Resource.SHEEP,
            Resource.WHEAT, Resource.WHEAT, Resource.WHEAT, Resource.WHEAT,
            Resource.ORE, Resource.ORE, Resource.ORE
        ]
        
        # Number distribution
        numbers = [2, 12, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11]
        
        # Place desert
        board[(0, 0)] = {"resource": None, "number": 7}
        
        # Place remaining hexes
        hexes = [(x, y) for x in range(-2, 3) for y in range(-2, 3) if (x, y) != (0, 0)]
        random.shuffle(hexes)
        
        for hex_pos in hexes:
            board[hex_pos] = {
                "resource": resources.pop(),
                "number": numbers.pop()
            }
        
        return board

    def _init_game(self):
        """Initialize a new game"""
        self.current_player = 0
        self.phase = "setup"
        
        # Initialize player resources
        for i in range(self.num_players):
            self.resources[i] = {
                Resource.WOOD: 0,
                Resource.BRICK: 0,
                Resource.SHEEP: 0,
                Resource.WHEAT: 0,
                Resource.ORE: 0
            }
            
        # Initialize development cards
        dev_cards = [
            "knight" * 14,
            "victory_point" * 5,
            "road_building" * 2,
            "year_of_plenty" * 2,
            "monopoly" * 2
        ]
        random.shuffle(dev_cards)
        self.dev_cards = dev_cards
        
        # Initialize victory points
        self.victory_points = defaultdict(int)
        
        # Set up phase
        self._setup_phase()

    def _setup_phase(self):
        """Handle initial placement of settlements and roads"""
        # First round: clockwise
        for i in range(self.num_players):
            player = i
            # Place settlement
            self.buildings[player].append({"type": BuildingType.SETTLEMENT, "position": (0, 0)})
            # Place road
            self.roads[player].append({"position": ((0, 0), (0, 1))})
            
        # Second round: counterclockwise
        for i in range(self.num_players - 1, -1, -1):
            player = i
            # Place settlement
            self.buildings[player].append({"type": BuildingType.SETTLEMENT, "position": (1, 0)})
            # Place road
            self.roads[player].append({"position": ((1, 0), (1, 1))})

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'action' not in move_data:
            return False
            
        action = move_data['action']
        
        if action == "build":
            if 'type' not in move_data or 'position' not in move_data:
                return False
                
            building_type = move_data['type']
            position = move_data['position']
            
            # Check resources
            if building_type == BuildingType.SETTLEMENT:
                required = {
                    Resource.WOOD: 1,
                    Resource.BRICK: 1,
                    Resource.SHEEP: 1,
                    Resource.WHEAT: 1
                }
            elif building_type == BuildingType.CITY:
                required = {
                    Resource.WHEAT: 2,
                    Resource.ORE: 3
                }
            elif building_type == BuildingType.ROAD:
                required = {
                    Resource.WOOD: 1,
                    Resource.BRICK: 1
                }
            
            # Check if player has resources
            if not all(self.resources[self.current_player][r] >= required[r] for r in required):
                return False
                
            # Check position validity
            if not self._is_valid_position(position, building_type):
                return False
                
            return True
            
        elif action == "trade":
            if 'offer' not in move_data or 'request' not in move_data:
                return False
                
            offer = move_data['offer']
            request = move_data['request']
            
            # Check if player has resources to trade
            if not all(self.resources[self.current_player][r] >= offer[r] for r in offer):
                return False
                
            return True
            
        elif action == "use_dev_card":
            if 'card' not in move_data:
                return False
                
            return True
            
        return False

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        action = move_data['action']
        
        if action == "build":
            building_type = move_data['type']
            position = move_data['position']
            
            # Deduct resources
            if building_type == BuildingType.SETTLEMENT:
                required = {
                    Resource.WOOD: 1,
                    Resource.BRICK: 1,
                    Resource.SHEEP: 1,
                    Resource.WHEAT: 1
                }
            elif building_type == BuildingType.CITY:
                required = {
                    Resource.WHEAT: 2,
                    Resource.ORE: 3
                }
            elif building_type == BuildingType.ROAD:
                required = {
                    Resource.WOOD: 1,
                    Resource.BRICK: 1
                }
            
            for r in required:
                self.resources[self.current_player][r] -= required[r]
                
            # Add building
            self.buildings[self.current_player].append({
                "type": building_type,
                "position": position
            })
            
            # Add victory points
            if building_type == BuildingType.SETTLEMENT:
                self.victory_points[self.current_player] += 1
            elif building_type == BuildingType.CITY:
                self.victory_points[self.current_player] += 2
                
        elif action == "trade":
            offer = move_data['offer']
            request = move_data['request']
            
            # Deduct offered resources
            for r in offer:
                self.resources[self.current_player][r] -= offer[r]
                
            # Add requested resources
            for r in request:
                self.resources[self.current_player][r] += request[r]
                
        elif action == "use_dev_card":
            card = move_data['card']
            if card == "knight":
                self.army_size[self.current_player] += 1
            elif card == "road_building":
                self._build_two_roads()
            elif card == "year_of_plenty":
                self._get_two_resources()
            elif card == "monopoly":
                self._take_all_resources()
            
        # Check for victory
        if self.victory_points[self.current_player] >= 10:
            self.phase = "end"
            
        # Move to next player
        self.current_player = (self.current_player + 1) % self.num_players
        
        return self.get_game_state()

    def _is_valid_position(self, position: Tuple[int, int], building_type: BuildingType) -> bool:
        """Check if a position is valid for building"""
        # Check if position is on board
        if position not in self.board:
            return False
            
        # Check if position is adjacent to existing roads/settlements
        if building_type == BuildingType.SETTLEMENT:
            # Must be adjacent to own road
            for road in self.roads[self.current_player]:
                if position in road["position"]:
                    return True
            return False
            
        elif building_type == BuildingType.CITY:
            # Must be on own settlement
            for building in self.buildings[self.current_player]:
                if building["type"] == BuildingType.SETTLEMENT and building["position"] == position:
                    return True
            return False
            
        elif building_type == BuildingType.ROAD:
            # Must connect to own settlement or road
            for building in self.buildings[self.current_player]:
                if building["position"] == position:
                    return True
            for road in self.roads[self.current_player]:
                if position in road["position"]:
                    return True
            return False
            
        return False

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'phase': self.phase,
            'resources': self.resources,
            'buildings': self.buildings,
            'roads': self.roads,
            'dev_cards': self.dev_cards,
            'victory_points': self.victory_points,
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
            
        # Player with most victory points wins
        return max(self.victory_points.items(), key=lambda x: x[1])[0]
