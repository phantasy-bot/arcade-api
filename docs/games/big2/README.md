# Big 2 Card Game API Documentation

Big 2 is a trick-taking card game where players compete to be the first to play all their cards. Players take turns playing cards or combinations of cards that beat the previous play.

## Game Rules

- Players: 2-4
- Deck: Standard 52-card deck
- Card ranking: 3 (lowest) to 2 (highest)
- Card combinations:
  - Single card
  - Pair
  - Triple
  - Straight (5+ cards in sequence)
  - Full house (3 of a kind + pair)
  - Four of a kind
  - Straight flush (straight with same suit)
- First play must be 3 of clubs
- Players must beat previous play or pass
- First player to finish wins

## API Endpoints

### Create New Game
```http
POST /games/big2/new
```

Creates a new Big 2 game.

Example:
```bash
curl -X POST http://localhost:8000/games/big2/new
```

Response:
```json
{
    "game_id": "big2-20250521-231234"
}
```

### Make Move
```http
POST /games/big2/{game_id}/move
```

Make a move in the game.

Required parameters:
- `cards`: List of cards to play
  - Each card is a dictionary with:
    - `suit`: ♠, ♥, ♦, ♣
    - `rank`: 3-2, J, Q, K, A

Example:
```bash
curl -X POST http://localhost:8000/games/big2/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "cards": [
            {"suit": "♣", "rank": "3"}
        ]
    }'
```

### Get Game State
```http
GET /games/big2/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "hands": {
        "0": [
            {"suit": "♠", "rank": "4"},
            {"suit": "♠", "rank": "5"},
            {"suit": "♠", "rank": "6"}
        ],
        "1": [
            {"suit": "♥", "rank": "4"},
            {"suit": "♥", "rank": "5"},
            {"suit": "♥", "rank": "6"}
        ]
    },
    "current_player": 0,
    "last_play": [
        {"suit": "♣", "rank": "3"}
    ],
    "last_player": 0,
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid card format
- 400 Bad Request: Invalid card combination
- 400 Bad Request: Not beating previous play
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Card-based gameplay
- Multiple card combinations
- Card ranking system
- Player turn management
- Game end detection
- Winner determination
