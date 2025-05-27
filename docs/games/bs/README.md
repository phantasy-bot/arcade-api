# BS (Bullshit) Card Game API Documentation

BS (Bullshit) is a bluffing card game where players try to get rid of their cards by claiming they are playing cards of a specific rank. Other players can call "BS" if they think the claim is false.

## Game Rules

- Players: 2-4
- Deck: Standard 52-card deck
- Start with 2s
- Players take turns playing cards
- Must claim rank being played
- Can bluff (play different cards)
- Other players can call "BS"
- If BS is correct: player takes cards
- If BS is wrong: caller takes cards
- First player to run out of cards wins

## API Endpoints

### Create New Game
```http
POST /games/bs/new
```

Creates a new BS game.

Example:
```bash
curl -X POST http://localhost:8000/games/bs/new
```

Response:
```json
{
    "game_id": "bs-20250521-230832"
}
```

### Make Move
```http
POST /games/bs/{game_id}/move
```

Make a move in the game.

Required parameters:
- `type`: "play" or "call_bs"

For type "play":
- `cards`: List of cards to play
  - Each card is a dictionary with:
    - `suit`: ♠, ♥, ♦, ♣
    - `rank`: 2-14 (2-A)
- `claim`: Number of cards claimed

For type "call_bs":
- No additional parameters

Example (playing cards):
```bash
curl -X POST http://localhost:8000/games/bs/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "type": "play",
        "cards": [
            {"suit": "♠", "rank": 2},
            {"suit": "♥", "rank": 2}
        ],
        "claim": 2
    }'
```

Example (calling BS):
```bash
curl -X POST http://localhost:8000/games/bs/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "type": "call_bs"
    }'
```

### Get Game State
```http
GET /games/bs/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "hands": {
        "0": [
            {"suit": "♠", "rank": 3},
            {"suit": "♥", "rank": 3},
            {"suit": "♦", "rank": 3}
        ],
        "1": [
            {"suit": "♣", "rank": 3},
            {"suit": "♠", "rank": 4},
            {"suit": "♥", "rank": 4}
        ]
    },
    "current_player": 0,
    "current_rank": 2,
    "discard_pile_size": 8,
    "last_claim": [
        {"suit": "♠", "rank": 2},
        {"suit": "♥", "rank": 2}
    ],
    "last_player": 0,
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid move type
- 400 Bad Request: Invalid cards
- 400 Bad Request: Invalid claim
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard 52-card deck
- Bluffing mechanics
- BS calling
- Card management
- Game end detection
- Winner determination
