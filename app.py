from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Optional
from game_state_manager import GameStateManager
from game_manager import GameManager

app = FastAPI(title="Game Arcade API")

# Initialize state manager
state_manager = GameStateManager()


@app.get("/games")
async def list_games():
    """List all available game types"""
    return [
        "tic-tac-toe",
        "connect-four",
        "omok",
        "chess",
        "shogi",
        "blackjack",
        "war",
        "cuttle",
        "go",
        "checkers",
        "mancala",
        "othello",
        "onitama",
        "tienlen",
        "gofish",
        "bs",
        "big2",
        "daifugo",
        "connect6",
        "tictactoe3d",
        "crazy8s",
        "hanafuda",
        "poker",
        "uno",
        "catan",
        "battleship",
        "scrabble",
        "concentration",
        "gin_rummy",
        "hangman",
        "jaipur",
    ]

    def restore_game(self, game_type: str, game_id: str, history_json: str) -> None:
        """Restore game state from JSON history"""
        game = self.get_game(game_type, game_id)
        game.history.deserialize(history_json)


# Create game manager instance
game_manager = GameManager()


@app.get("/games")
async def list_games():
    """List all available game types"""
    return list(game_manager.game_types.keys())


@app.post("/games/{game_type}/new")
async def create_new_game(game_type: str):
    """Create a new game instance"""
    game_id = game_manager.create_game(game_type)
    return {"game_id": game_id}


@app.post("/games/{game_type}/{game_id}/move")
async def make_move(game_type: str, game_id: str, move_data: Dict[str, Any]):
    """Make a move in the game"""
    game = game_manager.get_game(game_type, game_id)
    try:
        state = game.make_move(move_data)
        return state
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/games/{game_type}/{game_id}/state")
async def get_game_state(game_type: str, game_id: str):
    """Get current game state"""
    game = game_manager.get_game(game_type, game_id)
    return game.get_game_state()


@app.get("/games/{game_type}/{game_id}/history")
async def get_game_history(game_type: str, game_id: str):
    """Get game history"""
    return game_manager.get_game_history(game_type, game_id)


@app.post("/games/{game_type}/{game_id}/restore")
async def restore_game_state(game_type: str, game_id: str, history_json: str):
    """Restore game state from history"""
    game_manager.restore_game(game_type, game_id, history_json)
    return {"status": "restored"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=4444)
