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
            'type': self.piece_type,
            'color': self.color,
            'has_moved': self.has_moved
        }

class ChessGame(AbstractGame):
    BOARD_SIZE = 8
    PIECE_TYPES = ['p', 'r', 'n', 'b', 'q', 'k']  # pawn, rook, knight, bishop, queen, king
    
    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player = 'w'
        self._init_board()
        self.en_passant_target = None  # For en passant
        self.halfmove_clock = 0  # For fifty-move rule
        self.fullmove_number = 1  # For move counting
        self._init_game_state()

    def _init_board(self):
        """Initialize the chess board with pieces"""
        # Place pawns
        for i in range(self.BOARD_SIZE):
            self.board[1][i] = ChessPiece('p', 'w')  # White pawns
            self.board[6][i] = ChessPiece('p', 'b')  # Black pawns

        # Place other pieces
        for i, piece_type in enumerate(['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']):
            self.board[0][i] = ChessPiece(piece_type, 'w')  # White back row
            self.board[7][i] = ChessPiece(piece_type, 'b')  # Black back row

    def _init_game_state(self):
        """Initialize game state"""
        self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.current_player = 'w'
        self._init_board()
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

    def _restore_game_state(self):
        """Restore game state from history"""
        # Get the latest state from history
        if self.history_state:
            latest_move = self.history_state[-1]
            self.current_player = 'b' if latest_move['player'] == 'w' else 'w'
            
            # Reconstruct board from moves
            self.board = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
            self.en_passant_target = None
            self.halfmove_clock = 0
            self.fullmove_number = 1
            
            for move in self.history_state:
                move_data = move['move_data']
                piece = ChessPiece(move_data['piece_type'], move_data['color'])
                piece.has_moved = True
                self.board[move_data['to_row']][move_data['to_col']] = piece

    def _is_in_check(self, color: str) -> bool:
        """Check if the specified color is in check"""
        king_pos = self._find_king(color)
        if not king_pos:
            return False
            
        opponent_color = 'w' if color == 'b' else 'b'
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
                if piece and piece.piece_type == 'k' and piece.color == color:
                    return (row, col)
        return None

    def _can_attack(self, piece: ChessPiece, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Check if a piece can attack a position"""
        temp_piece = self.board[to_pos[0]][to_pos[1]]
        self.board[to_pos[0]][to_pos[1]] = None
        
        can_attack = self._validate_piece_move(piece.piece_type, from_pos, to_pos)
        
        self.board[to_pos[0]][to_pos[1]] = temp_piece
        return can_attack

    def validate_move(self, move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        try:
            from_row, from_col = move_data['from_row'], move_data['from_col']
            to_row, to_col = move_data['to_row'], move_data['to_col']
            
            # Check valid coordinates
            if not all(0 <= x < self.BOARD_SIZE for x in [from_row, from_col, to_row, to_col]):
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
            is_valid = self._validate_piece_move(piece.piece_type, (from_row, from_col), (to_row, to_col))
            
            # Check for castling
            if piece.piece_type == 'k' and not piece.has_moved:
                if abs(to_col - from_col) == 2:  # Castling attempt
                    return self._validate_castling(from_row, from_col, to_row, to_col)
            
            # Check for en passant
            if piece.piece_type == 'p' and self.en_passant_target:
                if (to_row, to_col) == self.en_passant_target:
                    return True
            
            return is_valid
            
        except KeyError:
            return False

    def _validate_castling(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Validate castling move"""
        if from_row != to_row or abs(to_col - from_col) != 2:
            return False
            
        # Check if king has moved
        if self.board[from_row][from_col].has_moved:
            return False
            
        # Check if rook has moved
        rook_col = 0 if to_col < from_col else 7  # Left or right rook
        rook = self.board[from_row][rook_col]
        if not rook or rook.piece_type != 'r' or rook.has_moved:
            return False
            
        # Check if path is clear
        start_col = min(from_col, to_col) + 1
        end_col = max(from_col, to_col)
        for col in range(start_col, end_col):
            if self.board[from_row][col]:
                return False
                
        # Check if king passes through check
        for col in range(min(from_col, to_col), max(from_col, to_col) + 1):
            if self._is_in_check(self.current_player):
                return False
                
        return True

    def _validate_piece_move(self, piece_type: str, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Validate move based on piece type"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Check for piece in the way
        if piece_type in ['r', 'b', 'q']:
            if not self._check_path_clear(from_pos, to_pos):
                return False

        if piece_type == 'p':  # Pawn
            direction = 1 if self.current_player == 'w' else -1
            
            # Check for en passant
            if self.en_passant_target and (to_row, to_col) == self.en_passant_target:
                return True
                
            if from_col == to_col:  # Move forward
                if abs(to_row - from_row) > 2:
                    return False
                if abs(to_row - from_row) == 2 and from_row != (1 if self.current_player == 'w' else 6):
                    return False
                if self.board[to_row][to_col]:
                    return False
                if abs(to_row - from_row) == 2:
                    self.en_passant_target = (to_row, to_col)
            else:  # Capture
                if abs(to_col - from_col) != 1 or abs(to_row - from_row) != 1:
                    return False
                if not self.board[to_row][to_col]:
                    return False
                if self.board[to_row][to_col].color == self.current_player:
                    return False
            return True
            
        elif piece_type == 'r':  # Rook
            return from_row == to_row or from_col == to_col
            
        elif piece_type == 'n':  # Knight
            return (abs(to_row - from_row) == 2 and abs(to_col - from_col) == 1) or \
                   (abs(to_row - from_row) == 1 and abs(to_col - from_col) == 2)
            
        elif piece_type == 'b':  # Bishop
            return abs(to_row - from_row) == abs(to_col - from_col)
            
        elif piece_type == 'q':  # Queen
            return abs(to_row - from_row) == abs(to_col - from_col) or \
                   from_row == to_row or from_col == to_col
            
        elif piece_type == 'k':  # King
            return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
            
        return False

    def _check_path_clear(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
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

        from_row, from_col = move_data['from_row'], move_data['from_col']
        to_row, to_col = move_data['to_row'], move_data['to_col']
        
        # Get the piece being moved
        piece = self.board[from_row][from_col]
        piece.has_moved = True
        
        # Handle castling
        if piece.piece_type == 'k' and abs(to_col - from_col) == 2:
            self._handle_castling(from_row, from_col, to_row, to_col)
            
        # Handle en passant
        elif piece.piece_type == 'p' and self.en_passant_target and (to_row, to_col) == self.en_passant_target:
            self._handle_en_passant(from_row, from_col, to_row, to_col)
            
        # Handle pawn promotion
        elif piece.piece_type == 'p' and to_row in [0, 7]:
            self._handle_pawn_promotion(from_row, from_col, to_row, to_col)
        
        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Update counters
        if piece.piece_type == 'p' or self.board[to_row][to_col]:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
            
        if self.current_player == 'b':
            self.fullmove_number += 1
        
        # Add move to history
        move = GameMove(
            player=self.current_player,
            move_data={
                'from_row': from_row,
                'from_col': from_col,
                'to_row': to_row,
                'to_col': to_col,
                'piece_type': piece.piece_type,
                'color': piece.color,
                'en_passant': self.en_passant_target,
                'halfmove_clock': self.halfmove_clock,
                'fullmove_number': self.fullmove_number
            },
            timestamp=time.time()
        )
        self.history.add_move(move)
        
        # Reset en passant target
        self.en_passant_target = None
        
        # Switch players
        self.current_player = 'b' if self.current_player == 'w' else 'w'
        
        return self.get_game_state()

    def _handle_castling(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """Handle castling move"""
        rook_col = 0 if to_col < from_col else 7  # Left or right rook
        rook = self.board[from_row][rook_col]
        
        # Move rook
        rook.has_moved = True
        rook_target_col = 3 if to_col < from_col else 5
        self.board[from_row][rook_target_col] = rook
        self.board[from_row][rook_col] = None

    def _handle_en_passant(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """Handle en passant capture"""
        # Remove the captured pawn
        direction = 1 if self.current_player == 'w' else -1
        captured_pawn = self.board[to_row + direction][to_col]
        self.board[to_row + direction][to_col] = None

    def _handle_pawn_promotion(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """Handle pawn promotion"""
        # Replace pawn with queen (default promotion)
        piece = self.board[from_row][from_col]
        self.board[to_row][to_col] = ChessPiece('q', piece.color)

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return {
            'board': [[piece.to_dict() if piece else None for piece in row] for row in self.board],
            'current_player': self.current_player,
            'game_over': self.is_game_over(),
            'winner': self.get_winner(),
            'in_check': self._is_in_check(self.current_player),
            'en_passant_target': self.en_passant_target,
            'halfmove_clock': self.halfmove_clock,
            'fullmove_number': self.fullmove_number
        }

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.get_winner() is not None or self._is_stalemate()

    def _is_stalemate(self) -> bool:
        """Check for stalemate"""
        # Check if current player has any legal moves
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.color == self.current_player:
                    for to_row in range(self.BOARD_SIZE):
                        for to_col in range(self.BOARD_SIZE):
                            if self.validate_move({
                                'from_row': row,
                                'from_col': col,
                                'to_row': to_row,
                                'to_col': to_col,
                                'player': self.current_player
                            }):
                                return False
        return True

    def get_winner(self) -> Optional[str]:
        """Get the winner if game is over"""
        # Check if either king is missing
        white_king = False
        black_king = False
        for row in self.board:
            for piece in row:
                if piece:
                    if piece.piece_type == 'k' and piece.color == 'w':
                        white_king = True
                    elif piece.piece_type == 'k' and piece.color == 'b':
                        black_king = True
        
        if not white_king:
            return 'b'
        if not black_king:
            return 'w'
            
        # Check for checkmate
        if self._is_in_check(self.current_player) and self._is_stalemate():
            return 'b' if self.current_player == 'w' else 'w'
            
        return None
