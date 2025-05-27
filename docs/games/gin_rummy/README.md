# Gin Rummy Game API Documentation

Gin Rummy is a card game where players try to form melds (sets or runs) and minimize their deadwood points. The game is played with a standard 52-card deck.

## Game Rules

- Players: 2
- Deck: 52 cards
- Hand: 10 cards
- Melds:
  - Sets: 3 or 4 cards of the same rank
  - Runs: 3 or more consecutive cards of the same suit
- Deadwood: Cards not in melds
- Points:
  - Number cards: Face value
  - Face cards: 10 points
  - Knock: End turn with 10 or fewer deadwood points
  - Undercut: Opponent wins if they have fewer deadwood points
- Win: Knock with fewer deadwood points than opponent

## API Endpoints

### Create New Game
```http
POST /games/gin_rummy/new
```

Creates a new Gin Rummy game.

Example:
```bash
curl -X POST http://localhost:8000/games/gin_rummy/new
```

Response:
```json
{
    "game_id": "gin_rummy-20250522-002031"
}
```

### Make Move
```http
POST /games/gin_rummy/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "draw", "discard", or "knock"
- For "draw" action:
  - `source`: "deck" or "discard"
- For "discard" action:
  - `card`: Card to discard
    - `suit`: ♠, ♥, ♦, or ♣
    - `rank`: 1-13
- For "knock" action: No additional parameters

Example (draw from deck):
```bash
curl -X POST http://localhost:8000/games/gin_rummy/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "draw",
        "source": "deck"
    }'
```

Example (discard card):
```bash
curl -X POST http://localhost:8000/games/gin_rummy/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "discard",
        "card": {
            "suit": "♠",
            "rank": 7
        }
    }'
```

Example (knock):
```bash
curl -X POST http://localhost:8000/games/gin_rummy/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "knock"
    }'
```

### Get Game State
```http
GET /games/gin_rummy/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "current_player": 0,
    "phase": "play",
    "hands": {
        "0": [
            {
                "suit": "♠",
                "rank": 7
            },
            {
                "suit": "♥",
                "rank": 9
            }
        ],
        "1": [
            {
                "suit": "♦",
                "rank": 5
            },
            {
                "suit": "♣",
                "rank": 10
            }
        ]
    },
    "discard_pile": [
        {
            "suit": "♠",
            "rank": 3
        }
    ],
    "deadwood": {
        "0": 15,
        "1": 20
    },
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid action
- 400 Bad Request: Invalid card
- 400 Bad Request: Invalid source
- 400 Bad Request: Card not in hand
- 400 Bad Request: Not your turn
- 400 Bad Request: Cannot knock (too many deadwood points)
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Card drawing
- Card discarding
- Meld detection
- Deadwood calculation
- Knock mechanism
- Undercut detection
- Game end detection
- Winner determination
