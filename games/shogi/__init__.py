from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, List, Optional, Tuple, Any
from copy import deepcopy
import time


class ShogiPiece:
    """Represents a shogi piece"""

    def __init__(self, piece_type: str, color: str, promoted: bool = False):
        self.piece_type = piece_type.lower()
        self.color = color.lower()
        self.promoted = promoted
        self.promotion_rank = None  # For tracking promotion rank

    def __str__(self):
        return f"{self.color}{self.piece_type}{'+' if self.promoted else ''}"

    def __repr__(self):
        return str(self)

    def to_dict(self) -> Dict[str, str]:
        return {
            "type": self.piece_type,
            "color": self.color,
            "promoted": self.promoted,
            "promotion_rank": self.promotion_rank,
        }




class ShogiGame(AbstractGame):
    BOARD_SIZE = 9
    RANKS = 9
    FILES = 9

    # Piece types: K (King), G (Gold), S (Silver), N (Knight), L (Lance), P (Pawn), B (Bishop), R (Rook)
    # Promoted versions: +P (Promoted Pawn), +L (Promoted Lance), +N (Promoted Knight), +S (Promoted Silver)
    PIECE_TYPES = ["K", "G", "S", "N", "L", "P", "B", "R"]

    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.board: List[List[Optional[ShogiPiece]]] = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player: str = "w"
        self.hands: Dict[str, List[str]] = {"w": [], "b": []} # Stores piece types e.g. ["p", "p", "r"]
        self.move_history: List[Dict[str, Any]] = [] # For basic move logging, stores move_data dicts
        self.position_history: List[Tuple[Any, Any, str]] = [] # For Sennichite (board_tuple, hands_tuple, player)
        # Note: _restore_game_state (if called by super().__init__ or game manager) 
        # would typically populate these from a persisted state for an existing game.

    def _setup_board(self) -> List[List[Optional[ShogiPiece]]]:
        """Create and return the initial Shogi board configuration."""
        board = [[None] * self.FILES for _ in range(self.RANKS)]
        # Rank 0 (Black's back rank)
        board[0] = [
            ShogiPiece("l", "b"), ShogiPiece("n", "b"), ShogiPiece("s", "b"), ShogiPiece("g", "b"), ShogiPiece("k", "b"), ShogiPiece("g", "b"), ShogiPiece("s", "b"), ShogiPiece("n", "b"), ShogiPiece("l", "b"),
        ]
        # Rank 1 (Black's pieces)
        board[1][1] = ShogiPiece("r", "b") # Rook
        board[1][7] = ShogiPiece("b", "b") # Bishop
        # Rank 2 (Black's pawns)
        board[2] = [ShogiPiece("p", "b") for _ in range(self.FILES)]

        # Rank 6 (White's pawns)
        board[6] = [ShogiPiece("p", "w") for _ in range(self.FILES)]
        # Rank 7 (White's pieces)
        board[7][1] = ShogiPiece("b", "w") # Bishop
        board[7][7] = ShogiPiece("r", "w") # Rook
        # Rank 8 (White's back rank)
        board[8] = [
            ShogiPiece("l", "w"), ShogiPiece("n", "w"), ShogiPiece("s", "w"), ShogiPiece("g", "w"), ShogiPiece("k", "w"), ShogiPiece("g", "w"), ShogiPiece("s", "w"), ShogiPiece("n", "w"), ShogiPiece("l", "w"),
        ]
        return board

    def _restore_game_state(self):
        """Restore game attributes from self.history.current_state."""
        if self.history.current_state:  # Game state was loaded from persistence
            loaded_board_data = self.history.current_state.get('board')
            self.board = [[None] * self.FILES for _ in range(self.RANKS)] # Initialize with Nones
            if loaded_board_data:
                for r_idx, row_data in enumerate(loaded_board_data):
                    if r_idx < self.RANKS:
                        for c_idx, piece_data in enumerate(row_data):
                            if c_idx < self.FILES and piece_data:
                                piece = ShogiPiece(
                                    piece_type=piece_data['type'],
                                    color=piece_data['color'],
                                    promoted=piece_data.get('promoted', False)
                                )
                                if 'promotion_rank' in piece_data:
                                    piece.promotion_rank = piece_data['promotion_rank']
                                self.board[r_idx][c_idx] = piece
            
            self.current_player = self.history.current_state.get('current_player', "w")
            loaded_hands = self.history.current_state.get('hands', {"w": {}, "b": {}})
            self.hands = {
                "w": loaded_hands.get("w", {}),
                "b": loaded_hands.get("b", {})
            }
        else:  # New game or load failed, set defaults for initialize_game to use
            self.board = [[None] * self.FILES for _ in range(self.RANKS)]
            self.current_player = "w"
            self.hands = {"w": {}, "b": {}}

    def initialize_game(self) -> None:
        """Initialize a new game state. Typically called for tests or when starting a new game from scratch."""
        self.board = self._setup_board()
        self.hands = {"w": [], "b": []}
        self.current_player = "w"
        self.move_history = []
        self.position_history = []
        self._add_current_position_to_history() # Record initial position



    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        try:
            # Check if move is a drop
            if move_data.get("is_drop"):
                return self._validate_drop(move_data)

            from_row, from_col = move_data["from_row"], move_data["from_col"]
            to_row, to_col = move_data["to_row"], move_data["to_col"]

            # Check valid coordinates
            if not all(
                0 <= x < self.BOARD_SIZE for x in [from_row, from_col, to_row, to_col]
            ):
                return False

            # Check piece exists and is correct color
            piece = self.board[from_row][from_col]
            if not piece or piece.color != self.current_player:
                return False

            # Check destination is empty or has opponent's piece
            target_piece_at_destination = self.board[to_row][to_col]
            if target_piece_at_destination and target_piece_at_destination.color == self.current_player:
                return False

            # Validate move based on piece type first (before check validation)
            # This uses the current board state for path checking etc.
            # Validate move based on piece type first (before check validation)
            # This uses the current board state for path checking etc.
            is_piece_move_valid = self._validate_piece_move(
                piece.piece_type, piece.promoted, (from_row, from_col), (to_row, to_col), piece.color, self.board
            )
            if not is_piece_move_valid:
                return False

            # Check if move would put king in check
            # Create a temporary board state for check validation
            temp_board = [row[:] for row in self.board] # Shallow copy of rows, pieces are references
            temp_board[to_row][to_col] = piece
            temp_board[from_row][from_col] = None
            
            king_in_check_after_move = self._is_in_check(self.current_player, temp_board)
            if king_in_check_after_move:
                return False # Move is invalid if it leaves king in check

            return True # If all checks pass

        except KeyError:
            return False

    def _validate_drop(self, move_data: Dict[str, Any]) -> bool:
        """Validate a piece drop move"""
        try:
            to_row, to_col = move_data["to_row"], move_data["to_col"]
            piece_type = move_data["piece_type"]

            # Check valid coordinates
            if not all(0 <= x < self.BOARD_SIZE for x in [to_row, to_col]):
                return False

            # Check destination is empty
            if self.board[to_row][to_col]:
                return False

            # Check player has the piece in hand
            if piece_type not in self.hands[self.current_player]:
                return False

            # Check drop restrictions
            if piece_type == "p":  # Pawn (lowercase)
                # Nifu: Can't drop pawn in same file as another UNPROMOTED pawn of the same color
                for r_idx in range(self.RANKS):
                    square_content = self.board[r_idx][to_col]
                    if (
                        square_content
                        and square_content.piece_type == "p"  # lowercase 'p'
                        and not square_content.promoted  # Must be an unpromoted pawn
                        and square_content.color == self.current_player
                    ):
                        return False  # Nifu violation
                # Pawn drop rank restriction (cannot drop on last rank)
                if self.current_player == "w" and to_row == 0:
                    return False
                if self.current_player == "b" and to_row == self.RANKS - 1:
                    return False

            elif piece_type == "l":  # Lance (lowercase)
                # Lance drop rank restriction (cannot drop on last rank)
                if self.current_player == "w" and to_row == 0:
                    return False
                if self.current_player == "b" and to_row == self.RANKS - 1:
                    return False

            elif piece_type == "n":  # Knight (lowercase)
                # Knight drop rank restriction (cannot drop on last two ranks)
                if self.current_player == "w" and to_row <= 1:
                    return False
                if self.current_player == "b" and to_row >= self.RANKS - 2:
                    return False
        
            # Cannot drop a King (already covered by PIECE_TYPES in hand, but good to be explicit if it were possible)
            # For Shogi, kings are never in hand, so this check is more for logical completeness if rules changed.
            # The primary check is that 'k' is not a droppable piece type from hand.
            # However, if 'k' somehow appeared as a piece_type in move_data for a drop, this would catch it.
            elif piece_type == "k": # King (lowercase)
                 return False # Explicitly disallow king drop if it were attempted

            return True

        except KeyError:
            return False

    def _validate_piece_move(
        self,
        piece_type: str,
        promoted: bool,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        piece_color: str,
        board_context: Optional[List[List[Optional[ShogiPiece]]]] = None
    ) -> bool:
        """Validate move based on piece type"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # Centralized path check for sliding pieces (Bishop, Rook)
        # Lance path check is specific due to its forward-only movement and is handled below.
        if piece_type in ["r", "b"]:
            if not self._check_path_clear(from_pos, to_pos, board_context):
                return False

        direction = -1 if piece_color == "w" else 1

        if piece_type == "p":  # Pawn
            if promoted:
                return self._validate_promoted_pawn_move(from_pos, to_pos, piece_color)
            return to_row == from_row + direction and from_col == to_col

        elif piece_type == "l":  # Lance
            if promoted:
                return self._validate_promoted_lance_move(from_pos, to_pos, piece_color)
            if from_col != to_col: return False  # Must be in the same column
            if direction == -1 and to_row >= from_row: return False
            if direction == 1 and to_row <= from_row: return False
            return self._check_path_clear(from_pos, to_pos, board_context)

        elif piece_type == "n":  # Knight
            if promoted:
                return self._validate_promoted_knight_move(from_pos, to_pos, piece_color)
            return to_row == from_row + (2 * direction) and abs(to_col - from_col) == 1

        elif piece_type == "s":  # Silver
            if promoted:
                return self._validate_promoted_silver_move(from_pos, to_pos, piece_color)
            s_dr = to_row - from_row; s_dc = to_col - from_col
            if s_dr == direction and s_dc == 0: return True
            if s_dr == direction and abs(s_dc) == 1: return True
            if s_dr == -direction and abs(s_dc) == 1: return True
            return False

        elif piece_type == "g":  # Gold
            dr = to_row - from_row; dc = to_col - from_col
            return (abs(dr) <= 1 and abs(dc) <= 1) and not (dr == -direction and abs(dc) == 1)

        elif piece_type == "k":  # King
            return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

        elif piece_type == "b":  # Bishop
            if promoted:
                return self._validate_promoted_bishop_move(from_pos, to_pos, piece_color)
            return abs(to_row - from_row) == abs(to_col - from_col) and self._check_path_clear(from_pos, to_pos, board_context)

        elif piece_type == "r":  # Rook
            if promoted:
                return self._validate_promoted_rook_move(from_pos, to_pos, piece_color)
            return (from_row == to_row or from_col == to_col) and self._check_path_clear(from_pos, to_pos, board_context)
        
        return False

    def _validate_promoted_pawn_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece_color: str) -> bool:
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        direction = -1 if piece_color == "w" else 1
        dr = to_row - from_row
        dc = to_col - from_col
        # Promoted Pawn moves like a Gold General
        return (abs(dr) <= 1 and abs(dc) <= 1) and not (dr == -direction and abs(dc) == 1)

    def _validate_promoted_knight_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece_color: str) -> bool:
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        direction = -1 if piece_color == "w" else 1
        dr = to_row - from_row
        dc = to_col - from_col
        # Promoted Knight moves like a Gold General
        return (abs(dr) <= 1 and abs(dc) <= 1) and not (dr == -direction and abs(dc) == 1)

    def _validate_promoted_silver_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece_color: str) -> bool:
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        direction = -1 if piece_color == "w" else 1
        dr = to_row - from_row
        dc = to_col - from_col
        # Promoted Silver moves like a Gold General
        return (abs(dr) <= 1 and abs(dc) <= 1) and not (dr == -direction and abs(dc) == 1)

    def _validate_promoted_lance_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece_color: str) -> bool:
        """Validate promoted lance move (moves like Gold General)"""
        from_row, from_col = from_pos; to_row, to_col = to_pos
        direction = -1 if piece_color == "w" else 1 # Corrected to use piece_color
        dr = to_row - from_row; dc = to_col - from_col
        return (abs(dr) <= 1 and abs(dc) <= 1) and not (dr == -direction and abs(dc) == 1)

    def _validate_promoted_bishop_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece_color: str) -> bool:
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        dr = to_row - from_row
        dc = to_col - from_col
        # Bishop-like move (path check is done in _validate_piece_move)
        is_bishop_move = abs(dr) == abs(dc)
        # King-like move
        is_king_move = abs(dr) <= 1 and abs(dc) <= 1
        return is_bishop_move or is_king_move

    def _validate_promoted_rook_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece_color: str) -> bool:
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        dr = to_row - from_row
        dc = to_col - from_col
        # Rook-like move (path check is done in _validate_piece_move)
        is_rook_move = dr == 0 or dc == 0
        # King-like move
        is_king_move = abs(dr) <= 1 and abs(dc) <= 1
        return is_rook_move or is_king_move

    def _check_path_clear(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], board_to_check: Optional[List[List[Optional[ShogiPiece]]]] = None) -> bool:
        """Check if path is clear for sliding pieces (Rook, Bishop, Lance)."""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        board = board_to_check if board_to_check is not None else self.board
        if from_row == to_row:  # Horizontal
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if board[from_row][col]:
                    return False
        elif from_col == to_col:  # Vertical
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if board[row][from_col]:
                    return False
        else:  # Diagonal
            row_dir = 1 if to_row > from_row else -1
            col_dir = 1 if to_col > from_col else -1

            row = from_row + row_dir
            col = from_col + col_dir

            while row != to_row and col != to_col:
                if board[row][col]:
                    return False
                row += row_dir
                col += col_dir

        return True

    def _is_in_check(self, player_color: str, board_to_check: List[List[Optional[ShogiPiece]]]) -> bool:
        """Check if the specified player is in check on a given board state."""
        king_pos = None
        for r_idx, row in enumerate(board_to_check):
            for c_idx, piece_on_board in enumerate(row):
                if piece_on_board and piece_on_board.piece_type == "k" and piece_on_board.color == player_color:
                    king_pos = (r_idx, c_idx)
                    break
            if king_pos:
                break
        if not king_pos:
            # This can happen during intermediate checks or if king is captured (which shouldn't be allowed by rules)
            return True # Consider it a check if king is not found (implies king capture)

        opponent_color = "b" if player_color == "w" else "w"
        for r_idx, row in enumerate(board_to_check):
            for c_idx, attacking_piece in enumerate(row):
                if attacking_piece and attacking_piece.color == opponent_color:
                    # Validate if the opponent's piece can attack the king_pos on the board_to_check
                    if self._validate_piece_move(
                        attacking_piece.piece_type,
                        attacking_piece.promoted,
                        (r_idx, c_idx), # from_pos is opponent piece's current position
                        king_pos,       # to_pos is the king's position
                        attacking_piece.color, # piece_color is the opponent's color
                        board_to_check  # board_context is the board state being checked
                    ):
                        return True
        return False

    def _find_king(self, color: str) -> Optional[Tuple[int, int]]:
        """Find the king's position for the specified color"""
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.piece_type == "k" and piece.color == color:
                    return (row, col)
        return None

    def _can_attack(
        self, piece: ShogiPiece, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Check if a piece can attack a position"""
        temp_piece = self.board[to_pos[0]][to_pos[1]]
        self.board[to_pos[0]][to_pos[1]] = None

        can_attack = self._validate_piece_move(
            piece.piece_type, piece.promoted, from_pos, to_pos, piece.color, self.board
        )

        self.board[to_pos[0]][to_pos[1]] = temp_piece
        return can_attack

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a move and update game state"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        # Handle piece drop
        if move_data.get("is_drop"):
            return self._handle_drop(move_data)

        from_row, from_col = move_data["from_row"], move_data["from_col"]
        to_row, to_col = move_data["to_row"], move_data["to_col"]

        # Get the piece being moved
        piece = self.board[from_row][from_col]
        piece.promoted = move_data.get("promoted", piece.promoted)

        # Handle promotion
        if piece.piece_type in ["p", "l", "n", "s"] and (
            piece.color == "w" and to_row <= 2 or piece.color == "b" and to_row >= 6
        ):
            piece.promoted = True
            piece.promotion_rank = to_row

        # Handle piece capture
        captured_piece = self.board[to_row][to_col]
        if captured_piece:
            self._capture_piece(captured_piece)

        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # Add move to history
        move = GameMove(
            player=self.current_player,
            move_data={
                "from_row": from_row,
                "from_col": from_col,
                "to_row": to_row,
                "to_col": to_col,
                "piece_type": piece.piece_type,
                "color": piece.color,
                "promoted": piece.promoted,
                "promotion_rank": piece.promotion_rank,
                "is_drop": False,
            },
            timestamp=time.time(),
        )
        self.history.add_move(move)

        # Switch players
        self.current_player = "b" if self.current_player == "w" else "w"

        # Update position history (after player switch, representing state for new current_player)
        self._add_current_position_to_history()

        return self.get_game_state()

    def _handle_drop(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle piece drop move"""
        to_row, to_col = move_data["to_row"], move_data["to_col"]
        piece_type = move_data["piece_type"]

        # Create new piece
        piece = ShogiPiece(piece_type, self.current_player)

        # Remove piece from hand
        try:
            self.hands[self.current_player].remove(piece_type)
        except ValueError:
            # This should not happen if drop validation is correct
            raise ValueError(f"Cannot drop piece {piece_type} not in hand for player {self.current_player}. Hand: {self.hands[self.current_player]}")

        # Place piece on board
        self.board[to_row][to_col] = piece

        # Add move to history
        move = GameMove(
            player=self.current_player,
            move_data={
                "to_row": to_row,
                "to_col": to_col,
                "piece_type": piece_type,
                "color": self.current_player,
                "promoted": False,
                "is_drop": True,
            },
            timestamp=time.time(),
        )
        self.history.add_move(move)

        # Switch players
        self.current_player = "b" if self.current_player == "w" else "w"

        # Update position history (after player switch, representing state for new current_player)
        self._add_current_position_to_history()

        return self.get_game_state()

    def _capture_piece(self, captured_piece: ShogiPiece) -> None:
        """Handle piece capture. Adds the captured piece to the current player's hand."""
        # Captured pieces revert to their base type (unpromoted).
        # piece_type is already stored as lowercase base type in ShogiPiece.
        piece_type_to_add = captured_piece.piece_type 
        self.hands[self.current_player].append(piece_type_to_add)

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "board": [
                [piece.to_dict() if piece else None for piece in row]
                for row in self.board
            ],
            "current_player": self.current_player,
            "hands": self.hands,
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
            "in_check": self._is_in_check(self.current_player, self.board),
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.get_winner() is not None

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        # Check if either king is missing
        white_king = False
        black_king = False
        for row in self.board:
            for piece in row:
                if piece:
                    if piece.piece_type == "k" and piece.color == "w":
                        white_king = True
                    elif piece.piece_type == "k" and piece.color == "b":
                        black_king = True

        if not white_king:
            return "b"
        if not black_king:
            return "w"

        # Check for Sennichite (repetition of the same position)
        # This should be checked after the move is made and history is updated.
        # The game ends immediately in a draw if a position is repeated 4 times.
        if self._is_sennichite():
            return "draw"

        # Check for checkmate
        if self._is_in_check(self.current_player, self.board) and self._is_stalemate():
            return "b" if self.current_player == "w" else "w"

        return None

    def _board_to_tuple(self, board: List[List[Optional[ShogiPiece]]]) -> Tuple[Tuple[Optional[str], ...], ...]:
        """Converts the board to a hashable tuple representation for history tracking."""
        return tuple(
            tuple(str(piece) if piece else None for piece in row) for row in board
        )

    def _hands_to_tuple(self, hands: Dict[str, List[str]]) -> Tuple[Tuple[str, Tuple[str, ...]], ...]:
        """Converts hands to a sorted, hashable tuple representation."""
        # Sort pieces within each player's hand, then sort by player to ensure consistent order
        return tuple(sorted(
            (player, tuple(sorted(hand_pieces)))
            for player, hand_pieces in hands.items()
        ))

    def _add_current_position_to_history(self) -> None:
        """Adds the current board state, hands, and player to move to the position history."""
        board_tuple = self._board_to_tuple(self.board)
        hands_tuple = self._hands_to_tuple(deepcopy(self.hands)) # Use deepcopy to avoid modifying original hands by sorting
        self.position_history.append((board_tuple, hands_tuple, self.current_player))

    def _is_sennichite(self) -> bool:
        """Check for Sennichite (fourfold repetition of the same game state)."""
        if not self.position_history: # Should not happen if initialized correctly
            return False
        
        # The current state (board, hands, player to move) is the last one added to position_history
        # if _add_current_position_to_history was called after the move and player switch.
        # Or, we can construct it from the current self.board, self.hands, self.current_player.
        # Let's use the latter for clarity, as it represents the state the current player is facing.
        
        current_board_tuple = self._board_to_tuple(self.board)
        # Ensure deepcopy of hands before creating tuple to avoid sorting original hands list if _hands_to_tuple modifies input
        current_hands_tuple = self._hands_to_tuple(deepcopy(self.hands)) 
        current_player_to_move = self.current_player
        
        current_position_key = (current_board_tuple, current_hands_tuple, current_player_to_move)
        
        count = self.position_history.count(current_position_key)
        return count >= 4

    def _is_stalemate(self) -> bool:
        """Check if the current player has any legal moves."""
        # Check if current player has any legal moves
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.color == self.current_player:
                    for to_row in range(self.BOARD_SIZE):
                        for to_col in range(self.BOARD_SIZE):
                            if self.validate_move(
                                {
                                    "from_row": row,
                                    "from_col": col,
                                    "to_row": to_row,
                                    "to_col": to_col,
                                    "player": self.current_player,
                                }
                            ):
                                return False

        # Check piece drops
        for piece_type in self.hands[self.current_player]:
            if self.hands[self.current_player][piece_type] > 0:
                for row in range(self.BOARD_SIZE):
                    for col in range(self.BOARD_SIZE):
                        if self.validate_move(
                            {
                                "to_row": row,
                                "to_col": col,
                                "piece_type": piece_type,
                                "player": self.current_player,
                                "is_drop": True,
                            }
                        ):
                            return False
        return True
