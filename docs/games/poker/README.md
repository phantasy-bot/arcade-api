# Poker Card Game API Documentation

Poker is a classic card game where players bet on the strength of their hand. This implementation features Texas Hold'em style poker with community cards and betting rounds.

## Game Rules

- Players: 2-4
- Deck: Standard 52-card deck
- Deal: 2 cards to each player
- Community cards: 5 cards shared by all players
- Betting rounds:
  - Pre-flop (2 cards)
  - Flop (3 cards)
  - Turn (4th card)
  - River (5th card)
- Hand rankings:
  1. Royal Flush
  2. Straight Flush
  3. Four of a Kind
  4. Full House
  5. Flush
  6. Straight
  7. Three of a Kind
  8. Two Pair
  9. Pair
  10. High Card
- Actions:
  - Fold: Give up hand
  - Check: Pass if no bet
  - Call: Match current bet
  - Bet: Make initial bet
  - Raise: Increase bet
- Blinds: Small blind and big blind
- Win: Highest hand wins pot

## API Endpoints

### Create New Game
```http
POST /games/poker/new
```

Creates a new Poker game.

Optional parameters:
- `small_blind`: Amount of small blind (default: 10)

Example:
```bash
curl -X POST http://localhost:8000/games/poker/new
```

Response:
```json
{
    "game_id": "poker-20250521-233439"
}
```

### Make Move
```http
POST /games/poker/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "fold", "check", "call", "bet", or "raise"
- For "bet" and "raise" actions:
  - `amount`: Amount to bet/raise

Example (bet):
```bash
curl -X POST http://localhost:8000/games/poker/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "bet",
        "amount": 50
    }'
```

Example (fold):
```bash
curl -X POST http://localhost:8000/games/poker/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "fold"
    }'
```

### Get Game State
```http
GET /games/poker/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "hands": {
        "0": [
            {"suit": "♠", "rank": "A"},
            {"suit": "♥", "rank": "K"}
        ],
        "1": [
            {"suit": "♦", "rank": "Q"},
            {"suit": "♣", "rank": "J"}
        ]
    },
    "community_cards": [
        {"suit": "♠", "rank": "10"},
        {"suit": "♠", "rank": "J"},
        {"suit": "♠", "rank": "Q"},
        {"suit": "♠", "rank": "K"},
        {"suit": "♠", "rank": "A"}
    ],
    "current_player": 0,
    "pot": 200,
    "bets": {
        "0": 100,
        "1": 100
    },
    "current_bet": 100,
    "round": 4,
    "game_over": true,
    "winner": 0
}
```

## Error Conditions

- 400 Bad Request: Invalid action
- 400 Bad Request: Invalid amount
- 400 Bad Request: Not your turn
- 400 Bad Request: Invalid bet amount
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Texas Hold'em style poker
- Multiple players
- Community cards
- Betting system
- Hand evaluation
- Turn management
- Game end detection
- Winner determination
