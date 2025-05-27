# Connect Four Game API Documentation

Connect Four is a two-player connection game in which players choose a color and take turns dropping colored discs into a seven-column, six-row vertically suspended grid. The pieces fall straight down, occupying the lowest available space within the column. The objective of the game is to be the first to form a horizontal, vertical, or diagonal line of four of one's own discs.

## Game Rules

- Players: R (Red) and Y (Yellow)
- Board: 6x7 grid
- Win condition: 4 in a row horizontally, vertically, or diagonally
- First move: Red player starts
- Column-based movement: Pieces fall to the lowest empty row in the selected column
- Draws: If all 42 spaces are filled and no player has won, the game is a draw

## API Endpoints

### Create New Game
```http
POST /games/connect-four/new
```

Creates a new Connect Four game.

Example:
```bash
curl -X POST http://localhost:8000/games/connect-four/new
```

Response:
```json
{
    "game_id": "connect-four-20250521-215050"
}
```

### Make Move
```http
POST /games/connect-four/{game_id}/move
```

Make a move in the game.

Required parameters:
- `column`: 0-6 (left to right)
- `player`: "R" or "Y"

Example:
```bash
curl -X POST http://localhost:8000/games/connect-four/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{"column": 3, "player": "R"}'
```

### Get Game State
```http
GET /games/connect-four/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [null, null, null, "R", null, null, null],
        [null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null]
    ],
    "current_player": "Y",
    "game_over": false,
    "winner": null
}
```

### Get Game History
```http
GET /games/connect-four/{game_id}/history
```

Get the complete history of moves in the game.

### Restore Game State
```http
POST /games/connect-four/{game_id}/restore
```

Restore a game to a previous state using history.

## Error Conditions

- 400 Bad Request: Invalid move (e.g., column is full, wrong player's turn)
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move
