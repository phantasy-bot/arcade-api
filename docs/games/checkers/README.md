# Checkers Game API Documentation

Checkers is a strategy board game played on an 8x8 board. Players take turns moving their pieces diagonally to capture opponent's pieces. The goal is to capture all of the opponent's pieces or block them so they cannot move.

## Game Rules

- Board size: 8x8
- Players: Black and White
- Pieces:
  - Regular pieces move diagonally forward
  - Kings can move diagonally in any direction
  - Pieces start on dark squares only
- Moves:
  - Move one square diagonally forward
  - Capture by jumping over an opponent's piece
  - Multiple captures in a single turn
  - Must capture if possible
  - Pieces become kings when reaching the opposite end
- Win conditions:
  - Capture all opponent's pieces
  - Block opponent so they cannot move
  - Draw if both players have pieces but no moves

## API Endpoints

### Create New Game
```http
POST /games/checkers/new
```

Creates a new Checkers game.

Example:
```bash
curl -X POST http://localhost:8000/games/checkers/new
```

Response:
```json
{
    "game_id": "checkers-20250521-223308"
}
```

### Make Move
```http
POST /games/checkers/{game_id}/move
```

Make a move in the game.

Required parameters:
- `select`: [x, y] to select a piece (optional)
- `move`: {"from": [x, y], "to": [x, y]} to move a piece

Example (select piece):
```bash
curl -X POST http://localhost:8000/games/checkers/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "select": [5, 0]
    }'
```

Example (move piece):
```bash
curl -X POST http://localhost:8000/games/checkers/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "move": {
            "from": [5, 0],
            "to": [4, 1]
        }
    }'
```

### Get Game State
```http
GET /games/checkers/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [0, 3, 0, 3, 0, 3, 0, 3],
        [3, 0, 3, 0, 3, 0, 3, 0],
        [...]
    ],
    "current_player": "BLACK",
    "selected_piece": [5, 0],
    "must_capture": true,
    "captured_pieces": {
        "BLACK": 0,
        "WHITE": 0
    },
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid move (e.g., moving to invalid position)
- 400 Bad Request: Must capture but not capturing
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard 8x8 board
- Piece movement and capture
- King promotion
- Multiple capture
- Must capture rule
- Game end detection
- Draw detection
