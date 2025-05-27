# Tic-Tac-Toe Game API Documentation

Tic-Tac-Toe is a classic two-player game where players take turns marking spaces in a 3×3 grid. The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row wins the game.

## Game Rules

- Players: X and O
- Board: 3x3 grid
- Win condition: 3 in a row horizontally, vertically, or diagonally
- First move: X always goes first
- Draws: If all 9 spaces are filled and no player has won, the game is a draw

## API Endpoints

### Create New Game
```http
POST /games/tic-tac-toe/new
```

Creates a new Tic-Tac-Toe game.

Example:
```bash
curl -X POST http://localhost:8000/games/tic-tac-toe/new
```

Response:
```json
{
    "game_id": "tic-tac-toe-20250521-215050"
}
```

### Make Move
```http
POST /games/tic-tac-toe/{game_id}/move
```

Make a move in the game.

Required parameters:
- `row`: 0-2 (top to bottom)
- `col`: 0-2 (left to right)
- `player`: "X" or "O"

Example:
```bash
curl -X POST http://localhost:8000/games/tic-tac-toe/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{"row": 0, "col": 0, "player": "X"}'
```

### Get Game State
```http
GET /games/tic-tac-toe/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        ["X", null, null],
        [null, null, null],
        [null, null, null]
    ],
    "current_player": "O",
    "game_over": false,
    "winner": null
}
```

### Get Game History
```http
GET /games/tic-tac-toe/{game_id}/history
```

Get the complete history of moves in the game.

### Restore Game State
```http
POST /games/tic-tac-toe/{game_id}/restore
```

Restore a game to a previous state using history.

## Error Conditions

- 400 Bad Request: Invalid move (e.g., space already taken, wrong player's turn)
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move
