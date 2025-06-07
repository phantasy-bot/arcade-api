#!/usr/bin/env python3
"""
Test script to verify that all games can be loaded correctly.
"""
from game_manager import GameManager


def test_game_loading():
    """Test loading all available games."""
    game_manager = GameManager()

    # Print available game types
    print("\nAvailable game types:")
    for game_type in sorted(game_manager.game_types.keys()):
        print(f"- {game_type}")

    # Try to create an instance of each game
    print("\nTesting game creation:")
    for game_type in sorted(game_manager.game_types.keys()):
        try:
            game_id = game_manager.create_game(game_type)
            print(f"✓ Successfully created {game_type} game with ID: {game_id}")
        except Exception as e:
            print(f"✗ Failed to create {game_type} game: {e}")


if __name__ == "__main__":
    test_game_loading()
