# Crazy Eights Card Game API Documentation

Crazy Eights is a classic card game where players try to get rid of all their cards by playing cards that match either the suit or rank of the top card on the discard pile. Eights are wild and can be played on any card.

## Game Rules

- Players: 2-4
- Deck: Standard 52-card deck
- Deal: 5 cards to each player
- Play: Match suit or rank of top card
- Special cards:
  - 8: Wild card (can change suit)
  - Draw from deck if no valid play
  - Discard pile is reshuffled when deck is empty
- Win: First player to get rid of all cards

## API Endpoints

### Create New Game
```http
POST /games/crazy8s/new
```

Creates a new Crazy Eights game.

Example:
```bash
curl -X POST http://localhost:8000/games/crazy8s/new
```

Response:
```json
{
    "game_id": "crazy8s-20250521-232952"
}
```

### Make Move
```http
POST /games/crazy8s/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "play" or "draw"
- For "play" action:
  - `card`: Card to play
    - `suit`: ♠, ♥, ♦, ♣
    - `rank`: 2-10, J, Q, K, A
  - `new_suit`: (optional) New suit when playing an 8

Example (play a card):
```bash
curl -X POST http://localhost:8000/games/crazy8s/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "play",
        "card": {
            "suit": "♠",
            "rank": "9"
        }
    }'
```

Example (play an 8 and change suit):
```bash
curl -X POST http://localhost:8000/games/crazy8s/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "play",
        "card": {
            "suit": "♦",
            "rank": "8"
        },
        "new_suit": "♥"
    }'
```

Example (draw a card):
```bash
curl -X POST http://localhost:8000/games/crazy8s/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "draw"
    }'
```

### Get Game State
```http
GET /games/crazy8s/{game_id}/state
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
    "discard_pile_top": {
        "suit": "♣",
        "rank": "3"
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

- Card-based gameplay
- Multiple players
- Card matching
- Wild cards (8s)
- Draw pile management
- Discard pile management
- Game end detection
- Winner determination
