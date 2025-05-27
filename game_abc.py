from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class GameMove:
    """Represents a single game move"""
    player: str
    move_data: Dict[str, Any]
    timestamp: float

class GameHistory:
    """Manages game history and state persistence"""
    def __init__(self, game_id: str = None):
        self.moves: List[GameMove] = []
        self.current_state: Dict[str, Any] = {}
        self.game_id = game_id
        self.data_dir = Path("game_data")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)

    def add_move(self, move: GameMove) -> None:
        """Add a move to the history and persist to disk"""
        self.moves.append(move)
        self._persist_to_disk()
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the full game history as JSON-serializable list"""
        return [move.__dict__ for move in self.moves]

    def serialize(self) -> str:
        """Serialize the entire game history and state to JSON"""
        return json.dumps({
            'moves': self.get_history(),
            'state': self.current_state
        })

    def deserialize(self, data: str) -> None:
        """Deserialize game history and state from JSON"""
        parsed = json.loads(data)
        self.moves = [GameMove(**move) for move in parsed['moves']]
        self.current_state = parsed['state']
        self._persist_to_disk()

    def _get_game_file(self) -> Path:
        """Get the file path for this game's data"""
        if not self.game_id:
            raise ValueError("Game ID is required for persistence")
        return self.data_dir / f"{self.game_id}.json"

    def _persist_to_disk(self) -> None:
        """Save game state to disk"""
        if not self.game_id:
            return
            
        file_path = self._get_game_file()
        with open(file_path, 'w') as f:
            f.write(self.serialize())

    def load_from_disk(self, game_id: str) -> bool:
        """Load game state from disk"""
        file_path = self.data_dir / f"{game_id}.json"
        if not file_path.exists():
            return False
            
        with open(file_path, 'r') as f:
            self.deserialize(f.read())
        return True

    def delete_from_disk(self) -> None:
        """Delete game data from disk"""
        if not self.game_id:
            return
            
        file_path = self._get_game_file()
        if file_path.exists():
            file_path.unlink()

class AbstractGame(ABC):
    """Abstract base class for all games"""
    
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.history = GameHistory(game_id)
        self._load_game_state()

    def _load_game_state(self):
        """Load game state from history"""
        self.history_state = self.history.get_history()
        self._restore_game_state()

    def _restore_game_state(self):
        """Restore game state from history"""
        # This should be implemented by specific game classes
        pass

    def initialize_game(self) -> Dict[str, Any]:
        """Initialize a new game instance"""
        self._init_game_state()
        return self.get_game_state()

    def _init_game_state(self):
        """Initialize game state"""
        # This should be implemented by specific game classes
        pass

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a move and update game state"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")
            
        # Add move to history
        move = GameMove(
            player=self.current_player,
            move_data=move_data,
            timestamp=time.time()
        )
        self.history.add_move(move)
        
        # Update game state
        self._update_game_state(move_data)
        
        return self.get_game_state()

    def _update_game_state(self, move_data: Dict[str, Any]):
        """Update game state after a move"""
        # This should be implemented by specific game classes
        pass
        self.current_player: Optional[str] = None

    @abstractmethod
    def initialize_game(self) -> Dict[str, Any]:
        """Initialize a new game instance"""
        pass

    @abstractmethod
    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        pass

    @abstractmethod
    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a move and update game state"""
        pass

    @abstractmethod
    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """Check if the game is over"""
        pass

    @abstractmethod
    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        pass
