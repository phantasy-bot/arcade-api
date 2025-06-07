import json
from pathlib import Path
from typing import Dict, Any, Optional
import time


class GameStateManager:
    """Manages game state persistence and retrieval"""

    def __init__(self, data_dir: str = "game_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def create_game(self, game_type: str) -> str:
        """Create a new game instance"""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        game_id = f"{game_type}-{timestamp}"

        # Initialize empty game state
        game_state = {
            "game_type": game_type,
            "created_at": timestamp,
            "moves": [],
            "game_over": False,
            "winner": None,
        }

        self._save_state(game_id, game_state)
        return game_id

    def get_game_state(self, game_id: str) -> Dict[str, Any]:
        """Get current game state"""
        return self._load_state(game_id)

    def add_move(self, game_id: str, move: Dict[str, Any]) -> Dict[str, Any]:
        """Add a move to the game"""
        game_state = self._load_state(game_id)
        game_state["moves"].append(
            {
                "player": move["player"],
                "move_data": move["move_data"],
                "timestamp": time.time(),
            }
        )
        self._save_state(game_id, game_state)
        return game_state

    def _get_file_path(self, game_id: str) -> Path:
        """Get the file path for a game"""
        return self.data_dir / f"{game_id}.json"

    def _load_state(self, game_id: str) -> Dict[str, Any]:
        """Load game state from disk"""
        file_path = self._get_file_path(game_id)
        if not file_path.exists():
            raise ValueError(f"Game {game_id} not found")

        with open(file_path, "r") as f:
            return json.load(f)

    def _save_state(self, game_id: str, state: Dict[str, Any]) -> None:
        """Save game state to disk"""
        file_path = self._get_file_path(game_id)
        with open(file_path, "w") as f:
            json.dump(state, f, indent=2)
