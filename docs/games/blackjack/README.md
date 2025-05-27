# Blackjack Game API Documentation

Blackjack is a casino banking game with a long history. The game is played with one or more decks of 52 cards. The objective of the game is to beat the dealer by obtaining a hand total of 21 or as close to 21 as possible without going over.

## Game Rules

- Deck: 6 decks of standard 52-card decks
- Minimum bet: $10
- Maximum bet: $1000
- Dealer must hit on 16 and stand on 17
- Players can:
  - Hit: Take another card
  - Stand: Keep current hand
  - Double: Double bet and take one more card
  - Split: Split a pair into two hands
- Blackjack pays 3:2
- Insurance is not available
- Surrender is not available

## API Endpoints

### Create New Game
```http
POST /games/blackjack/new
```

Creates a new Blackjack game.

Example:
```bash
curl -X POST http://localhost:8000/games/blackjack/new
```

Response:
```json
{
    "game_id": "blackjack-20250521-221750"
}
```

### Make Bet
```http
POST /games/blackjack/{game_id}/bet
```

Make initial bets and start the game.

Required parameters:
- `bets`: Array of bet amounts (one for each hand)

Example:
```bash
curl -X POST http://localhost:8000/games/blackjack/{game_id}/bet \
    -H "Content-Type: application/json" \
    -d '{
        "bets": [100]
    }'
```

### Make Action
```http
POST /games/blackjack/{game_id}/action
```

Make a player action on a specific hand.

Required parameters:
- `action`: "hit", "stand", "double", or "split"
- `hand_idx`: Index of the hand to act on (optional, defaults to current hand)

Example:
```bash
curl -X POST http://localhost:8000/games/blackjack/{game_id}/action \
    -H "Content-Type: application/json" \
    -d '{
        "action": "hit",
        "hand_idx": 0
    }'
```

### Get Game State
```http
GET /games/blackjack/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "dealer": {
        "visible_card": {"rank": "A", "suite": "♠", "face_up": true},
        "value": 11,
        "hand": {
            "cards": [
                {"rank": "A", "suite": "♠", "face_up": true},
                {"rank": "K", "suite": "♥", "face_up": true}
            ],
            "value": 21,
            "is_bust": false,
            "is_blackjack": true
        }
    },
    "player_hands": [
        {
            "cards": [
                {"rank": "10", "suite": "♦", "face_up": true},
                {"rank": "J", "suite": "♣", "face_up": true},
                {"rank": "K", "suite": "♠", "face_up": true}
            ],
            "value": 30,
            "is_bust": true,
            "is_blackjack": false,
            "bet": 100,
            "is_split": false,
            "is_double": false,
            "is_surrendered": false
        }
    ],
    "current_hand_idx": 0,
    "legal_actions": ["stand"],
    "game_over": true,
    "outcomes": [
        {
            "hand": {
                "cards": [
                    {"rank": "10", "suite": "♦", "face_up": true},
                    {"rank": "J", "suite": "♣", "face_up": true},
                    {"rank": "K", "suite": "♠", "face_up": true}
                ],
                "value": 30,
                "is_bust": true,
                "is_blackjack": false,
                "bet": 100,
                "is_split": false,
                "is_double": false,
                "is_surrendered": false
            },
            "outcome": "lose",
            "payout": -100
        }
    ]
}
```

## Error Conditions

- 400 Bad Request: Invalid action (e.g., trying to hit on a bust hand)
- 400 Bad Request: Invalid bet amount (must be between min and max bet)
- 400 Bad Request: Invalid hand index
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each action
