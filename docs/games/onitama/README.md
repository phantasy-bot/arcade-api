# Onitama Game API Documentation

Onitama is a strategy board game where players move pieces using special cards. Each player has two cards that define how pieces can move, and they take turns moving pieces to capture the opponent's master piece or reach the opponent's side of the board.

## Game Rules

- Board size: 5x5
- Players: Blue and Red
- Pieces:
  - 5 regular pieces per player
  - 1 Master piece per player
- Cards:
  - Each player has 2 active cards
  - Cards define piece movement
  - Cards are exchanged after each move
- Win conditions:
  - Capture opponent's Master piece
  - Move your Master piece to opponent's side
  - Opponent has no valid moves

## API Endpoints

### Create New Game
```http
POST /games/onitama/new
```

Creates a new Onitama game.

Example:
```bash
curl -X POST http://localhost:8000/games/onitama/new
```

Response:
```json
{
    "game_id": "onitama-20250521-225534"
}
```

### Make Move
```http
POST /games/onitama/{game_id}/move
```

Make a move in the game.

Required parameters:
- `card`: Name of the card to use
- `x`: Current row position (0-4)
- `y`: Current column position (0-4)
- `nx`: New row position (0-4)
- `ny`: New column position (0-4)

Example:
```bash
curl -X POST http://localhost:8000/games/onitama/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "card": "Dragon",
        "x": 0,
        "y": 2,
        "nx": 1,
        "ny": 2
    }'
```

### Get Game State
```http
GET /games/onitama/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": [
        [1, 1, 3, 1, 1],  // Blue pieces (3 is Blue Master)
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [2, 2, 4, 2, 2]   // Red pieces (4 is Red Master)
    ],
    "current_player": "BLUE",
    "blue_cards": [
        {
            "name": "Dragon",
            "moves": [[0, 2], [0, -2], [-1, 0], [1, 0]],
            "active": true
        },
        {
            "name": "Crab",
            "moves": [[0, 2], [0, -1], [0, -2]],
            "active": true
        }
    ],
    "red_cards": [
        {
            "name": "Monkey",
            "moves": [[1, 1], [1, -1], [-1, 1], [-1, -1]],
            "active": true
        },
        {
            "name": "Rooster",
            "moves": [[1, 1], [1, -1], [-1, 0]],
            "active": true
        }
    ],
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid card name
- 400 Bad Request: Invalid position
- 400 Bad Request: Invalid move with card
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Standard 5x5 board
- Piece movement with cards
- Card exchange system
- Master piece capture
- Game end detection
- Winner determination
