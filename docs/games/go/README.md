# Go Game API Documentation

Go is a strategy board game played on a 19x19 grid. Players take turns placing stones of their color (black or white) on empty intersections. The goal is to capture territory and opponent's stones.

## Game Rules

- Board size: 19x19 (standard)
- Players: Black and White
- Stones: Black plays first
- Moves:
  - Place a stone on an empty intersection
  - Pass (skip turn)
  - Capture opponent's stones by surrounding them
- Ko rule: Cannot recreate the previous board position
- Komi: 7.5 points for White
- End game: Two consecutive passes
- Scoring:
  - Territory: Empty points surrounded by a player's stones
  - Captured stones: Each captured stone counts as one point
  - Final score: Territory + Captured stones + Komi (for White)

## API Endpoints

### Create New Game
```http
POST /games/go/new
```

Creates a new Go game.

Example:
```bash
curl -X POST http://localhost:8000/games/go/new
```

Response:
```json
{
    "game_id": "go-20250521-223001"
}
```

### Make Move
```http
POST /games/go/{game_id}/move
```

Make a move in the game.

Required parameters:
- `x`: Row position (0-18)
- `y`: Column position (0-18)
- `pass`: Boolean to pass turn (optional)

Example (place stone):
```bash
curl -X POST http://localhost:8000/games/go/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "x": 5,
        "y": 5
    }'
```

Example (pass turn):
```bash
curl -X POST http://localhost:8000/games/go/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "pass": true
    }'
```

### Get Game State
```http
GET /games/go/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [0, 0, 0, ...],
        [0, 0, 0, ...],
        [...]
    ],
    "current_player": "BLACK",
    "captured_stones": {
        "BLACK": 5,
        "WHITE": 3
    },
    "ko_position": [5, 5],
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid move (e.g., placing on occupied point)
- 400 Bad Request: Ko rule violation
- 400 Bad Request: Suicide move (placing stone that would be immediately captured)
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard 19x19 board
- Stone placement and capture
- Ko rule enforcement
- Territory calculation
- Score calculation with komi
- Pass move
- Game end detection
- Winner determination
