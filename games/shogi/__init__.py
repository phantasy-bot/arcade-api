from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, Tuple, List
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
        # Initialization of board, current_player, hands, and _init_board()
        # is now handled by _restore_game_state (for defaults on new game)
        # and initialize_game (for full setup on new game, called externally by tests/game runner).

    def _init_board(self):
        """Initialize the shogi board with pieces"""
        # Place pieces in their starting positions
        # First rank (top)
        self.board[0] = [
            ShogiPiece("L", "b"),
            ShogiPiece("N", "b"),
            ShogiPiece("S", "b"),
            ShogiPiece("G", "b"),
            ShogiPiece("K", "b"),
            ShogiPiece("G", "b"),
            ShogiPiece("S", "b"),
            ShogiPiece("N", "b"),
            ShogiPiece("L", "b"),
        ]
        # Second rank
        self.board[1] = [
            None,
            None,
            None,
            ShogiPiece("B", "b"),
            None,
            ShogiPiece("R", "b"),
            None,
            None,
            None,
        ]
        # Third rank
        self.board[2] = [ShogiPiece("P", "b") for _ in range(self.FILES)]

        # Seventh rank
        self.board[6] = [ShogiPiece("P", "w") for _ in range(self.FILES)]
        # Eighth rank
        self.board[7] = [
            None,
            None,
            None,
            ShogiPiece("B", "w"),
            None,
            ShogiPiece("R", "w"),
            None,
            None,
            None,
        ]
        # Ninth rank (bottom)
        self.board[8] = [
            ShogiPiece("L", "w"),
            ShogiPiece("N", "w"),
            ShogiPiece("S", "w"),
            ShogiPiece("G", "w"),
            ShogiPiece("K", "w"),
            ShogiPiece("G", "w"),
            ShogiPiece("S", "w"),
            ShogiPiece("N", "w"),
            ShogiPiece("L", "w"),
        ]

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

    def initialize_game(self) -> Dict[str, Any]:
        """Initialize a new game instance, set up board, players, etc., and return initial state."""
        # Set up the initial state (board, player, hands)
        self._init_board()  # Populate the board with pieces

        # Update and persist history
        self.history.current_state = self.get_game_state()
        if self.game_id: # Only persist if game_id is available
            self.history._persist_to_disk() # Ensure initial state is saved if it's a new game

        return self.history.current_state

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
            target_piece = self.board[to_row][to_col]
            if target_piece and target_piece.color == self.current_player:
                return False

            # Check if move would put king in check
            temp_piece = self.board[to_row][to_col]
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None

            if self._is_in_check(self.current_player):
                self.board[from_row][from_col] = piece
                self.board[to_row][to_col] = temp_piece
                return False

            self.board[from_row][from_col] = piece
            self.board[to_row][to_col] = temp_piece

            # Validate move based on piece type
            return self._validate_piece_move(
                piece.piece_type, piece.promoted, (from_row, from_col), (to_row, to_col)
            )

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
            if (
                piece_type not in self.hands[self.current_player]
                or self.hands[self.current_player][piece_type] <= 0
            ):
                return False

            # Check drop restrictions
            if piece_type == "P":  # Pawn
                # Can't drop pawn in same file as another pawn
                for row in range(self.BOARD_SIZE):
                    if (
                        self.board[row][to_col]
                        and self.board[row][to_col].piece_type == "P"
                        and self.board[row][to_col].color == self.current_player
                    ):
                        return False
            elif piece_type == "K":  # King
                return False  # Can't drop king

            return True

        except KeyError:
            return False

    def _validate_piece_move(
        self,
        piece_type: str,
        promoted: bool,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
    ) -> bool:
        """Validate move based on piece type"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # Check for piece in the way for sliding pieces
        if piece_type in ["R", "B"]:
            if not self._check_path_clear(from_pos, to_pos):
                return False

        direction = 1 if self.current_player == "w" else -1

        if piece_type == "P":  # Pawn
            if promoted:
                return self._validate_promoted_pawn_move(from_pos, to_pos)
            return to_row == from_row + direction and from_col == to_col

        elif piece_type == "L":  # Lance
            if promoted:
                return self._validate_promoted_lance_move(from_pos, to_pos)
            return to_row > from_row and from_col == to_col

        elif piece_type == "N":  # Knight
            if promoted:
                return self._validate_promoted_knight_move(from_pos, to_pos)
            return to_row == from_row + (2 * direction) and abs(to_col - from_col) == 1

        elif piece_type == "S":  # Silver
            if promoted:
                return self._validate_promoted_silver_move(from_pos, to_pos)
            return (abs(to_row - from_row) == 1 and abs(to_col - from_col) <= 1) or (
                to_row == from_row + direction and abs(to_col - from_col) == 1
            )

        elif piece_type == "G":  # Gold
            return (abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1) or (
                to_row == from_row + direction and abs(to_col - from_col) <= 1
            )

        elif piece_type == "K":  # King
            return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

        elif piece_type == "B":  # Bishop
            if promoted:
                return self._validate_promoted_bishop_move(from_pos, to_pos)
            return abs(to_row - from_row) == abs(to_col - from_col)

        elif piece_type == "R":  # Rook
            if promoted:
                return self._validate_promoted_rook_move(from_pos, to_pos)
            return from_row == to_row or from_col == to_col

        return False

    def _validate_promoted_pawn_move(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Validate promoted pawn move"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

    def _validate_promoted_lance_move(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Validate promoted lance move"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        return (abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1) or (
            to_row == from_row + 1 and from_col == to_col
        )

    def _validate_promoted_knight_move(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Validate promoted knight move"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

    def _validate_promoted_silver_move(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Validate promoted silver move"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

    def _validate_promoted_bishop_move(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Validate promoted bishop move"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        return (abs(to_row - from_row) == abs(to_col - from_col)) or (
            abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
        )

    def _validate_promoted_rook_move(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Validate promoted rook move"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        return (from_row == to_row or from_col == to_col) or (
            abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
        )

    def _check_path_clear(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Check if path between positions is clear"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        if from_row == to_row:  # Horizontal
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if self.board[from_row][col]:
                    return False
        elif from_col == to_col:  # Vertical
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if self.board[row][from_col]:
                    return False
        else:  # Diagonal
            row_dir = 1 if to_row > from_row else -1
            col_dir = 1 if to_col > from_col else -1

            row = from_row + row_dir
            col = from_col + col_dir

            while row != to_row and col != to_col:
                if self.board[row][col]:
                    return False
                row += row_dir
                col += col_dir

        return True

    def _is_in_check(self, color: str) -> bool:
        """Check if the specified color is in check"""
        king_pos = self._find_king(color)
        if not king_pos:
            return False

        opponent_color = "w" if color == "b" else "b"
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    if self._can_attack(piece, (row, col), king_pos):
                        return True
        return False

    def _find_king(self, color: str) -> Optional[Tuple[int, int]]:
        """Find the king's position for the specified color"""
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.piece_type == "K" and piece.color == color:
                    return (row, col)
        return None

    def _can_attack(
        self, piece: ShogiPiece, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Check if a piece can attack a position"""
        temp_piece = self.board[to_pos[0]][to_pos[1]]
        self.board[to_pos[0]][to_pos[1]] = None

        can_attack = self._validate_piece_move(
            piece.piece_type, piece.promoted, from_pos, to_pos
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
        if piece.piece_type in ["P", "L", "N", "S"] and (
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

        return self.get_game_state()

    def _handle_drop(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle piece drop move"""
        to_row, to_col = move_data["to_row"], move_data["to_col"]
        piece_type = move_data["piece_type"]

        # Create new piece
        piece = ShogiPiece(piece_type, self.current_player)

        # Remove piece from hand
        self.hands[self.current_player][piece_type] -= 1

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

        return self.get_game_state()

    def _capture_piece(self, piece: ShogiPiece) -> None:
        """Handle piece capture"""
        # Add captured piece to opponent's hand
        self.hands[piece.color][piece.piece_type] = (
            self.hands[piece.color].get(piece.piece_type, 0) + 1
        )

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
            "in_check": self._is_in_check(self.current_player),
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
                    if piece.piece_type == "K" and piece.color == "w":
                        white_king = True
                    elif piece.piece_type == "K" and piece.color == "b":
                        black_king = True

        if not white_king:
            return "b"
        if not black_king:
            return "w"

        # Check for checkmate
        if self._is_in_check(self.current_player) and self._is_stalemate():
            return "b" if self.current_player == "w" else "w"

        return None

    def _is_stalemate(self) -> bool:
        """Check for stalemate"""
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
