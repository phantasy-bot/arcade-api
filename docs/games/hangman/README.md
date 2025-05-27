# Hangman Game API Documentation

Hangman is a word guessing game where players try to guess a word by suggesting letters within a limited number of guesses.

## Game Rules

- Word length: Varies
- Incorrect guesses: 6 maximum
- Guesses: One letter at a time
- Win: Guess all letters correctly
- Lose: Reach maximum incorrect guesses

## API Endpoints

### Create New Game
```http
POST /games/hangman/new
```

Creates a new Hangman game.

Optional parameters:
- `word_list`: List of words to choose from

Example:
```bash
curl -X POST http://localhost:8000/games/hangman/new
```

Response:
```json
{
    "game_id": "hangman-20250522-004318"
}
```

### Make Move
```http
POST /games/hangman/{game_id}/move
```

Make a move in the game.

Required parameters:
- `action`: "guess"
- `letter`: Letter to guess

Example:
```bash
curl -X POST http://localhost:8000/games/hangman/{game_id}/move \
    -H "Content-Type: application/json" \
    -d '{
        "action": "guess",
        "letter": "p"
    }'
```

### Get Game State
```http
GET /games/hangman/{game_id}/state
```

Get the current state of the game.

Response:
```json
{
    "current_word": "_ython",
    "guesses": ["p"],
    "incorrect_guesses": [],
    "max_incorrect": 6,
    "phase": "play",
    "game_over": false,
    "winner": null
}
```

## Error Conditions

- 400 Bad Request: Invalid action
- 400 Bad Request: Invalid letter
- 400 Bad Request: Letter already guessed
- 404 Not Found: Game not found
- 500 Internal Server Error: Server error

## State Management

- Game state is persisted to disk in the `game_data` directory
- Each game has a unique ID that persists between server restarts
- Game history can be retrieved and restored at any time
- State is automatically saved after each move

## Game Features

- Word guessing
- Letter validation
- Incorrect guess tracking
- Word masking
- Game end detection
- Winner determination
