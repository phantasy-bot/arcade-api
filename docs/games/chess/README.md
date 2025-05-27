# Chess Game API Documentation

Chess is a two-player strategy board game played on a square board, commonly with eight rows and eight columns, that has been described as the "drosophila of artificial intelligence". Each player begins with 16 pieces: one king, one queen, two rooks, two knights, two bishops, and eight pawns.

## Game Rules

- Players: w (White) and b (Black)
- Board: 8x8 grid
- Pieces:
  - Pawns (p): Move forward, capture diagonally
  - Rooks (r): Move any number of squares horizontally or vertically
  - Knights (n): Move in an L-shape (2 squares in one direction, then 1 square perpendicular)
  - Bishops (b): Move any number of squares diagonally
  - Queens (q): Move any number of squares horizontally, vertically, or diagonally
  - Kings (k): Move one square in any direction
- First move: White player starts
- Win condition: Checkmate (opponent's king is in check with no legal moves)
- Draws: Stalemate, insufficient material, threefold repetition, fifty-move rule

## API Endpoints

### Create New Game
```http
POST /games/chess/new
```

Creates a new Chess game.

Example:
```bash
curl -X POST http://localhost:8000/games/chess/new
```

Response:
```json
{
    "game_id": "chess-20250521-220019"
}
```

### Make Move
```http
POST /games/chess/{game_id}/move
```

Make a move in the game.

Required parameters:
- `from_row`: 0-7 (top to bottom)
- `from_col`: 0-7 (left to right)
- `to_row`: 0-7 (top to bottom)
- `to_col`: 0-7 (left to right)
- `player`: "w" or "b"

Example:
```bash
curl -X POST http://localhost:8000/games/chess/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "from_row": 1,
        "from_col": 0,
        "to_row": 3,
        "to_col": 0,
        "player": "w"
    }'
```

### Get Game State
```http
GET /games/chess/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [
            {"type": "r", "color": "b", "has_moved": false},
            {"type": "n", "color": "b", "has_moved": false},
            {"type": "b", "color": "b", "has_moved": false},
            {"type": "q", "color": "b", "has_moved": false},
            {"type": "k", "color": "b", "has_moved": false},
            {"type": "b", "color": "b", "has_moved": false},
            {"type": "n", "color": "b", "has_moved": false},
            {"type": "r", "color": "b", "has_moved": false}
        ],
        [
            {"type": "p", "color": "b", "has_moved": false},
            {"type": "p", "color": "b", "has_moved": false},
            {"type": "p", "color": "b", "has_moved": false},
            {"type": "p", "color": "b", "has_moved": false},
            {"type": "p", "color": "b", "has_moved": false},
            {"type": "p", "color": "b", "has_moved": false},
            {"type": "p", "color": "b", "has_moved": false},
            {"type": "p", "color": "b", "has_moved": false}
        ],
        [
            null, null, null, null, null, null, null, null
        ],
        [
            {"type": "p", "color": "w", "has_moved": true},
            null, null, null, null, null, null, null
        ],
        [
            null, null, null, null, null, null, null, null
        ],
        [
            null, null, null, null, null, null, null, null
        ],
        [
            {"type": "p", "color": "w", "has_moved": false},
            {"type": "p", "color": "w", "has_moved": false},
            {"type": "p", "color": "w", "has_moved": false},
            {"type": "p", "color": "w", "has_moved": false},
            {"type": "p", "color": "w", "has_moved": false},
            {"type": "p", "color": "w", "has_moved": false},
            {"type": "p", "color": "w", "has_moved": false},
            {"type": "p", "color": "w", "has_moved": false}
        ],
        [
            {"type": "r", "color": "w", "has_moved": false},
            {"type": "n", "color": "w", "has_moved": false},
            {"type": "b", "color": "w", "has_moved": false},
            {"type": "q", "color": "w", "has_moved": false},
            {"type": "k", "color": "w", "has_moved": false},
            {"type": "b", "color": "w", "has_moved": false},
            {"type": "n", "color": "w", "has_moved": false},
            {"type": "r", "color": "w", "has_moved": false}
        ]
    ],
    "current_player": "b",
    "game_over": false,
    "winner": null
}
```

### Get Game History
```http
GET /games/chess/{game_id}/history
```

Get the complete history of moves in the game.

### Restore Game State
```http
POST /games/chess/{game_id}/restore
```

Restore a game to a previous state using history.

## Error Conditions

- 400 Bad Request: Invalid move (e.g., invalid coordinates, wrong player's turn, illegal move)
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move
