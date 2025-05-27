# Hanafuda Card Game API Documentation

Hanafuda is a traditional Japanese card game played with a 48-card deck, featuring cards with beautiful illustrations of flowers and other elements. Players take turns playing cards to capture cards from the field, with the goal of accumulating the most points.

## Game Rules

- Players: 2
- Deck: 48 Hanafuda cards
- Card types:
  - Bright cards (20 points)
  - Animal cards (10 points)
  - Ribbon cards (5 points)
  - Plain cards (1 point)
- Deal: 8 cards to each player
- Field: 8 cards placed face up
- Capture rules:
  - Same month cards
  - Bright cards capture plain cards
  - Animal cards capture animal cards of same month
  - Ribbon cards capture ribbon cards of same month
- After playing a card:
  - Draw a card from deck (if available)
  - If no capture, place card on field
- Game ends when deck is empty and players have no cards
- Win: Player with highest score

## API Endpoints

### Create New Game
```http
POST /games/hanafuda/new
```

Creates a new Hanafuda game.

Example:
```bash
curl -X POST http://localhost:8000/games/hanafuda/new
```

Response:
```json
{
    "game_id": "hanafuda-20250521-233109"
}
```

### Make Move
```http
POST /games/hanafuda/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "play"
- For "play" action:
  - `card`: Card to play
    - `month`: 1-12
    - `rank`: Card name (e.g., "Pine", "Crane", "Red Ribbon", "Plain")
    - `points`: 1, 5, 10, or 20
    - `suit`: "Bright", "Animal", "Ribbon", or "Plain"

Example:
```bash
curl -X POST http://localhost:8000/games/hanafuda/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "play",
        "card": {
            "month": 1,
            "rank": "Pine",
            "points": 20,
            "suit": "Bright"
        }
    }'
```

### Get Game State
```http
GET /games/hanafuda/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "hands": {
        "0": [
            {
                "month": 1,
                "rank": "Crane",
                "points": 10,
                "suit": "Animal"
            },
            {
                "month": 2,
                "rank": "Plum",
                "points": 20,
                "suit": "Bright"
            }
        ],
        "1": [
            {
                "month": 3,
                "rank": "Cherry",
                "points": 20,
                "suit": "Bright"
            },
            {
                "month": 4,
                "rank": "Wisteria",
                "points": 20,
                "suit": "Bright"
            }
        ]
    },
    "current_player": 0,
    "field": [
        {
            "month": 5,
            "rank": "Iris",
            "points": 20,
            "suit": "Bright"
        },
        {
            "month": 6,
            "rank": "Peony",
            "points": 20,
            "suit": "Bright"
        }
    ],
    "scores": {
        "0": 30,
        "1": 25
    },
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid card format
- 400 Bad Request: Invalid action
- 400 Bad Request: Card not in hand
- 400 Bad Request: Invalid play
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Hanafuda card deck
- Multiple players
- Card capturing
- Point scoring
- Turn management
- Game end detection
- Winner determination
