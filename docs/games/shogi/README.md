# Shogi Game API Documentation

Shogi (将棋), also known as Japanese chess, is a two-player strategy board game in the same family as Western chess, chaturanga, makruk, and xiangqi, and is the most popular of a family of chess variants native to Japan. Shogi is characterized by the ability to return pieces to the board as allies after they have been captured, which results in a more dynamic game than other chess variants.

## Game Rules

- Players: w (White) and b (Black)
- Board: 9x9 grid
- Pieces:
  - Pawns (P): Move forward, capture forward
  - Lances (L): Move forward any number of squares
  - Knights (N): Move in an L-shape (2 forward, 1 sideways)
  - Silver Generals (S): Move one square diagonally or forward
  - Gold Generals (G): Move one square orthogonally or forward diagonally
  - Kings (K): Move one square in any direction
  - Bishops (B): Move diagonally any number of squares
  - Rooks (R): Move orthogonally any number of squares
- First move: White player starts
- Promotion: Most pieces must promote when reaching certain ranks
- Piece drops: Captured pieces can be returned to the board
- Win condition: Checkmate (opponent's king is in check with no legal moves)

## Special Rules

1. **Promotion**:
   - Pawns, lances, and knights must promote when reaching certain ranks
   - Silver generals, bishops, and rooks may choose to promote
   - Promoted pieces gain additional movement abilities
   - Pieces cannot promote if it would result in checkmate

2. **Piece Drops**:
   - Captured pieces can be dropped back onto the board
   - Cannot drop a piece that would result in checkmate
   - Cannot drop a pawn in the same file as another pawn
   - Cannot drop a king
   - Cannot drop a piece that would result in stalemate

3. **Piece Movement**:
   - All pieces except kings and gold generals have different movement when promoted
   - Promoted pieces generally gain additional movement abilities
   - Pieces cannot move through other pieces
   - Pieces cannot move off the board

## API Endpoints

### Create New Game
```http
POST /games/shogi/new
```

Creates a new Shogi game.

Example:
```bash
curl -X POST http://localhost:8000/games/shogi/new
```

Response:
```json
{
    "game_id": "shogi-20250521-220748"
}
```

### Make Move
```http
POST /games/shogi/{game_id}/move
```

Make a move in the game.

Required parameters:
- `from_row`: 0-8 (top to bottom)
- `from_col`: 0-8 (left to right)
- `to_row`: 0-8 (top to bottom)
- `to_col`: 0-8 (left to right)
- `player`: "w" or "b"
- `promoted`: true or false (for promotion)

Example (normal move):
```bash
curl -X POST http://localhost:8000/games/shogi/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "from_row": 6,
        "from_col": 0,
        "to_row": 5,
        "to_col": 0,
        "player": "w",
        "promoted": false
    }'
```

Example (piece drop):
```bash
curl -X POST http://localhost:8000/games/shogi/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "to_row": 3,
        "to_col": 4,
        "player": "w",
        "piece_type": "P",
        "is_drop": true
    }'
```

### Get Game State
```http
GET /games/shogi/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [
            {"type": "L", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "N", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "S", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "G", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "K", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "G", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "S", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "N", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "L", "color": "b", "promoted": false, "promotion_rank": null}
        ],
        [
            null, null, null,
            {"type": "B", "color": "b", "promoted": false, "promotion_rank": null},
            null,
            {"type": "R", "color": "b", "promoted": false, "promotion_rank": null},
            null, null, null
        ],
        [
            {"type": "P", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "b", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "b", "promoted": false, "promotion_rank": null}
        ],
        [
            null, null, null, null, null, null, null, null, null
        ],
        [
            null, null, null, null, null, null, null, null, null
        ],
        [
            null, null, null, null, null, null, null, null, null
        ],
        [
            {"type": "P", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "P", "color": "w", "promoted": false, "promotion_rank": null}
        ],
        [
            null, null, null,
            {"type": "B", "color": "w", "promoted": false, "promotion_rank": null},
            null,
            {"type": "R", "color": "w", "promoted": false, "promotion_rank": null},
            null, null, null
        ],
        [
            {"type": "L", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "N", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "S", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "G", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "K", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "G", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "S", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "N", "color": "w", "promoted": false, "promotion_rank": null},
            {"type": "L", "color": "w", "promoted": false, "promotion_rank": null}
        ]
    ],
    "current_player": "b",
    "hands": {
        "w": {
            "P": 0,
            "L": 0,
            "N": 0,
            "S": 0,
            "G": 0,
            "B": 0,
            "R": 0
        },
        "b": {
            "P": 0,
            "L": 0,
            "N": 0,
            "S": 0,
            "G": 0,
            "B": 0,
            "R": 0
        }
    },
    "game_over": false,
    "winner": null,
    "in_check": false
}
```

### Get Game History
```http
GET /games/shogi/{game_id}/history
```

Get the complete history of moves in the game.

### Restore Game State
```http
POST /games/shogi/{game_id}/restore
```

Restore a game to a previous state using history.

## Error Conditions

- 400 Bad Request: Invalid move (e.g., invalid coordinates, wrong player's turn, illegal move)
- 400 Bad Request: Invalid piece drop (e.g., dropping in same file as pawn, dropping king)
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move
