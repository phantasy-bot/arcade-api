# Mancala Game API Documentation

Mancala is a strategy board game played with seeds and holes. Players take turns moving seeds around the board, trying to capture more seeds than their opponent.

## Game Rules

- Board: 12 holes (6 for each player) + 2 stores
- Players: Player 1 (left) and Player 2 (right)
- Start: 4 seeds in each hole
- Moves:
  - Choose a hole with seeds
  - Distribute seeds clockwise
  - Last seed in own store: take another turn
  - Last seed in own empty hole: capture opposite hole's seeds
- End game:
  - When one player's holes are empty
  - Move remaining seeds to stores
  - Player with more seeds in store wins

## API Endpoints

### Create New Game
```http
POST /games/mancala/new
```

Creates a new Mancala game.

Example:
```bash
curl -X POST http://localhost:8000/games/mancala/new
```

Response:
```json
{
    "game_id": "mancala-20250521-223907"
}
```

### Make Move
```http
POST /games/mancala/{game_id}/move
```

Make a move in the game.

Required parameters:
- `hole`: Hole index (1-6 for Player 1, 8-13 for Player 2)

Example:
```bash
curl -X POST http://localhost:8000/games/mancala/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "hole": 3
    }'
```

### Get Game State
```http
GET /games/mancala/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        0,    // Player 1 store
        4,    // Player 1 hole 1
        4,    // Player 1 hole 2
        4,    // Player 1 hole 3
        4,    // Player 1 hole 4
        4,    // Player 1 hole 5
        4,    // Player 1 hole 6
        0,    // Player 2 store
        4,    // Player 2 hole 1
        4,    // Player 2 hole 2
        4,    // Player 2 hole 3
        4,    // Player 2 hole 4
        4,    // Player 2 hole 5
        4     // Player 2 hole 6
    ],
    "current_player": "PLAYER1",
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid hole index
- 400 Bad Request: Empty hole
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard 6-hole board
- Seed distribution
- Store capture
- Multiple turn rule
- Capture rule
- Game end detection
- Winner determination
