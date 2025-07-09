import copy
from typing import List, Tuple, Optional, Dict, Set
from enum import Enum

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class PieceType(Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"

class Piece:
    def __init__(self, color: Color, piece_type: PieceType):
        self.color = color
        self.piece_type = piece_type
        self.has_moved = False
    
    def __str__(self):
        symbols = {
            PieceType.PAWN: ('♙', '♟'),
            PieceType.ROOK: ('♖', '♜'),
            PieceType.KNIGHT: ('♘', '♞'),
            PieceType.BISHOP: ('♗', '♝'),
            PieceType.QUEEN: ('♕', '♛'),
            PieceType.KING: ('♔', '♚')
        }
        return symbols[self.piece_type][0 if self.color == Color.WHITE else 1]

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = Color.WHITE
        self.move_history = []
        self.setup_board()
    
    def setup_board(self):
        # Set up pawns
        for col in range(8):
            self.board[1][col] = Piece(Color.BLACK, PieceType.PAWN)
            self.board[6][col] = Piece(Color.WHITE, PieceType.PAWN)
        
        # Set up other pieces
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                      PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
        
        for col, piece_type in enumerate(piece_order):
            self.board[0][col] = Piece(Color.BLACK, piece_type)
            self.board[7][col] = Piece(Color.WHITE, piece_type)
    
    def display_board(self):
        print("\n  a b c d e f g h")
        for row in range(8):
            print(f"{8-row} ", end="")
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    print(f"{piece} ", end="")
                else:
                    print("· ", end="")
            print(f" {8-row}")
        print("  a b c d e f g h")
        print(f"\nCurrent player: {self.current_player.value.title()}")
    
    def position_to_coords(self, position: str) -> Tuple[int, int]:
        """Convert chess notation (e.g., 'e4') to array coordinates."""
        if len(position) != 2:
            raise ValueError("Invalid position format")
        
        col = ord(position[0].lower()) - ord('a')
        row = 8 - int(position[1])
        
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError("Position out of bounds")
        
        return row, col
    
    def coords_to_position(self, row: int, col: int) -> str:
        """Convert array coordinates to chess notation."""
        return chr(ord('a') + col) + str(8 - row)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at given coordinates."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds."""
        return 0 <= row < 8 and 0 <= col < 8
    
    def is_path_clear(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if path between two positions is clear (excluding destination)."""
        row_dir = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_dir = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        current_row, current_col = from_row + row_dir, from_col + col_dir
        
        while (current_row, current_col) != (to_row, to_col):
            if self.board[current_row][current_col] is not None:
                return False
            current_row += row_dir
            current_col += col_dir
        
        return True
    
    def is_valid_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a move is valid according to piece rules."""
        piece = self.get_piece(from_row, from_col)
        if not piece:
            return False
        
        # Check if it's the player's turn
        if piece.color != self.current_player:
            return False
        
        # Check if destination is valid
        if not self.is_valid_position(to_row, to_col):
            return False
        
        # Check if destination has same color piece
        dest_piece = self.get_piece(to_row, to_col)
        if dest_piece and dest_piece.color == piece.color:
            return False
        
        # Check piece-specific movement rules
        if piece.piece_type == PieceType.PAWN:
            return self.is_valid_pawn_move(from_row, from_col, to_row, to_col)
        elif piece.piece_type == PieceType.ROOK:
            return self.is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece.piece_type == PieceType.KNIGHT:
            return self.is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece.piece_type == PieceType.BISHOP:
            return self.is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece.piece_type == PieceType.QUEEN:
            return self.is_valid_queen_move(from_row, from_col, to_row, to_col)
        elif piece.piece_type == PieceType.KING:
            return self.is_valid_king_move(from_row, from_col, to_row, to_col)
        
        return False
    
    def is_valid_pawn_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        piece = self.get_piece(from_row, from_col)
        direction = -1 if piece.color == Color.WHITE else 1
        
        # Forward move
        if from_col == to_col:
            if to_row == from_row + direction:
                return self.get_piece(to_row, to_col) is None
            elif to_row == from_row + 2 * direction and not piece.has_moved:
                return (self.get_piece(to_row, to_col) is None and 
                       self.get_piece(from_row + direction, from_col) is None)
        
        # Diagonal capture
        elif abs(from_col - to_col) == 1 and to_row == from_row + direction:
            target_piece = self.get_piece(to_row, to_col)
            return target_piece is not None and target_piece.color != piece.color
        
        return False
    
    def is_valid_rook_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        # Must move in straight line
        if from_row != to_row and from_col != to_col:
            return False
        
        return self.is_path_clear(from_row, from_col, to_row, to_col)
    
    def is_valid_knight_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def is_valid_bishop_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        # Must move diagonally
        if abs(to_row - from_row) != abs(to_col - from_col):
            return False
        
        return self.is_path_clear(from_row, from_col, to_row, to_col)
    
    def is_valid_queen_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        return (self.is_valid_rook_move(from_row, from_col, to_row, to_col) or
                self.is_valid_bishop_move(from_row, from_col, to_row, to_col))
    
    def is_valid_king_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        return (abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1 and
                not (from_row == to_row and from_col == to_col))
    
    def find_king(self, color: Color) -> Tuple[int, int]:
        """Find the position of the king for the given color."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    return row, col
        raise ValueError(f"King not found for {color}")
    
    def is_in_check(self, color: Color) -> bool:
        """Check if the king of the given color is in check."""
        king_row, king_col = self.find_king(color)
        
        # Check if any opponent piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    if self.is_valid_move(row, col, king_row, king_col):
                        return True
        
        return False
    
    def would_be_in_check_after_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if making a move would leave the current player in check."""
        # Make a temporary copy of the board
        original_piece = self.board[from_row][from_col]
        captured_piece = self.board[to_row][to_col]
        
        # Make the move
        self.board[to_row][to_col] = original_piece
        self.board[from_row][from_col] = None
        
        # Check if this leaves the king in check
        in_check = self.is_in_check(self.current_player)
        
        # Restore the board
        self.board[from_row][from_col] = original_piece
        self.board[to_row][to_col] = captured_piece
        
        return in_check
    
    def move_piece(self, from_pos: str, to_pos: str) -> bool:
        """Move a piece from one position to another."""
        try:
            from_row, from_col = self.position_to_coords(from_pos)
            to_row, to_col = self.position_to_coords(to_pos)
        except ValueError as e:
            print(f"Invalid position: {e}")
            return False
        
        # Check if the move is valid
        if not self.is_valid_move(from_row, from_col, to_row, to_col):
            print("Invalid move!")
            return False
        
        # Check if this move would leave the king in check
        if self.would_be_in_check_after_move(from_row, from_col, to_row, to_col):
            print("This move would leave your king in check!")
            return False
        
        # Make the move
        piece = self.board[from_row][from_col]
        captured_piece = self.board[to_row][to_col]
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.has_moved = True
        
        # Record the move
        self.move_history.append({
            'from': from_pos,
            'to': to_pos,
            'piece': piece,
            'captured': captured_piece
        })
        
        # Switch players
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        
        return True
    
    def is_checkmate(self, color: Color) -> bool:
        """Check if the given color is in checkmate."""
        if not self.is_in_check(color):
            return False
        
        # Try all possible moves for the given color
        for from_row in range(8):
            for from_col in range(8):
                piece = self.board[from_row][from_col]
                if piece and piece.color == color:
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move(from_row, from_col, to_row, to_col):
                                if not self.would_be_in_check_after_move(from_row, from_col, to_row, to_col):
                                    return False
        
        return True
    
    def is_stalemate(self, color: Color) -> bool:
        """Check if the given color is in stalemate."""
        if self.is_in_check(color):
            return False
        
        # Check if any legal move exists
        for from_row in range(8):
            for from_col in range(8):
                piece = self.board[from_row][from_col]
                if piece and piece.color == color:
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move(from_row, from_col, to_row, to_col):
                                if not self.would_be_in_check_after_move(from_row, from_col, to_row, to_col):
                                    return False
        
        return True

class ChessGame:
    def __init__(self):
        self.board = ChessBoard()
        self.game_over = False
        self.winner = None
    
    def play(self):
        """Main game loop."""
        print("Welcome to Chess!")
        print("Enter moves in format: e2 e4 (from position to position)")
        print("Type 'quit' to exit, 'help' for more commands")
        
        while not self.game_over:
            self.board.display_board()
            
            # Check for game-ending conditions
            if self.board.is_checkmate(self.board.current_player):
                winner = "White" if self.board.current_player == Color.BLACK else "Black"
                print(f"Checkmate! {winner} wins!")
                self.game_over = True
                continue
            
            if self.board.is_stalemate(self.board.current_player):
                print("Stalemate! The game is a draw.")
                self.game_over = True
                continue
            
            if self.board.is_in_check(self.board.current_player):
                print("Check!")
            
            # Get player input
            move = input(f"\n{self.board.current_player.value.title()} to move: ").strip().lower()
            
            if move == 'quit':
                print("Thanks for playing!")
                break
            elif move == 'help':
                self.show_help()
                continue
            
            # Parse move
            if len(move.split()) != 2:
                print("Invalid format. Use: e2 e4")
                continue
            
            from_pos, to_pos = move.split()
            
            # Attempt to make the move
            if self.board.move_piece(from_pos, to_pos):
                print(f"Moved from {from_pos} to {to_pos}")
            else:
                print("Invalid move. Try again.")
    
    def show_help(self):
        """Display help information."""
        print("\n=== Chess Game Help ===")
        print("Move format: [from] [to] (e.g., e2 e4)")
        print("Positions are in chess notation (a1 to h8)")
        print("Commands:")
        print("  help - Show this help")
        print("  quit - Exit the game")
        print("======================")

if __name__ == "__main__":
    game = ChessGame()
    game.play()