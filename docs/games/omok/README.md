# Omok Game API Documentation

Omok (also known as Five-in-a-Row or Gomoku) is a traditional board game played on a 15x15 grid. Players take turns placing stones on the board, with the goal of being the first to form an unbroken chain of five stones horizontally, vertically, or diagonally.

## Game Rules

- Players: B (Black) and W (White)
- Board: 15x15 grid
- Win condition: 5 in a row horizontally, vertically, or diagonally
- First move: Black player starts
- Draws: If the board is filled and no player has won, the game is a draw
- Free placement: Players can place stones anywhere on the board

## API Endpoints

### Create New Game
```http
POST /games/omok/new
```

Creates a new Omok game.

Example:
```bash
curl -X POST http://localhost:8000/games/omok/new
```

Response:
```json
{
    "game_id": "omok-20250521-215050"
}
```

### Make Move
```http
POST /games/omok/{game_id}/move
```

Make a move in the game.

Required parameters:
- `row`: 0-14 (top to bottom)
- `col`: 0-14 (left to right)
- `player`: "B" or "W"

Example:
```bash
curl -X POST http://localhost:8000/games/omok/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{"row": 7, "col": 7, "player": "B"}'
```

### Get Game State
```http
GET /games/omok/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [null, null, null, null, null, null, null, "B", null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, "B", null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null]
    ],
    "current_player": "W",
    "game_over": false,
    "winner": null
}
```

### Get Game History
```http
GET /games/omok/{game_id}/history
```

Get the complete history of moves in the game.

### Restore Game State
```http
POST /games/omok/{game_id}/restore
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
