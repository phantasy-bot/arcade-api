# Game Arcade API

A lightweight, production-ready API for managing multiple game types and game sessions.

## Features

- Support for multiple game types (Tic-Tac-Toe, Connect Four, etc.)
- JSON-based game state management
- Game history tracking and replay
- State persistence and restoration
- Production-ready with proper error handling
- Easy state persistence and serialization
- RESTful API interface

## Game Types Currently Supported

- Tic-Tac-Toe
- Connect Four
- (More games to be added)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd game-arcade-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development Setup

1. First, create and activate a virtual environment:
   ```bash
   # On Windows:
   python -m venv .venv
   .venv\Scripts\activate
   
   # On macOS/Linux:
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install the required dependencies:
   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (including testing tools)
   pip install -r requirements-dev.txt
   ```

## Running the Server

To start the development server:
```bash
uvicorn app:app --reload --port 4444
```

The API will be available at `http://localhost:4444`

## Testing Framework

The project includes a comprehensive testing framework to ensure game logic is correct and reliable.

### Running Tests

#### Basic Test Commands

```bash
# Run all tests with coverage report
pytest --cov=. --cov-report=term-missing

# Run all tests without coverage
pytest

# Run a specific test file
pytest tests/test_connect_four.py -v

# Run a specific test method
pytest tests/test_connect_four.py::TestConnectFourGame::test_diagonal_win -v

# Run tests with detailed output
pytest -v

# Run tests with coverage report in HTML format (creates htmlcov/ directory)
pytest --cov=. --cov-report=html
```

#### Running Specific Test Cases

For more control over test execution, use the `run_test_case.py` script:

```bash
# Run a specific test case
python scripts/run_test_case.py tic_tac_toe test_win_condition

# Run with test data
python scripts/run_test_case.py tic_tac_toe test_win_condition --test-data tests/test_data/tic_tac_toe_win.json
```

#### Test Utilities

The `tests/helpers.py` module provides utility functions for testing:

- `load_test_data()`: Load test data from JSON files
- `save_test_data()`: Save test data to JSON files
- `assert_valid_game_state()`: Validate game state structure
- `generate_random_move()`: Generate random valid moves
- `play_game_until_completion()`: Automate game play for testing

Example usage:

```python
from tests.helpers import load_test_data, assert_valid_game_state

def test_with_data():
    test_data = load_test_data('tic_tac_toe_win.json')
    # Use test_data in your test
    assert_valid_game_state(test_data['initial_state'])
```

### Test Structure

Each game has its own test file following the naming convention `test_<game_name>.py`. The test files are automatically generated and include test stubs for common test cases:

- `test_initial_state`: Verify the initial game state
- `test_valid_moves`: Test valid moves
- `test_invalid_moves`: Test invalid moves
- `test_game_flow`: Test a complete game flow
- `test_win_condition`: Test win conditions
- `test_draw_condition`: Test draw conditions (if applicable)

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking

Run all code quality checks:

```bash
# Format code with black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type check with mypy
mypy .
```

## Continuous Integration

The project uses GitHub Actions for continuous integration. The following checks are run on every push and pull request:

- Unit tests on multiple Python versions
- Code coverage reporting
- Code formatting with Black
- Import sorting with isort
- Linting with flake8
- Type checking with mypy

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/game-arcade-api.git
   cd game-arcade-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Run tests:
   ```bash
   python run_tests.py
   ```

## API Documentation

### 1. List Available Games
```http
GET /games
```

Returns a list of available game types.

### 2. Create New Game
```http
POST /games/{game_type}/new
```

Creates a new game instance of the specified type.

Example:
```bash
curl -X POST http://localhost:8000/games/tic-tac-toe/new
```

Response:
```json
{
    "game_id": "tic-tac-toe-20250521-214458"
}
```

### 3. Make Move
```http
POST /games/{game_type}/{game_id}/move
```

Makes a move in the game. The required move data depends on the game type.

Example for Tic-Tac-Toe:
```bash
curl -X POST http://localhost:8000/games/tic-tac-toe/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{"row": 0, "col": 0, "player": "X"}'
```

Example for Connect Four:
```bash
curl -X POST http://localhost:8000/games/connect-four/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{"column": 3, "player": "R"}'
```

### 4. Get Game State
```http
GET /games/{game_type}/{game_id}/state
```

Gets the current state of the game.

Example:
```bash
curl http://localhost:8000/games/tic-tac-toe/{game_id}/state
```

### 5. Get Game History
```http
GET /games/{game_type}/{game_id}/history
```

Gets the complete history of moves in the game.

Example:
```bash
curl http://localhost:8000/games/tic-tac-toe/{game_id}/history
```

### 6. Restore Game State
```http
POST /games/{game_type}/{game_id}/restore
```

Restores a game to a previous state using history.

Example:
```bash
curl -X POST http://localhost:8000/games/tic-tac-toe/{game_id}/restore \
    -H "Content-Type: application/json" \
    -d '{"history_json": "[...]"}'
```

## Game Rules and Move Formats

### Tic-Tac-Toe
- Players: X and O
- Board: 3x3 grid
- Move format: {"row": 0-2, "col": 0-2, "player": "X" or "O"}
- Win condition: 3 in a row horizontally, vertically, or diagonally

### Connect Four
- Players: R (Red) and Y (Yellow)
- Board: 6x7 grid
- Move format: {"column": 0-6, "player": "R" or "Y"}
- Win condition: 4 in a row horizontally, vertically, or diagonally

## Adding New Games

To add a new game type:

1. Create a new file in the `games` directory
2. Implement the `AbstractGame` interface
3. Register the game in the `GameManager` class

Example:
```python
from game_abc import AbstractGame

class NewGame(AbstractGame):
    def initialize_game(self):
        # Implement game initialization
        pass

    def validate_move(self, move_data):
        # Implement move validation
        pass

    # Implement other required methods...
```

## Error Handling

The API returns HTTP status codes and error messages:
- 200: Success
- 400: Bad Request (invalid move or data)
- 404: Not Found (game not found)
- 500: Internal Server Error

Example error response:
```json
{
    "detail": "Invalid move: Column is full"
}
```

## State Persistence

Game states can be persisted and restored using the history endpoints. The history includes:
- All moves made
- Timestamps
- Player information
- Game state at each move

## Development Guidelines

1. Keep game logic in the game classes
2. Use JSON for all data exchange
3. Validate all inputs
4. Maintain consistent error handling
5. Document new game rules and move formats

## Contributing

1. Fork the repository
2. Create your feature branch
3. Implement your changes
4. Update documentation
5. Submit a pull request
