# Uno Card Game API Documentation

Uno is a fast-paced card game where players try to get rid of all their cards. Special cards like Skip, Reverse, and Draw Two add strategic elements to the gameplay.

## Game Rules

- Players: 2-4
- Deck: 108 cards
- Card types:
  - Number cards (0-9) in 4 colors
  - Special cards:
    - Skip: Skip next player's turn
    - Reverse: Reverse play direction
    - Draw Two: Next player draws 2 cards
    - Wild: Choose any color
    - Wild Draw Four: Next player draws 4 cards and chooses color
- Deal: 7 cards to each player
- Play: Match color or number
- Special cards:
  - Skip: Skip next player
  - Reverse: Change direction
  - Draw Two: Next player draws 2 cards
  - Wild: Choose any color
  - Wild Draw Four: Next player draws 4 cards
- Win: First player to get rid of all cards

## API Endpoints

### Create New Game
```http
POST /games/uno/new
```

Creates a new Uno game.

Example:
```bash
curl -X POST http://localhost:8000/games/uno/new
```

Response:
```json
{
    "game_id": "uno-20250521-233743"
}
```

### Make Move
```http
POST /games/uno/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "play", "draw", or "choose_color"
- For "play" action:
  - `card`: Card to play
    - `color`: red, yellow, green, blue, or wild
    - `value`: 0-9, skip, reverse, draw2, wild, or wild4
    - `special`: true if special card
  - `new_color`: (optional) New color when playing wild card
- For "draw" action: No additional parameters
- For "choose_color" action:
  - `color`: New color to choose

Example (play a card):
```bash
curl -X POST http://localhost:8000/games/uno/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "play",
        "card": {
            "color": "red",
            "value": "5",
            "special": false
        }
    }'
```

Example (play a wild card and choose color):
```bash
curl -X POST http://localhost:8000/games/uno/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "play",
        "card": {
            "color": "wild",
            "value": "wild",
            "special": true
        },
        "new_color": "blue"
    }'
```

Example (draw a card):
```bash
curl -X POST http://localhost:8000/games/uno/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "draw"
    }'
```

### Get Game State
```http
GET /games/uno/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "hands": {
        "0": [
            {
                "color": "red",
                "value": "5",
                "special": false,
                "wild": false
            },
            {
                "color": "blue",
                "value": "skip",
                "special": true,
                "wild": false
            }
        ],
        "1": [
            {
                "color": "green",
                "value": "7",
                "special": false,
                "wild": false
            },
            {
                "color": "yellow",
                "value": "draw2",
                "special": true,
                "wild": false
            }
        ]
    },
    "current_player": 0,
    "discard_pile_top": {
        "color": "blue",
        "value": "9",
        "special": false,
        "wild": false
    },
    "direction": 1,
    "draw_count": 0,
    "skip_count": 0,
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

- Uno card deck
- Multiple players
- Special cards
- Color matching
- Number matching
- Draw pile management
- Discard pile management
- Game end detection
- Winner determination
