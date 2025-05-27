from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple, Set
import numpy as np
from enum import Enum
import time
import random
from collections import defaultdict

class ShipType(Enum):
    CARRIER = 5
    BATTLESHIP = 4
    CRUISER = 3
    SUBMARINE = 3
    DESTROYER = 2

class ShotResult(Enum):
    HIT = 1
    MISS = 2
    SUNK = 3
    GAME_OVER = 4

class BattleshipGame(AbstractGame):
    def __init__(self, game_id: str, board_size: int = 10):
        super().__init__(game_id)
        self.board_size = board_size
        self.current_player = 0
        self.boards = defaultdict(lambda: np.zeros((board_size, board_size), dtype=int))
        self.shots = defaultdict(lambda: np.zeros((board_size, board_size), dtype=int))
        self.ships = defaultdict(dict)
        self.sunk_ships = defaultdict(set)
        self.phase = "setup"  # setup, play, end
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self.current_player = 0
        self.phase = "setup"
        self.boards = defaultdict(lambda: np.zeros((self.board_size, self.board_size), dtype=int))
        self.shots = defaultdict(lambda: np.zeros((self.board_size, self.board_size), dtype=int))
        self.ships = defaultdict(dict)
        self.sunk_ships = defaultdict(set)
        
        # Place ships for each player
        for player in range(2):
            self._place_ships(player)

    def _place_ships(self, player: int):
        """Randomly place ships for a player"""
        for ship_type in ShipType:
            length = ship_type.value
            placed = False
            
            while not placed:
                # Choose random orientation
                horizontal = random.choice([True, False])
                
                if horizontal:
                    # Choose random position
                    x = random.randint(0, self.board_size - length)
                    y = random.randint(0, self.board_size - 1)
                    
                    # Check if position is valid
                    if all(self.boards[player][x+i][y] == 0 for i in range(length)):
                        # Place ship
                        for i in range(length):
                            self.boards[player][x+i][y] = length
                        placed = True
                        self.ships[player][ship_type] = ((x, y), length, True)
                else:
                    # Choose random position
                    x = random.randint(0, self.board_size - 1)
                    y = random.randint(0, self.board_size - length)
                    
                    # Check if position is valid
                    if all(self.boards[player][x][y+i] == 0 for i in range(length)):
                        # Place ship
                        for i in range(length):
                            self.boards[player][x][y+i] = length
                        placed = True
                        self.ships[player][ship_type] = ((x, y), length, False)

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if 'action' not in move_data:
            return False
            
        action = move_data['action']
        
        if action == "shoot":
            if 'x' not in move_data or 'y' not in move_data:
                return False
                
            x = move_data['x']
            y = move_data['y']
            
            # Check if coordinates are valid
            if not (0 <= x < self.board_size and 0 <= y < self.board_size):
                return False
                
            # Check if this position hasn't been shot yet
            if self.shots[self.current_player][x][y] != 0:
                return False
                
            return True
            
        return False

    def _check_ship_sunk(self, player: int, x: int, y: int) -> Optional[ShipType]:
        """Check if a ship has been sunk"""
        length = self.boards[player][x][y]
        
        if length == 0:
            return None
            
        # Find the ship this position belongs to
        for ship_type, (pos, ship_length, horizontal) in self.ships[player].items():
            if horizontal:
                if pos[0] <= x < pos[0] + ship_length and pos[1] == y:
                    # Check if all positions of this ship have been hit
                    if all(self.shots[player][pos[0]+i][pos[1]] != 0 for i in range(ship_length)):
                        return ship_type
            else:
                if pos[0] == x and pos[1] <= y < pos[1] + ship_length:
                    # Check if all positions of this ship have been hit
                    if all(self.shots[player][pos[0]][pos[1]+i] != 0 for i in range(ship_length)):
                        return ship_type
        
        return None

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move in the game"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        action = move_data['action']
        x = move_data['x']
        y = move_data['y']
        
        if action == "shoot":
            # Mark shot
            self.shots[self.current_player][x][y] = 1
            
            # Check if hit
            if self.boards[self.current_player][x][y] != 0:
                # Check if ship is sunk
                sunk_ship = self._check_ship_sunk(self.current_player, x, y)
                if sunk_ship:
                    self.sunk_ships[self.current_player].add(sunk_ship)
                    return {
                        "result": ShotResult.SUNK.name,
                        "ship": sunk_ship.name,
                        "game_over": self._check_game_over()
                    }
                return {"result": ShotResult.HIT.name}
            
            # Move to next player
            self.current_player = 1 - self.current_player
            return {"result": ShotResult.MISS.name}
            
        return {"result": ShotResult.GAME_OVER.name}

    def _check_game_over(self) -> bool:
        """Check if the game is over"""
        # Game is over if all ships of either player are sunk
        all_ships = set(ShipType)
        return self.sunk_ships[0] == all_ships or self.sunk_ships[1] == all_ships

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board_size': self.board_size,
            'current_player': self.current_player,
            'phase': self.phase,
            'shots': self.shots,
            'sunk_ships': {str(k): [s.name for s in v] for k, v in self.sunk_ships.items()},
            'game_over': self.is_game_over(),
            'winner': self.get_winner()
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.phase == "end"

    def get_winner(self) -> Optional[int]:
        """Get the winner if game is over"""
        if not self.is_game_over():
            return None
            
        all_ships = set(ShipType)
        if self.sunk_ships[0] == all_ships:
            return 1
        elif self.sunk_ships[1] == all_ships:
            return 0
            
        return None
