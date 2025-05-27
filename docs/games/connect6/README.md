# Connect 6 Game API Documentation

Connect 6 is a strategy board game where players take turns placing stones on a board. The goal is to be the first to create a line of 6 stones horizontally, vertically, or diagonally.

## Game Rules

- Board size: 19x19
- Players: Black and White
- First turn (Black): Places 2 stones
- All other turns: Place 1 stone
- Win condition: Create a line of 6 stones
- Lines can be horizontal, vertical, or diagonal
- No restriction on line placement

## API Endpoints

### Create New Game
```http
POST /games/connect6/new
```

Creates a new Connect 6 game.

Example:
```bash
curl -X POST http://localhost:8000/games/connect6/new
```

Response:
```json
{
    "game_id": "connect6-20250521-231940"
}
```

### Make Move
```http
POST /games/connect6/{game_id}/move
```

Make a move in the game.

Required parameters:
- `positions`: List of positions to place stones
  - First turn (Black): Must be 2 positions
  - All other turns: Must be 1 position
  - Each position is a list: [x, y]

Example (first turn - Black places 2 stones):
```bash
curl -X POST http://localhost:8000/games/connect6/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "positions": [
            [9, 9],
            [10, 10]
        ]
    }'
```

Example (all other turns - place 1 stone):
```bash
curl -X POST http://localhost:8000/games/connect6/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "positions": [
            [9, 10]
        ]
    }'
```

### Get Game State
```http
GET /games/connect6/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ],
    "current_player": "WHITE",
    "turn": 2,
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid number of positions
- 400 Bad Request: Invalid position
- 400 Bad Request: Position occupied
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard 19x19 board
- Stone placement
- Line detection
- Turn management
- Game end detection
- Winner determination
