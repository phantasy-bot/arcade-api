"""
Pytest configuration and shared fixtures for game tests.
"""

import pytest
from typing import Dict, Any, Type

from game_abc import AbstractGame

# Add the project root to the Python path for easier imports
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


# Fixtures for testing
def game_factory(game_class: Type[AbstractGame]) -> AbstractGame:
    """Create a new game instance for testing."""
    game = game_class(game_id="test_game")
    game.initialize_game()
    return game


@pytest.fixture
def tic_tac_toe_game():
    """Fixture that provides a TicTacToe game instance."""
    from games.tic_tac_toe import TicTacToeGame

    return game_factory(TicTacToeGame)


# Add more game fixtures as needed
# Example:
# @pytest.fixture
# def chess_game():
#     from games.chess import ChessGame
#     return game_factory(ChessGame)


def pytest_configure(config):
    """Pytest configuration hook."""
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line("markers", "integration: mark test as integration test")
