# Concentration (Memory) Game API Documentation

Concentration is a memory game where players take turns flipping over pairs of cards to find matching pairs. The player with the most matches wins.

## Game Rules

- Players: 2
- Board: 4x4 grid (default)
- Cards: Pairs of matching cards
- Play: Players take turns flipping over cards
- Win: Most matches when all cards are matched

## API Endpoints

### Create New Game
```http
POST /games/concentration/new
```

Creates a new Concentration game.

Optional parameters:
- `board_size`: Size of the board (default: 4)

Example:
```bash
curl -X POST http://localhost:8000/games/concentration/new
```

Response:
```json
{
    "game_id": "concentration-20250522-001851"
}
```

### Make Move
```http
POST /games/concentration/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "flip"
- `position`: [x, y] coordinates

Example:
```bash
curl -X POST http://localhost:8000/games/concentration/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "flip",
        "position": [1, 2]
    }'
```

### Get Game State
```http
GET /games/concentration/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [
            {"value": "1", "is_face_up": true},
            {"value": "2", "is_face_up": false}
        ],
        [
            {"value": "1", "is_face_up": true},
            {"value": "2", "is_face_up": false}
        ]
    ],
    "current_player": 0,
    "phase": "play",
    "flipped_cards": [[0, 0], [0, 1]],
    "matches": [[0, 0], [1, 0]],
    "scores": {
        "0": 1,
        "1": 0
    },
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid action
- 400 Bad Request: Invalid position
- 400 Bad Request: Card already matched
- 400 Bad Request: Card already flipped
- 400 Bad Request: Too many cards flipped
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Card flipping
- Match detection
- Score tracking
- Turn management
- Game end detection
- Winner determination
