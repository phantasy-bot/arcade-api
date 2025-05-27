from typing import Dict, Any, Optional, Type
from game_abc import AbstractGame
from pathlib import Path
import importlib
import json

class GameManager:
    def __init__(self):
        self.game_types = {}
        self._register_games()
        
    def _register_games(self):
        """Register all available game types"""
        game_dir = Path(__file__).parent / "games"
        for game_file in game_dir.glob("*.py"):
            game_name = game_file.stem
            try:
                game_module = importlib.import_module(f"games.{game_name}")
                game_class = getattr(game_module, f"{game_name.capitalize()}Game")
                self.game_types[game_name] = game_class
            except (ImportError, AttributeError):
                continue

    def create_game(self, game_type: str) -> str:
        """Create a new game instance"""
        if game_type not in self.game_types:
            raise ValueError(f"Invalid game type: {game_type}")
            
        game_class = self.game_types[game_type]
        game_id = f"{game_type}-{int(time.time())}"
        game = game_class(game_id)
        return game_id

    def get_game(self, game_type: str, game_id: str) -> AbstractGame:
        """Get an existing game instance"""
        if game_type not in self.game_types:
            raise ValueError(f"Invalid game type: {game_type}")
            
        game_class = self.game_types[game_type]
        return game_class(game_id)

    def get_game_history(self, game_type: str, game_id: str) -> Dict[str, Any]:
        """Get game history"""
        game = self.get_game(game_type, game_id)
        return game.history.get_history()

    def restore_game(self, game_type: str, game_id: str, history_json: str) -> None:
        """Restore game state from history"""
        game = self.get_game(game_type, game_id)
        game.history.deserialize(history_json)
