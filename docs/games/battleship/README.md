# Battleship Game API Documentation

Battleship is a strategy game where players try to sink their opponent's ships by guessing their locations on a grid.

## Game Rules

- Players: 2
- Board: 10x10 grid
- Ships:
  - Carrier (5 spaces)
  - Battleship (4 spaces)
  - Cruiser (3 spaces)
  - Submarine (3 spaces)
  - Destroyer (2 spaces)
- Play: Players take turns shooting at opponent's grid
- Win: Sink all opponent's ships

## API Endpoints

### Create New Game
```http
POST /games/battleship/new
```

Creates a new Battleship game.

Optional parameters:
- `board_size`: Size of the board (default: 10)

Example:
```bash
curl -X POST http://localhost:8000/games/battleship/new
```

Response:
```json
{
    "game_id": "battleship-20250521-234922"
}
```

### Make Move
```http
POST /games/battleship/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "shoot"
- `x`: X coordinate (0-9)
- `y`: Y coordinate (0-9)

Example:
```bash
curl -X POST http://localhost:8000/games/battleship/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "shoot",
        "x": 3,
        "y": 4
    }'
```

### Get Game State
```http
GET /games/battleship/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board_size": 10,
    "current_player": 0,
    "phase": "play",
    "shots": {
        "0": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ],
        "1": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
    },
    "sunk_ships": {
        "0": ["DESTROYER"],
        "1": []
    },
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid action
- 400 Bad Request: Invalid coordinates
- 400 Bad Request: Position already shot
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Ship placement
- Turn-based shooting
- Hit/miss tracking
- Ship sinking
- Game end detection
- Winner determination
