import chess
from colorama import Fore, Back, Style, init

init(autoreset=True)

UNICODE_PIECES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

def get_captured_pieces(board):
    """
    Calculates captured pieces for both colors and returns formatted unicode lists.
    """
    start_counts = {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}
    w_lost, b_lost = [], []
    for pt in start_counts:
        w_count = len(board.pieces(pt, chess.WHITE))
        b_count = len(board.pieces(pt, chess.BLACK))
        if w_count < start_counts[pt]:
            w_lost.extend([Fore.CYAN + UNICODE_PIECES[chess.piece_symbol(pt).upper()]] * (start_counts[pt] - w_count))
        if b_count < start_counts[pt]:
            b_lost.extend([Fore.RED + UNICODE_PIECES[chess.piece_symbol(pt).lower()]] * (start_counts[pt] - b_count))
    return w_lost, b_lost

def get_eval_bar(score):
    """
    Generates a visual evaluation bar representation based on the current evaluation score.
    """
    clamped_score = max(-1000, min(1000, score))
    white_blocks = int((clamped_score + 1000) / 2000 * 20)
    black_blocks = 20 - white_blocks
    bar = Fore.CYAN + "█" * white_blocks + Fore.RED + "█" * black_blocks + Style.RESET_ALL
    eval_text = f"{score/100:.2f}"
    if score > 0: eval_text = "+" + eval_text
    return f"Eval: [{bar}] {eval_text}"

def print_board(board, user_is_white=True, last_move=None, current_eval=0, cursor_square=None, selected_square=None):
    """
    Renders the current state of the chessboard dynamically, handling captures, evaluation, and cursor highlights.
    """
    ranks = range(7, -1, -1) if user_is_white else range(8)
    files = range(8) if user_is_white else range(7, -1, -1)
    file_labels = "     a   b   c   d   e   f   g   h" if user_is_white else "     h   g   f   e   d   c   b   a"
    
    w_lost, b_lost = get_captured_pieces(board)
    user_lost = w_lost if user_is_white else b_lost
    bot_lost = b_lost if user_is_white else w_lost
    
    print((Fore.LIGHTBLACK_EX + "Bot Lost: " + Style.RESET_ALL + " ".join(bot_lost)) + "\033[K")
    print(("\n" + Fore.YELLOW + file_labels + Style.RESET_ALL) + "\033[K")
    print("   +---+---+---+---+---+---+---+---+\033[K")
    
    king_sq = board.king(board.turn)
    is_check = board.is_check()
    is_checkmate = board.is_checkmate()

    for rank in ranks:
        row_str = Fore.YELLOW + f" {rank + 1} |" + Style.RESET_ALL
        for file in files:
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            bg_color = ""
            fg_color = Fore.LIGHTBLACK_EX if piece is None else (Fore.CYAN if piece.color == chess.WHITE else Fore.RED)
            char = " . " if piece is None else f" {UNICODE_PIECES[piece.symbol()]} "

            if last_move and (square == last_move.from_square or square == last_move.to_square):
                bg_color = Back.LIGHTBLACK_EX
            
            if piece and piece.piece_type == chess.KING and piece.color == board.turn:
                if is_checkmate: bg_color = Back.RED
                elif is_check: bg_color = Back.YELLOW
            
            if square == selected_square:
                bg_color = Back.GREEN
                
            if square == cursor_square:
                bg_color = Back.WHITE
                fg_color = Fore.BLACK 

            row_str += bg_color + fg_color + char + Style.RESET_ALL + "|"
        
        row_str += Fore.YELLOW + f" {rank + 1}" + Style.RESET_ALL
        print(row_str + "\033[K")
        print("   +---+---+---+---+---+---+---+---+\033[K")
        
    print((Fore.YELLOW + file_labels + "\n" + Style.RESET_ALL) + "\033[K")
    print((Fore.LIGHTBLACK_EX + "You Lost: " + Style.RESET_ALL + " ".join(user_lost)) + "\033[K")
    print(get_eval_bar(current_eval) + "\033[K")