# Go Fish Game API Documentation

Go Fish is a classic card game where players try to collect sets of four cards (books) by asking other players for cards of a specific rank. If the player doesn't have the card, they must "go fish" from the deck.

## Game Rules

- Players: 2-4
- Deck: Standard 52-card deck
- Initial hand: 7 cards
- Book: 4 cards of the same rank
- Players take turns asking for cards
- Must have the rank in hand to ask
- If player has card, they must give it
- If no card, player "goes fish" from deck
- Player gets another turn if successful
- Game ends when deck is empty and no more moves
- Winner has most books

## API Endpoints

### Create New Game
```http
POST /games/gofish/new
```

Creates a new Go Fish game.

Example:
```bash
curl -X POST http://localhost:8000/games/gofish/new
```

Response:
```json
{
    "game_id": "gofish-20250521-230714"
}
```

### Make Move
```http
POST /games/gofish/{game_id}/move
```

Make a move in the game.

Required parameters:
- `target_player`: Player to ask (0-3)
- `rank`: Card rank to ask for (1-13)

Example:
```bash
curl -X POST http://localhost:8000/games/gofish/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "target_player": 1,
        "rank": 5
    }'
```

### Get Game State
```http
GET /games/gofish/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "hands": {
        "0": [
            {"suit": "♠", "rank": 5},
            {"suit": "♥", "rank": 5},
            {"suit": "♦", "rank": 5}
        ],
        "1": [
            {"suit": "♣", "rank": 5},
            {"suit": "♠", "rank": 6},
            {"suit": "♥", "rank": 6}
        ]
    },
    "current_player": 0,
    "fish_pile_size": 34,
    "book_count": {
        "0": 2,
        "1": 1
    },
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid target player
- 400 Bad Request: Invalid rank
- 400 Bad Request: Asking for card not in hand
- 400 Bad Request: Asking self
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard 52-card deck
- Book collection
- Turn-based gameplay
- Fish pile management
- Game end detection
- Winner determination
