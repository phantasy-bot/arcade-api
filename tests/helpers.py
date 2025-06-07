""
Test helper functions and utilities.
"""
from typing import Dict, Any, List, Tuple, Optional, Union
import json
from pathlib import Path
import random
from datetime import datetime

def load_test_data(filename: str) -> Dict[str, Any]:
    """Load test data from a JSON file."""
    path = Path(__file__).parent / 'test_data' / filename
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_test_data(data: Dict[str, Any], filename: str) -> None:
    """Save test data to a JSON file."""
    test_data_dir = Path(__file__).parent / 'test_data'
    test_data_dir.mkdir(exist_ok=True)
    
    path = test_data_dir / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def assert_valid_game_state(state: Dict[str, Any]) -> None:
    """Assert that a game state is valid."""
    assert isinstance(state, dict), "Game state must be a dictionary"
    assert 'game_id' in state, "Game state must have a game_id"
    assert 'status' in state, "Game state must have a status"
    assert 'current_player' in state, "Game state must have a current_player"
    assert 'players' in state, "Game state must have players"
    assert isinstance(state['players'], list), "Players must be a list"
    assert len(state['players']) > 0, "There must be at least one player"

def generate_random_move(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a random valid move based on the current game state."""
    # This is a simplified example. Actual implementation will depend on the game.
    return {
        'player_id': state['current_player'],
        'move': {
            'type': 'move',
            'data': {
                'x': random.randint(0, 2),  # Example for grid-based games
                'y': random.randint(0, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    }

def play_game_until_completion(game, max_moves: int = 100) -> Dict[str, Any]:
    """
    Play a game with random moves until completion or max_moves is reached.
    Returns the final game state.
    """
    state = game.get_game_state()
    move_count = 0
    
    while not state.get('game_over', False) and move_count < max_moves:
        try:
            move = generate_random_move(state)
            state = game.make_move(move)
            move_count += 1
        except (ValueError, RuntimeError) as e:
            # If we can't make a move, the game might be over
            print(f"Game error: {e}")
            break
    
    return state
