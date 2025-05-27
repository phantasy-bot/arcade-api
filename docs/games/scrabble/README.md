# Scrabble Game API Documentation

Scrabble is a word game where players use letter tiles to form words on a game board. The game is played with a 15x15 board and letter tiles that have different point values.

## Game Rules

- Players: 2-4
- Board: 15x15 grid
- Letter tiles: 100 tiles with different point values
- Play: Players take turns placing words on the board
- Points: Based on letter values and special squares
- Win: Highest score when game ends

## Letter Values

- A, E, I, O, U, L, N, S, T, R: 1 point
- D, G: 2 points
- B, C, M, P: 3 points
- F, H, V, W, Y: 4 points
- K: 5 points
- J, X: 8 points
- Q, Z: 10 points
- Blank tile: 0 points

## Special Squares

- Double Letter
- Triple Letter
- Double Word
- Triple Word
- Center square: Double word score for first word

## API Endpoints

### Create New Game
```http
POST /games/scrabble/new
```

Creates a new Scrabble game.

Optional parameters:
- `num_players`: Number of players (default: 2)

Example:
```bash
curl -X POST http://localhost:8000/games/scrabble/new
```

Response:
```json
{
    "game_id": "scrabble-20250522-000950"
}
```

### Make Move
```http
POST /games/scrabble/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "place_word" or "exchange"
- For "place_word" action:
  - `word`: Word to place
  - `start`: [x, y] coordinates
  - `direction": "horizontal" or "vertical"
- For "exchange" action:
  - `tiles`: List of tiles to exchange

Example (place word):
```bash
curl -X POST http://localhost:8000/games/scrabble/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "place_word",
        "word": "hello",
        "start": [7, 7],
        "direction": "horizontal"
    }'
```

Example (exchange tiles):
```bash
curl -X POST http://localhost:8000/games/scrabble/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "exchange",
        "tiles": ["a", "e", "i"]
    }'
```

### Get Game State
```http
GET /games/scrabble/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, "h", "e", "l", "l", "o", null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
        [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null]
    ],
    "current_player": 0,
    "phase": "play",
    "rack": {
        "0": [
            {"letter": "a", "points": 1, "is_blank": false},
            {"letter": "b", "points": 3, "is_blank": false},
            {"letter": "c", "points": 3, "is_blank": false},
            {"letter": "d", "points": 2, "is_blank": false},
            {"letter": "e", "points": 1, "is_blank": false},
            {"letter": "f", "points": 4, "is_blank": false},
            {"letter": "g", "points": 2, "is_blank": false}
        ]
    },
    "score": {
        "0": 29,
        "1": 0
    },
    "turns": 1,
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid action
- 400 Bad Request: Invalid word
- 400 Bad Request: Invalid position
- 400 Bad Request: Not your turn
- 400 Bad Request: Insufficient tiles
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Letter tile management
- Word placement
- Score calculation
- Special squares
- Exchange mechanism
- Game end detection
- Winner determination
