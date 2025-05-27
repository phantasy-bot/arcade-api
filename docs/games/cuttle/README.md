# Cuttle Card Game API Documentation

Cuttle is a simple but strategic card game where players try to capture cards from the table by matching ranks or playing wild cards. The game is played with a standard 52-card deck.

## Game Rules

- Standard 52-card deck
- Players start with 4 cards each
- Cards are played to the table
- Capture cards by:
  - Matching rank
  - Playing a wild card (J, Q, K, A)
  - Playing a card next to a table card in sequence
- Scoring:
  - Regular cards: face value
  - Special cards (J, Q, K, A): 20 points
- Game ends when all cards are played
- Highest score wins

## API Endpoints

### Create New Game
```http
POST /games/cuttle/new
```

Creates a new Cuttle game.

Example:
```bash
curl -X POST http://localhost:8000/games/cuttle/new
```

Response:
```json
{
    "game_id": "cuttle-20250521-222218"
}
```

### Make Move
```http
POST /games/cuttle/{game_id}/play
```

Play a card from your hand.

Required parameters:
- `card_idx`: Index of the card to play (0-3)

Example:
```bash
curl -X POST http://localhost:8000/games/cuttle/{game_id}/play \
    -H "Content-Type: application/json" \
    -d '{
        "card_idx": 0
    }'
```

### Get Game State
```http
GET /games/cuttle/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "round": 12,
    "player_score": 123,
    "computer_score": 105,
    "player_hand": [
        {"rank": "A", "suite": "♠", "value": 14, "is_wild": true},
        {"rank": "7", "suite": "♥", "value": 7, "is_wild": false},
        {"rank": "K", "suite": "♦", "value": 13, "is_wild": true},
        {"rank": "4", "suite": "♣", "value": 4, "is_wild": false}
    ],
    "table": [
        {"rank": "8", "suite": "♠", "value": 8, "is_wild": false},
        {"rank": "J", "suite": "♥", "value": 11, "is_wild": true},
        {"rank": "Q", "suite": "♦", "value": 12, "is_wild": true}
    ],
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid card index
- 400 Bad Request: Maximum number of rounds reached
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard 52-card deck
- Wild cards (J, Q, K, A)
- Sequence matching
- Score tracking
- Computer opponent
- Card capture system
- Round counter
