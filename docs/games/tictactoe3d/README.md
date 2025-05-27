# 3D Tic-Tac-Toe Game API Documentation

3D Tic-Tac-Toe is an extension of the classic Tic-Tac-Toe game played on a 4x4x4 cube. Players take turns placing their pieces in empty spaces, trying to create a line of 4 pieces in any direction.

## Game Rules

- Board size: 4x4x4
- Players: X and O
- Win condition: Create a line of 4 pieces
- Lines can be:
  - Horizontal
  - Vertical
  - Depth-wise
  - Diagonal (including 3D diagonals)

## API Endpoints

### Create New Game
```http
POST /games/tictactoe3d/new
```

Creates a new 3D Tic-Tac-Toe game.

Example:
```bash
curl -X POST http://localhost:8000/games/tictactoe3d/new
```

Response:
```json
{
    "game_id": "tictactoe3d-20250521-232406"
}
```

### Make Move
```http
POST /games/tictactoe3d/{game_id}/move
```

Make a move in the game.

Required parameters:
- `position`: List of 3 coordinates [x, y, z]
  - x: 0-3 (horizontal)
  - y: 0-3 (vertical)
  - z: 0-3 (depth)

Example:
```bash
curl -X POST http://localhost:8000/games/tictactoe3d/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "position": [0, 0, 0]
    }'
```

### Get Game State
```http
GET /games/tictactoe3d/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ]
        ],
        [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ]
        ],
        [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ]
        ],
        [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ]
        ]
    ],
    "current_player": "X",
    "game_over": false,
    "winner": null
}
```

## Error Conditions

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

- 3D board representation
- Piece placement
- Line detection (26 directions)
- Turn management
- Game end detection
- Winner determination
