#!/usr/bin/env python3
"""
Script to generate test files for all games.
"""
import os
import re
from pathlib import Path
from string import Template
from typing import Optional

# Directory paths
BASE_DIR = Path(__file__).parent.parent
GAMES_DIR = BASE_DIR / "games"
TESTS_DIR = BASE_DIR / "tests"
TEMPLATE_PATH = TESTS_DIR / "templates" / "test_game_template.py"


def to_camel_case(snake_str):
    """Convert snake_case to CamelCase."""
    return "".join(word.title() for word in snake_str.split("_"))


def get_game_class_name(module_path: Path) -> Optional[str]:
    """Extract the game class name from the module."""
    try:
        with open(module_path, 'r') as f:
            content = f.read()
            
        # Look for class definitions that end with 'Game'
        import ast
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith('Game'):
                return node.name
                
    except Exception as e:
        print(f"  Warning: Could not parse {module_path}: {e}")
    
    return None

def generate_test_file(game_name: str, force_update: bool = True):
    """Generate or update a test file for a game.
    
    Args:
        game_name: Name of the game (directory name in games/)
        force_update: If True, update the file even if it exists
    """
    game_module = game_name
    game_module_path = GAMES_DIR / game_name / "__init__.py"
    
    # Try to get the actual game class name from the module
    game_class_name = get_game_class_name(game_module_path)
    
    if game_class_name is None:
        # Fall back to the default naming convention if we can't determine the class name
        game_class_name = to_camel_case(game_name.replace("-", "_")) + "Game"
        print(f"  Using default class name: {game_class_name}")
    
    test_file = TESTS_DIR / f"test_{game_name}.py"
    test_class_name = f"Test{game_class_name}"

    # Read the template
    with open(TEMPLATE_PATH, "r") as f:
        template_content = f.read()

    # Generate the import statement
    import_statement = f"from games.{game_module} import {game_class_name}"
    
    # Replace placeholders
    test_content = template_content.format(
        game_name=game_name.replace("_", " ").title()
    )
    
    # Replace the import placeholder
    test_content = test_content.replace(
        "# GAME_IMPORT_PLACEHOLDER", 
        import_statement
    )
    
    # Replace the test class name and game class
    test_content = test_content.replace(
        "class TestGame(BaseGameTest):", 
        f"class {test_class_name}(BaseGameTest):"
    )
    
    test_content = test_content.replace(
        "GAME_CLASS = None  # Will be set by the test generator",
        f"GAME_CLASS = {game_class_name}"
    )

    # Check if we need to update the file
    if test_file.exists():
        with open(test_file, "r") as f:
            existing_content = f.read()
        
        # If the file hasn't changed and we're not forcing an update, skip it
        if not force_update and test_content == existing_content:
            print(f"Skipping unchanged file: {test_file}")
            return
            
        print(f"Updating test file: {test_file}")
    else:
        print(f"Generating new test file: {test_file}")
    
    # Write the test file
    with open(test_file, "w") as f:
        f.write(test_content)


def main():
    """Generate test files for all games."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate or update test files for games.')
    parser.add_argument('--force', action='store_true', help='Force update all test files')
    parser.add_argument('games', nargs='*', help='Specific games to generate tests for (default: all)')
    args = parser.parse_args()
    
    # Create tests directory if it doesn't exist
    TESTS_DIR.mkdir(exist_ok=True, parents=True)
    
    # If specific games were provided, only process those
    if args.games:
        game_dirs = [GAMES_DIR / game for game in args.games if (GAMES_DIR / game).is_dir()]
        if not game_dirs:
            print(f"No valid game directories found for: {', '.join(args.games)}")
            return
    else:
        # Otherwise, process all game directories
        game_dirs = [d for d in sorted(GAMES_DIR.iterdir()) 
                    if d.is_dir() and not d.name.startswith('__') and not d.name.startswith('.')]
    
    # Process each game directory
    for game_dir in game_dirs:
        try:
            generate_test_file(game_dir.name, force_update=args.force)
        except Exception as e:
            print(f"Error generating tests for {game_dir.name}: {e}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
