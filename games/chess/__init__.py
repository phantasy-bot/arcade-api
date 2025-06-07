from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, Tuple, List
import time


class ChessPiece:
    """Represents a chess piece"""

    def __init__(self, piece_type: str, color: str):
        self.piece_type = piece_type.lower()
        self.color = color.lower()
        self.has_moved = False

    def __str__(self):
        return f"{self.color}{self.piece_type}"

    def __repr__(self):
        return str(self)

    def to_dict(self) -> Dict[str, str]:
        return {
            "type": self.piece_type,
            "color": self.color,
            "has_moved": self.has_moved,
        }


class ChessGame(AbstractGame):
    BOARD_SIZE = 8
    PIECE_TYPES = [
        "p",
        "r",
        "n",
        "b",
        "q",
        "k",
    ]  # pawn, rook, knight, bishop, queen, king

    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player = "w"
        self._init_board()
        self.en_passant_target = None  # For en passant
        self.halfmove_clock = 0  # For fifty-move rule
        self.fullmove_number = 1  # For move counting
        self._init_game_state()

    def initialize_game(self) -> Dict[str, Any]:
        """Initialize a new game instance"""
        self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player = "w"
        self._init_board()
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        return self.get_game_state()
        
    def _init_board(self):
        """Initialize the chess board with pieces"""
        # Place pawns
        for i in range(self.BOARD_SIZE):
            self.board[1][i] = ChessPiece("p", "w")  # White pawns
            self.board[6][i] = ChessPiece("p", "b")  # Black pawns

        # Place other pieces
        for i, piece_type in enumerate(["r", "n", "b", "q", "k", "b", "n", "r"]):
            self.board[0][i] = ChessPiece(piece_type, "w")  # White back row
            self.board[7][i] = ChessPiece(piece_type, "b")  # Black back row

    def _init_game_state(self):
        """Initialize game state"""
        self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player = "w"
        self._init_board()
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

    def _restore_game_state(self):
        """Restore game state from history"""
        # Get the latest state from history
        if self.history_state:
            latest_move = self.history_state[-1]
            self.current_player = "b" if latest_move["player"] == "w" else "w"

            # Reconstruct board from moves
            self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
            self.en_passant_target = None
            self.halfmove_clock = 0
            self.fullmove_number = 1

            for move in self.history_state:
                move_data = move["move_data"]
                piece = ChessPiece(move_data["piece_type"], move_data["color"])
                piece.has_moved = True
                self.board[move_data["to_row"]][move_data["to_col"]] = piece

    def _would_put_king_in_check(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a move would put the current player's king in check"""
        # Save the current state
        piece = self.board[from_row][from_col]
        target_piece = self.board[to_row][to_col]
        
        # Make the move temporarily
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Check if the current player's king is in check
        in_check = self._is_in_check(piece.color)
        
        # Undo the move
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = target_piece
        
        return in_check
        
    def _is_in_check(self, color: str) -> bool:
        """Check if the specified color is in check"""
        king_pos = self._find_king(color)
        if not king_pos:
            return False # Should not happen in a valid game

        opponent_color = "w" if color == "b" else "b"
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    if self._can_attack(piece, (row, col), king_pos):
                        return True
        return False

    def _is_insufficient_material(self) -> bool:
        """Check if there is insufficient material to checkmate"""
        pieces = []
        for row in self.board:
            for piece in row:
                if piece and piece.piece_type != 'k':  # Count all pieces except kings
                    pieces.append(piece)
        
        # If there are no pieces except kings, it's a draw
        if not pieces:
            return True
            
        # If there's only one minor piece, it's a draw
        if len(pieces) == 1 and pieces[0].piece_type in ['b', 'n']:
            return True
            
        # If there are only two bishops on the same color, it's a draw
        if len(pieces) == 2 and all(p.piece_type == 'b' for p in pieces):
            # Check if bishops are on the same color
            bishop1_pos = None
            bishop2_pos = None
            for row in range(self.BOARD_SIZE):
                for col in range(self.BOARD_SIZE):
                    piece = self.board[row][col]
                    if piece and piece.piece_type == 'b':
                        if bishop1_pos is None:
                            bishop1_pos = (row, col)
                        else:
                            bishop2_pos = (row, col)
            
            if bishop1_pos and bishop2_pos:
                # Bishops are on the same color if (row + col) % 2 is the same for both
                if (bishop1_pos[0] + bishop1_pos[1]) % 2 == (bishop2_pos[0] + bishop2_pos[1]) % 2:
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
        self, piece: ChessPiece, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Check if a piece can attack a position"""
        # Check if the target position has a piece of the same color
        target_piece = self.board[to_pos[0]][to_pos[1]]
        if target_piece and target_piece.color == piece.color:
            return False
            
        # Temporarily remove the target piece to validate the move
        self.board[to_pos[0]][to_pos[1]] = None

        can_attack = self._validate_piece_move(piece.piece_type, from_pos, to_pos)

        # Restore the target piece
        self.board[to_pos[0]][to_pos[1]] = target_piece
        return can_attack

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        try:
            from_row, from_col = move_data['from_row'], move_data['from_col']
            to_row, to_col = move_data['to_row'], move_data['to_col']
            player = move_data['player']
            
            # Check if the move is within the board bounds
            if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
                return False

            # Check if there's a piece at the source
            piece = self.board[from_row][from_col]
            if not piece:
                return False

            # Check if it's the player's turn
            if piece.color != player:
                return False

            # Special case: Castling
            if move_data.get('castling', False):
                if not (piece.piece_type == 'k' and abs(from_col - to_col) == 2):
                    return False
                if not self._validate_castling(from_row, from_col, to_row, to_col):
                    return False
                return True
            
            # Check if the move is valid for the piece type
            if not self._validate_piece_move(piece.piece_type, (from_row, from_col), (to_row, to_col)):
                return False
            
            # Check if the move would put the king in check
            would_check = self._would_put_king_in_check(from_row, from_col, to_row, to_col)
            if would_check:
                return False

            return True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False

    def _validate_castling(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """Validate castling move"""
        if from_row != to_row or abs(to_col - from_col) != 2:
            return False

        # Check if king has moved
        if self.board[from_row][from_col].has_moved:
            return False

        # Check if rook has moved
        rook_col = 0 if to_col < from_col else 7  # Left or right rook
        rook = self.board[from_row][rook_col]
        if not rook or rook.piece_type != "r" or rook.has_moved:
            return False

        # Check if path is clear
        start_col = min(from_col, to_col) + 1
        end_col = max(from_col, to_col)
        for col in range(start_col, end_col):
            if self.board[from_row][col]:
                return False

        # Check if king would be in check at any point during castling
        king = self.board[from_row][from_col]
        direction = 1 if to_col > from_col else -1
        
        # Check the king's current position and the two squares it will pass through
        for offset in [0, 1, 2]:
            test_col = from_col + (direction * offset)
            # Temporarily move the king to the test position
            self.board[from_row][from_col] = None
            original_piece = self.board[from_row][test_col]
            self.board[from_row][test_col] = king
            
            # Check if the king would be in check at this position
            in_check = self._is_in_check(self.current_player)
            
            # Move the king back
            self.board[from_row][from_col] = king
            self.board[from_row][test_col] = original_piece
            
            if in_check:
                return False

        return True

    def _validate_piece_move(
        self, piece_type: str, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Validate move based on piece type"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Get the piece being moved
        piece = self.board[from_row][from_col]
        if not piece:
            return False
        
        piece_color = piece.color

        # Check if the destination square is occupied by a friendly piece
        target_piece = self.board[to_row][to_col]
        if target_piece and target_piece.color == piece_color:
            return False

        # Check for piece in the way
        if piece_type in ["r", "b", "q"]:
            if not self._check_path_clear(from_pos, to_pos):
                return False

        if piece_type == "p":  # Pawn
            direction = 1 if piece_color == "w" else -1
            start_row = 1 if piece_color == "w" else 6

            # Check for en passant capture first
            if self.en_passant_target and (to_row, to_col) == self.en_passant_target:
                # For en passant, the target square is empty, but the captured pawn is on an adjacent file
                # Check if moving diagonally one square in the correct direction
                col_diff = abs(from_col - to_col)
                row_diff = to_row - from_row
                
                # For en passant, the row difference should be -1 for white (moving up) and 1 for black (moving down)
                # because rows increase as we go down the board (0 is the top row, 7 is the bottom row)
                expected_row_diff = -1 if piece_color == 'w' else 1
                
                if col_diff == 1 and row_diff == expected_row_diff:
                    # The actual captured pawn is on the same rank as the moving pawn, same file as the target
                    captured_pawn_row = from_row
                    captured_pawn_col = to_col
                    
                    # Check if there's an opponent's pawn that can be captured en passant
                    if (0 <= captured_pawn_row < 8 and 0 <= captured_pawn_col < 8 and
                        self.board[captured_pawn_row][captured_pawn_col] and
                        self.board[captured_pawn_row][captured_pawn_col].piece_type == 'p' and
                        self.board[captured_pawn_row][captured_pawn_col].color != piece_color):
                        return True
        
            if from_col == to_col:  # Moving forward
                # Check if destination is occupied
                if self.board[to_row][to_col] is not None:
                    return False
                
                # Check for valid move distance
                if abs(to_row - from_row) > 2:
                    return False
                if abs(to_row - from_row) == 0:  # Not moving
                    return False
                
                # Check for one square move
                if (piece_color == "w" and to_row - from_row == 1) or \
                   (piece_color == "b" and from_row - to_row == 1):
                    return True
                
                # Check for two-square move (only from starting position)
                if from_row != start_row:
                    return False
                
                # Check if the path is clear (only need to check the square in between)
                if piece_color == "w" and self.board[from_row + 1][from_col] is not None:
                    return False
                if piece_color == "b" and self.board[from_row - 1][from_col] is not None:
                    return False
                
                return True
                    
            else:  # Standard capture (not en passant)
                # Must move diagonally one square
                if abs(to_col - from_col) != 1 or abs(to_row - from_row) != 1:
                    return False
                    
                # Must capture opponent's piece
                target = self.board[to_row][to_col]
                if target is None or target.color == piece_color:
                    return False
                    
                return True

        elif piece_type == "r":  # Rook
            return from_row == to_row or from_col == to_col

        elif piece_type == "n":  # Knight
            # Knight moves in an L-shape: 2 squares in one direction and 1 square perpendicular
            row_diff = abs(to_row - from_row)
            col_diff = abs(to_col - from_col)
            return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

        elif piece_type == "b":  # Bishop
            return abs(to_row - from_row) == abs(to_col - from_col)

        elif piece_type == "q":  # Queen
            return (
                abs(to_row - from_row) == abs(to_col - from_col)
                or from_row == to_row
                or from_col == to_col
            )

        elif piece_type == "k":  # King
            return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

        return False

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

    def make_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a move and update game state"""
        if not self.validate_move(move_data):
            raise ValueError("Invalid move")

        from_row, from_col = move_data["from_row"], move_data["from_col"]
        to_row, to_col = move_data["to_row"], move_data["to_col"]

        # Get the piece being moved
        piece = self.board[from_row][from_col]
        piece.has_moved = True

        # Handle castling
        if piece.piece_type == "k" and abs(to_col - from_col) == 2:
            self._handle_castling(from_row, from_col, to_row, to_col)

        # Handle en passant
        elif (
            piece.piece_type == "p"
            and self.en_passant_target
            and (to_row, to_col) == self.en_passant_target
        ):
            self._handle_en_passant(from_row, from_col, to_row, to_col)

        # Handle pawn promotion
        elif piece.piece_type == "p" and to_row in [0, 7]:
            self._handle_pawn_promotion(from_row, from_col, to_row, to_col)

        # Check for en passant opportunity (pawn moving two squares)
        if piece.piece_type == 'p' and abs(to_row - from_row) == 2:
            direction = 1 if piece.color == 'w' else -1
            self.en_passant_target = (from_row + direction, from_col)
        else:
            self.en_passant_target = None
            
        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # Check for 50-move rule before updating counters
        if self.halfmove_clock >= 50:
            return self.get_game_state()
            
        # Update halfmove clock
        if piece.piece_type == "p" or self.board[to_row][to_col]:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if self.current_player == "b":
            self.fullmove_number += 1

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
                "en_passant": self.en_passant_target,
                "halfmove_clock": self.halfmove_clock,
                "fullmove_number": self.fullmove_number,
            },
            timestamp=time.time(),
        )
        self.history.add_move(move)

        # Reset en passant target after the move is complete.
        # This logic is based on the piece that just moved (referenced by 'piece', 'to_row', 'from_row').
        if not (piece.piece_type == 'p' and abs(to_row - from_row) == 2):
            self.en_passant_target = None

        moving_player = self.current_player
        # Switch self.current_player to the player whose turn it would be next.
        self.current_player = "b" if moving_player == "w" else "w"
        player_who_would_move_next = self.current_player

        game_over = self.is_game_over() # Evaluates based on player_who_would_move_next
        winner = self.get_winner() if game_over else None # Evaluates based on player_who_would_move_next
        
        # Determine 'in_check' status for the player whose turn it would be.
        # If white is checkmated by black, player_who_would_move_next is 'w', and _is_in_check('w') is True.
        in_check_status = self._is_in_check(player_who_would_move_next)

        # Determine current_player for the returned game_state
        # If game is over, current_player in state is the one who made the final move.
        # Otherwise, it's the player whose turn it is next.
        current_player_for_state = moving_player if game_over else player_who_would_move_next

        game_state = {
            "board": [[p.to_dict() if p else None for p in row] for row in self.board],
            "current_player": current_player_for_state,
            "game_over": game_over,
            "winner": winner,
            "in_check": in_check_status,
            "en_passant_target": self.en_passant_target,
            "halfmove_clock": self.halfmove_clock,
            "fullmove_number": self.fullmove_number,
        }
        
        # self.current_player is already correctly set for the next turn if the game continues,
        # or reflects the player who would have moved if the game ended.
        # The previous conditional switch is no longer needed.
        
        return game_state

    def _handle_castling(self, from_row: int, from_col: int, to_row: int, to_col: int) -> None:
        """Handle castling move"""
        # Move the king
        king = self.board[from_row][from_col]
        king.has_moved = True
        self.board[to_row][to_col] = king
        self.board[from_row][from_col] = None
        
        # Determine the rook's positions
        if to_col > from_col:  # Kingside castling
            rook_from_col = 7
            rook_to_col = 5
        else:  # Queenside castling
            rook_from_col = 0
            rook_to_col = 3
            
        # Move the rook
        rook = self.board[from_row][rook_from_col]
        if rook and rook.piece_type == 'r':
            rook.has_moved = True
            self.board[from_row][rook_to_col] = rook
            self.board[from_row][rook_from_col] = None

    def _handle_en_passant(self, from_row: int, from_col: int, to_row: int, to_col: int) -> None:
        """Handle en passant capture"""
        if self.en_passant_target and (to_row, to_col) == self.en_passant_target:
            print(f"Handling en passant capture at {self.en_passant_target}")
            # The captured pawn is on the same rank as the moving pawn, same file as the target
            captured_row = from_row
            captured_col = to_col
            print(f"Removing captured pawn at ({captured_row}, {captured_col})")
            self.board[captured_row][captured_col] = None
        # Reset the en passant target after the capture
        self.en_passant_target = None

    def _handle_pawn_promotion(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ):
        """Handle pawn promotion"""
        # Replace pawn with queen (default promotion)
        piece = self.board[from_row][from_col]
        self.board[to_row][to_col] = ChessPiece("q", piece.color)

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            "board": [
                [piece.to_dict() if piece else None for piece in row]
                for row in self.board
            ],
            "current_player": self.current_player,
            "game_over": self.is_game_over(),
            "winner": self.get_winner(),
            "in_check": self._is_in_check(self.current_player),
            "en_passant_target": self.en_passant_target,
            "halfmove_clock": self.halfmove_clock,
            "fullmove_number": self.fullmove_number,
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        # Check for 50-move rule
        if self.halfmove_clock >= 50:
            return True
            
        # Check for insufficient material
        if self._is_insufficient_material():
            return True
            
        # Check if current player has any legal moves
        # First, check if the current player's king is in check
        in_check = self._is_in_check(self.current_player)
        
        # Then check for any legal moves
        for from_row in range(self.BOARD_SIZE):
            for from_col in range(self.BOARD_SIZE):
                piece = self.board[from_row][from_col]
                if piece and piece.color == self.current_player:
                    for to_row in range(self.BOARD_SIZE):
                        for to_col in range(self.BOARD_SIZE):
                            if from_row == to_row and from_col == to_col:
                                continue
                                
                            # Skip if not a valid move for this piece
                            if not self._validate_piece_move(piece.piece_type, (from_row, from_col), (to_row, to_col)):
                                continue
                            
                            # Make the move
                            original_piece_at_from = self.board[from_row][from_col]
                            original_piece_at_to = self.board[to_row][to_col]
                            
                            self.board[to_row][to_col] = original_piece_at_from
                            self.board[from_row][from_col] = None
                            
                            # Check if king is in check after the move
                            still_in_check_after_simulated_move = self._is_in_check(self.current_player)
                            
                            # Undo the move
                            self.board[from_row][from_col] = original_piece_at_from
                            self.board[to_row][to_col] = original_piece_at_to
                            
                            # If this move gets us out of check, it's a legal move
                            if not still_in_check_after_simulated_move:
                                return False  # Found a legal move
        
        # If we get here, there are no legal moves
        return True

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
        return True

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        # Check if either king is missing (e.g. captured, though this shouldn't happen before checkmate)
        white_king_present = any(piece and piece.piece_type == "k" and piece.color == "w" for r in self.board for piece in r)
        black_king_present = any(piece and piece.piece_type == "k" and piece.color == "b" for r in self.board for piece in r)

        if not white_king_present:
            return "b"
        if not black_king_present:
            return "w"
        
        # Check for game end conditions based on the current player (whose turn it would be)
        if self.is_game_over(): # This checks if self.current_player has no legal moves
            if self._is_in_check(self.current_player):
                # If current player is in check and has no legal moves, it's checkmate.
                # The *other* player wins.
                return "b" if self.current_player == "w" else "w"
            else:
                # If current player has no legal moves but is NOT in check, it's stalemate.
                return None # Draw
                
        # Check for other draw conditions that might not be caught by is_game_over (e.g. 50-move, insufficient material)
        # These are typically checked before determining if a player has legal moves.
        # However, is_game_over already checks these, so this might be redundant if is_game_over is comprehensive.
        if self.halfmove_clock >= 50:
            return None  # Draw
            
        if self._is_insufficient_material():
            return None  # Draw
            
        return None # Game is not over, or it's a draw condition not yet handled
            
    def _has_no_legal_moves(self) -> bool:
        """Check if the current player has any legal moves"""
        for from_row in range(self.BOARD_SIZE):
            for from_col in range(self.BOARD_SIZE):
                piece = self.board[from_row][from_col]
                if piece and piece.color == self.current_player:
                    # For each piece, check all possible moves
                    for to_row in range(self.BOARD_SIZE):
                        for to_col in range(self.BOARD_SIZE):
                            # Skip if it's the same position
                            if from_row == to_row and from_col == to_col:
                                continue
                            
                            # Skip if the destination has a piece of the same color
                            dest_piece = self.board[to_row][to_col]
                            if dest_piece and dest_piece.color == self.current_player:
                                continue
                            
                            # Check if the move is valid for this piece type
                            if not self._validate_piece_move(piece.piece_type, (from_row, from_col), (to_row, to_col)):
                                continue
                            
                            # Make a copy of the board to test the move
                            original_piece = self.board[to_row][to_col]
                            self.board[to_row][to_col] = piece
                            self.board[from_row][from_col] = None
                            
                            # Check if the king is in check after the move
                            king_in_check = self._is_in_check(self.current_player)
                            
                            # Restore the board
                            self.board[from_row][from_col] = piece
                            self.board[to_row][to_col] = original_piece
                            
                            # If the move doesn't leave the king in check, it's a legal move
                            if not king_in_check:
                                return False
        
        # If we get here, no legal moves were found
        return True
