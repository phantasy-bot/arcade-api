# Settlers of Catan API Documentation

Settlers of Catan is a strategy board game where players compete to establish settlements on an island. Players collect resources (wood, brick, sheep, wheat, and ore) to build settlements, cities, and roads.

## Game Rules

- Players: 3-4
- Resources: Wood, Brick, Sheep, Wheat, Ore
- Buildings:
  - Settlements (1 point)
  - Cities (2 points)
  - Roads
- Victory: 10 victory points
- Special cards:
  - Knight: Move robber
  - Road Building: Build 2 roads
  - Year of Plenty: Get 2 resources
  - Monopoly: Take all resources from other players
- Longest Road: 2 points
- Largest Army: 2 points

## API Endpoints

### Create New Game
```http
POST /games/catan/new
```

Creates a new Catan game.

Example:
```bash
curl -X POST http://localhost:8000/games/catan/new
```

Response:
```json
{
    "game_id": "catan-20250521-234603"
}
```

### Make Move
```http
POST /games/catan/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "build", "trade", or "use_dev_card"
- For "build" action:
  - `type`: "settlement", "city", or "road"
  - `position`: [x, y] coordinates
- For "trade" action:
  - `offer`: Resources to offer
    - "wood": number
    - "brick": number
    - "sheep": number
    - "wheat": number
    - "ore": number
  - `request`: Resources to request
    - Same format as offer
- For "use_dev_card" action:
  - `card`: "knight", "road_building", "year_of_plenty", or "monopoly"

Example (build settlement):
```bash
curl -X POST http://localhost:8000/games/catan/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "build",
        "type": "settlement",
        "position": [0, 0]
    }'
```

Example (trade resources):
```bash
curl -X POST http://localhost:8000/games/catan/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "trade",
        "offer": {
            "wood": 2,
            "brick": 1
        },
        "request": {
            "wheat": 1,
            "sheep": 1
        }
    }'
```

Example (use development card):
```bash
curl -X POST http://localhost:8000/games/catan/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "use_dev_card",
        "card": "knight"
    }'
```

### Get Game State
```http
GET /games/catan/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "board": {
        "[0,0]": {
            "resource": "wood",
            "number": 6
        },
        "[0,1]": {
            "resource": "brick",
            "number": 8
        }
    },
    "current_player": 0,
    "phase": "play",
    "resources": {
        "0": {
            "wood": 5,
            "brick": 3,
            "sheep": 2,
            "wheat": 4,
            "ore": 1
        }
    },
    "buildings": {
        "0": [
            {
                "type": "settlement",
                "position": [0, 0]
            }
        ]
    },
    "roads": {
        "0": [
            {
                "position": [[0, 0], [0, 1]]
            }
        ]
    },
    "victory_points": {
        "0": 1
    },
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid action
- 400 Bad Request: Invalid position
- 400 Bad Request: Insufficient resources
- 400 Bad Request: Not your turn
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Resource management
- Building placement
- Trading system
- Development cards
- Victory point tracking
- Longest road tracking
- Largest army tracking
- Game end detection
- Winner determination
