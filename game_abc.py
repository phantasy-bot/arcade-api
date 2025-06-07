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
        self.data_dir.mkdir(exist_ok=True)

    def add_move(self, move: GameMove) -> None:
        self.moves.append(move)
        # The game class is responsible for updating its state and then calling
        # self.history.current_state = self.get_game_state() before or after add_move.
        # add_move here just records the move and persists.
        self._persist_to_disk()

    def get_history(self) -> List[Dict[str, Any]]:
        return [move.__dict__ for move in self.moves]

    def serialize(self) -> str:
        return json.dumps({"moves": self.get_history(), "state": self.current_state, "game_id": self.game_id})

    def deserialize(self, data: str) -> None:
        parsed = json.loads(data)
        self.moves = [GameMove(**move) for move in parsed.get("moves", [])]
        self.current_state = parsed.get("state", {})
        self.game_id = parsed.get("game_id", self.game_id) # Restore game_id

    def _get_game_file(self) -> Optional[Path]:
        if not self.game_id:
            return None
        return self.data_dir / f"{self.game_id}.json"

    def _persist_to_disk(self) -> None:
        file_path = self._get_game_file()
        if not file_path:
            return
        with open(file_path, "w") as f:
            f.write(self.serialize())

    def load_from_disk(self, game_id: str) -> bool:
        self.game_id = game_id # Ensure game_id is set
        file_path = self._get_game_file()
        if not file_path or not file_path.exists():
            self.current_state = {} # Ensure state is clean if no file
            self.moves = []
            return False
        with open(file_path, "r") as f:
            try:
                self.deserialize(f.read())
            except json.JSONDecodeError: # Handle cases where file is corrupted
                self.current_state = {}
                self.moves = []
                return False
        return True

    def delete_from_disk(self) -> None:
        file_path = self._get_game_file()
        if file_path and file_path.exists():
            file_path.unlink()

class AbstractGame(ABC):
    """Abstract base class for all games"""
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.history = GameHistory(game_id)
        self._load_game_state()

    def _load_game_state(self):
        """Loads game state from history if available, then restores it."""
        if not self.history.load_from_disk(self.game_id):
            # File didn't exist or other load issue.
            # self.history.current_state will be empty. Game should initialize.
            pass # current_state is already {} from GameHistory.load_from_disk
        self._restore_game_state() # Uses self.history.current_state

    @abstractmethod
    def _restore_game_state(self):
        """
        Restore game attributes (e.g., board, current_player) from self.history.current_state.
        Called after _load_game_state. If current_state is empty (new game or failed load),
        this method should set up default attributes. initialize_game() will later establish
        the definitive initial state for a new game.
        """
        raise NotImplementedError

    @abstractmethod
    def initialize_game(self) -> Dict[str, Any]:
        """Initialize a new game instance, set up board, players, etc., and return initial state."""
        raise NotImplementedError

    @abstractmethod
    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        raise NotImplementedError

    @abstractmethod
    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a move and update game state"""
        raise NotImplementedError

    @abstractmethod
    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        raise NotImplementedError

    @abstractmethod
    def is_game_over(self) -> bool:
        """Check if the game is over"""
        raise NotImplementedError

    @abstractmethod
    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        raise NotImplementedError
