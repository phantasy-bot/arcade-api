# War Card Game API Documentation

War is a simple card game where players compare cards and the higher card wins. If the cards are of equal value, a "war" occurs and additional cards are played until a winner is determined.

## Game Rules

- Standard 52-card deck
- Cards ranked from 2 (lowest) to Ace (highest)
- Players start with equal number of cards
- Each round:
  - Both players reveal a card
  - Higher card wins both cards
  - If cards are equal, a "war" occurs:
    - Each player places three cards face down
    - Then one card face up
    - Higher face-up card wins all cards
- Game ends when one player has all cards
- Maximum 1000 rounds to prevent infinite games

## API Endpoints

### Create New Game
```http
POST /games/war/new
```

Creates a new War game.

Example:
```bash
curl -X POST http://localhost:8000/games/war/new
```

Response:
```json
{
    "game_id": "war-20250521-222028"
}
```

### Play Round
```http
POST /games/war/{game_id}/play
```

Play a round of War.

Example:
```bash
curl -X POST http://localhost:8000/games/war/{game_id}/play
```

### Get Game State
```http
GET /games/war/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "round": 12,
    "player_cards": 23,
    "computer_cards": 29,
    "current_battle": [
        {"rank": "A", "suite": "♠", "value": 14},
        {"rank": "K", "suite": "♥", "value": 13}
    ],
    "war_cards": [
        {"rank": "10", "suite": "♦", "value": 10},
        {"rank": "J", "suite": "♣", "value": 11},
        {"rank": "Q", "suite": "♠", "value": 12}
    ],
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Maximum number of rounds reached
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard card ranking (2-10, J, Q, K, A)
- War resolution with three face-down cards
- Automatic game progression
- Round counter
- Card count tracking
- Draw detection
