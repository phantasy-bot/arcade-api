# Daifugo Card Game API Documentation

Daifugo is a Japanese card game where players compete to be the first to play all their cards. Players take turns playing cards or combinations of cards that beat the previous play. The game is similar to Big 2 but with a unique ranking system and roles.

## Game Rules

- Players: 2-4
- Deck: 54 cards (standard deck + 2 jokers)
- Card ranking: 3 (lowest) to 2 (highest), with jokers being highest
- Card combinations:
  - Single card
  - Pair
  - Triple
  - Straight (3+ cards in sequence)
  - Full house (3 of a kind + pair)
  - Four of a kind
  - Straight flush (straight with same suit)
- First play must be 3 of clubs
- Players must beat previous play or pass
- First player to finish wins
- Roles:
  - Daifugo (Winner)
  - Fugo (Second place)
  - Heimin (Third place)
  - Chonin (Fourth place)

## API Endpoints

### Create New Game
```http
POST /games/daifugo/new
```

Creates a new Daifugo game.

Example:
```bash
curl -X POST http://localhost:8000/games/daifugo/new
```

Response:
```json
{
    "game_id": "daifugo-20250521-231529"
}
```

### Make Move
```http
POST /games/daifugo/{game_id}/move
```

Make a move in the game.

Required parameters:
- `cards`: List of cards to play
  - Each card is a dictionary with:
    - `suit`: ♠, ♥, ♦, ♣, or empty for jokers
    - `rank`: 3-2, J, Q, K, A, joker, or Joker

Example:
```bash
curl -X POST http://localhost:8000/games/daifugo/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "cards": [
            {"suit": "♣", "rank": "3"}
        ]
    }'
```

### Get Game State
```http
GET /games/daifugo/{game_id}/state
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
    "roles": ["Daifugo", "Fugo", "Heimin", "Chonin"],
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
- Role assignment
- Game end detection
- Winner determination
