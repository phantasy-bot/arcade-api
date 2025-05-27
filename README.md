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

## Running the Server

To start the development server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

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
