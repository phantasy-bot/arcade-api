# Othello Game API Documentation

Othello (also known as Reversi) is a strategy board game played on an 8x8 board. Players take turns placing pieces of their color, which can flip opponent's pieces to their color. The goal is to have more pieces of your color on the board at the end of the game.

## Game Rules

- Board size: 8x8
- Players: Black and White
- Start: 4 pieces in center (2 black, 2 white)
- Moves:
  - Place a piece of your color
  - Must flip at least one opponent's piece
  - Pieces are flipped if surrounded by your pieces
  - Can pass if no valid moves
- Win condition:
  - More pieces of your color at game end
  - Draw if equal pieces

## API Endpoints

### Create New Game
```http
POST /games/othello/new
```

Creates a new Othello game.

Example:
```bash
curl -X POST http://localhost:8000/games/othello/new
```

Response:
```json
{
    "game_id": "othello-20250521-224459"
}
```

### Make Move
```http
POST /games/othello/{game_id}/move
```

Make a move in the game.

Required parameters:
- `x`: Row position (0-7)
- `y`: Column position (0-7)
- `pass`: Boolean to pass turn (optional)

Example (place piece):
```bash
curl -X POST http://localhost:8000/games/othello/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "x": 3,
        "y": 2
    }'
```

Example (pass turn):
```bash
curl -X POST http://localhost:8000/games/othello/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "pass": true
    }'
```

### Get Game State
```http
GET /games/othello/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 1, 0, 0, 0],
        [0, 0, 0, 1, 2, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ],
    "current_player": "BLACK",
    "valid_moves": [
        [2, 3],
        [3, 2],
        [4, 5],
        [5, 4]
    ],
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid move (e.g., placing on occupied position)
- 400 Bad Request: Not flipping any pieces
- 400 Bad Request: Passing when valid moves exist
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard 8x8 board
- Piece placement and flipping
- Valid move detection
- Pass move
- Game end detection
- Winner determination
