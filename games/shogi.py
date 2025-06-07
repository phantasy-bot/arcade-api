from typing import Dict, Any, List, Optional
from game_abc import AbstractGame, GameMove # Assuming GameMove might be used later
import time

# Player identifiers
SENTE = "Sente"  # Black, traditionally plays first
GOTE = "Gote"    # White, traditionally plays second


class ShogiGame(AbstractGame):
    """Implements the game of Shogi."""

    def __init__(self, game_id: str):
        super().__init__(game_id)
        # Note: Game state (board, current_player) is typically set by self.initialize_game(),
        # which is called by test setup or game management logic, not directly in __init__ here.
        # AbstractGame.__init__ calls self._load_game_state() which calls self._restore_game_state().
        # If no saved state, initialize_game() is expected to be called explicitly.

    def initialize_game(self) -> Dict[str, Any]:
        """Initializes the game state for a new Shogi game."""
        self.board: List[List[Optional[str]]] = [[None for _ in range(9)] for _ in range(9)]
        self.current_player: str = SENTE
        self.game_over: bool = False
        self.winner: Optional[str] = None
        self.captured_by_sente: List[str] = []
        self.captured_by_gote: List[str] = []
        # TODO: Populate the board with initial Shogi pieces
        
        self.history.current_state = self.get_game_state()
        self.history._persist_to_disk() # Ensure initial state is saved for a new game
        return self.get_game_state()

    def _restore_game_state(self):
        """Restores game state from self.history.current_state."""
        state = self.history.current_state
        self.board = state.get('board', [[None for _ in range(9)] for _ in range(9)])
        self.current_player = state.get('current_player', SENTE)
        self.game_over = state.get('game_over', False)
        self.winner = state.get('winner', None)
        self.captured_by_sente = state.get('captured_by_sente', [])
        self.captured_by_gote = state.get('captured_by_gote', [])

    def get_game_state(self) -> Dict[str, Any]:
        """Returns the current state of the game."""
        return {
            "board": self.board,
            "current_player": self.current_player,
            "game_over": self.game_over,
            "winner": self.winner,
            "captured_by_sente": self.captured_by_sente,
            "captured_by_gote": self.captured_by_gote,
            "game_id": self.game_id
        }

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validates if a move is legal."""
        player = move_data.get("player")
        if player != self.current_player:
            return False
        # TODO: Implement actual Shogi move validation logic
        return True

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a move and updates game state."""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        move = GameMove(
            player=self.current_player, 
            move_data=move_data, 
            timestamp=time.time()
        )
        self.history.add_move(move) 

        if self.current_player == SENTE:
            self.current_player = GOTE
        else:
            self.current_player = SENTE
        
        # TODO: Check for win/draw conditions
        self.history.current_state = self.get_game_state() # Update state in history after move
        # self.history.add_move already persists.
        return self.get_game_state()

    def is_game_over(self) -> bool:
        """Checks if the game is over."""
        # TODO: Implement Shogi game over conditions
        return self.game_over

    def get_winner(self) -> Optional[str]:
        """Gets the winner if the game is over."""
        # TODO: Determine winner based on game state
        return self.winner

# Note: Now ShogiGame directly implements initialize_game and make_move as required by AbstractGame's abstract declarations.
