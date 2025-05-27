# Jaipur Game API Documentation

Jaipur is a two-player card game where players take on the role of merchants competing to earn the most money by trading goods and camels.

## Game Rules

- Players: 2
- Goods: Diamond, Gold, Silver, Cloth, Spice, Camels
- Market: 5 cards visible
- Actions:
  - Take a single good card
  - Take all camels
  - Exchange cards
  - Sell goods
- Victory: Most points when game ends

## API Endpoints

### Create New Game
```http
POST /games/jaipur/new
```

Creates a new Jaipur game.

Example:
```bash
curl -X POST http://localhost:8000/games/jaipur/new
```

Response:
```json
{
    "game_id": "jaipur-20250522-005117"
}
```

### Make Move
```http
POST /games/jaipur/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "take", "sell", or "exchange"
- For "take" action:
  - `card`: Type of card to take
- For "sell" action:
  - `type`: Type of good to sell
- For "exchange" action:
  - `give`: List of cards to give
  - `take`: List of cards to take

Example (take a card):
```bash
curl -X POST http://localhost:8000/games/jaipur/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "take",
        "card": "diamond"
    }'
```

Example (sell goods):
```bash
curl -X POST http://localhost:8000/games/jaipur/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "sell",
        "type": "cloth"
    }'
```

Example (exchange cards):
```bash
curl -X POST http://localhost:8000/games/jaipur/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "exchange",
        "give": [{"type": "diamond"}, {"type": "gold"}],
        "take": [{"type": "silver"}, {"type": "cloth"}]
    }'
```

### Get Game State
```http
GET /games/jaipur/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "current_player": 0,
    "phase": "play",
    "market": [
        {
            "type": "diamond",
            "value": 1
        },
        {
            "type": "gold",
            "value": 1
        }
    ],
    "camel_market": [
        {
            "type": "camel",
            "value": 1
        }
    ],
    "camel_herd": [
        {
            "type": "camel",
            "value": 1
        }
    ],
    "players": [
        {
            "diamond": 2,
            "gold": 1,
            "camel": 3
        },
        {
            "silver": 2,
            "cloth": 1
        }
    ],
    "tokens": {
        "diamond": [5, 3, 2, 1],
        "gold": [5, 3, 2, 1],
        "silver": [5, 3, 2, 1],
        "cloth": [5, 3, 2, 1],
        "spice": [5, 3, 2, 1],
        "camel": [5, 4, 3, 2, 2, 2, 1, 1, 1, 1]
    },
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid action
- 400 Bad Request: Invalid card type
- 400 Bad Request: Not enough cards to sell
- 400 Bad Request: Not enough cards to exchange
- 400 Bad Request: Invalid exchange
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Card taking
- Card selling
- Card exchanging
- Camel management
- Token tracking
- Game end detection
- Winner determination
