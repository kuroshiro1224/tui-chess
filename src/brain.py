import chess
from chess import polyglot
import time
import random

PIECE_VALUES = {
    chess.PAWN: 100, chess.KNIGHT: 330, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
}

PAWN_PST = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_PST = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

KING_PST = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,  10,   0,   0,  10,  30,  20
]

PST = {
    chess.PAWN: PAWN_PST,
    chess.KNIGHT: KNIGHT_PST,
    chess.BISHOP: BISHOP_PST,
    chess.ROOK: [0]*64,
    chess.QUEEN: [0]*64,
    chess.KING: KING_PST 
}

SEARCH_START_TIME = 0
SEARCH_TIME_LIMIT = 10.0
CACHE = {}
EXACT, LOWERBOUND, UPPERBOUND = 0, 1, 2

class TimeOutException(Exception):
    pass

def get_piece_value(piece, square):
    base_val = PIECE_VALUES[piece.piece_type]
    pst_table = PST[piece.piece_type]
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    if piece.color == chess.WHITE:
        pst_index = (7 - rank) * 8 + file
    else:
        pst_index = rank * 8 + file
    return base_val + pst_table[pst_index]

def evaluate_board(board):
    """
    Evaluates the board position from the perspective of the side to move.
    """
    if board.is_checkmate():
        return -99999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0
        
    evaluation = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            val = get_piece_value(piece, square)
            if piece.color == board.turn:
                evaluation += val
            else:
                evaluation -= val

    if board.is_repetition(2):
        evaluation += 50
        
    return evaluation

def mvv_lva_score(board, move):
    """Most Valuable Victim - Least Valuable Attacker (MVV-LVA) heuristic."""
    if not board.is_capture(move):
        return 0
        
    attacker = board.piece_at(move.from_square)
    victim = board.piece_at(move.to_square)
    
    if victim is None and board.is_en_passant(move):
        victim_val = PIECE_VALUES[chess.PAWN]
        attacker_val = PIECE_VALUES[chess.PAWN]
    elif victim and attacker:
        victim_val = PIECE_VALUES[victim.piece_type]
        attacker_val = PIECE_VALUES[attacker.piece_type]
    else:
        return 0
        
    return 10 * victim_val - attacker_val

def order_moves(board):
    """Orders moves to maximize Alpha-Beta pruning efficiency."""
    moves = list(board.legal_moves)
    random.shuffle(moves) 
    moves.sort(key=lambda move: mvv_lva_score(board, move), reverse=True)
    return moves

def quiescence_search(board, alpha, beta):
    if time.time() - SEARCH_START_TIME > SEARCH_TIME_LIMIT:
        raise TimeOutException()
        
    stand_pat = evaluate_board(board)
    
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat
        
    ordered_captures = [m for m in board.legal_moves if board.is_capture(m)]
    ordered_captures.sort(key=lambda move: mvv_lva_score(board, move), reverse=True)

    for move in ordered_captures:
        board.push(move)
        score = -quiescence_search(board, -beta, -alpha)
        board.pop()
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
            
    return alpha

def negamax(board, depth, alpha, beta):
    if time.time() - SEARCH_START_TIME > SEARCH_TIME_LIMIT:
        raise TimeOutException()
    
    if board.can_claim_draw():
        return 0

    board_hash = board.fen() 
    if board_hash in CACHE:
        entry = CACHE[board_hash]
        if entry['depth'] >= depth:
            if entry['flag'] == EXACT: 
                return entry['score']
            elif entry['flag'] == LOWERBOUND: 
                alpha = max(alpha, entry['score'])
            elif entry['flag'] == UPPERBOUND: 
                beta = min(beta, entry['score'])
            if alpha >= beta: 
                return entry['score']

    if board.is_game_over():
        return evaluate_board(board)
    if depth == 0:
        return quiescence_search(board, alpha, beta)

    ordered_moves = order_moves(board)
    original_alpha = alpha
    best_score = -float('inf')

    for move in ordered_moves:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()
        
        if score > best_score:
            best_score = score
            
        if score > alpha:
            alpha = score
            
        if alpha >= beta:
            break 
            
    flag = EXACT
    if best_score <= original_alpha: 
        flag = UPPERBOUND
    elif best_score >= beta: 
        flag = LOWERBOUND
        
    CACHE[board_hash] = {'score': best_score, 'depth': depth, 'flag': flag}
    return best_score

def get_best_move(board, depth=3):
    global SEARCH_START_TIME, SEARCH_TIME_LIMIT
    SEARCH_START_TIME = time.time()
    SEARCH_TIME_LIMIT = 10.0  
    
    try:
        with polyglot.open_reader("opening_book.bin") as reader:
            entry = reader.weighted_choice(board) 
            return entry.move, 0
    except:
        pass 

    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None, 0
        
    best_move = random.choice(legal_moves) 
    best_eval = -evaluate_board(board)
    original_stack_len = len(board.move_stack)

    try:
        for current_depth in range(1, depth + 1):
            ordered_moves = order_moves(board)
            
            if best_move in ordered_moves:
                ordered_moves.remove(best_move)
                ordered_moves.insert(0, best_move)
                
            current_best_move = None
            alpha = -float('inf')
            beta = float('inf')
            current_best_score = -float('inf')
            
            for move in ordered_moves:
                board.push(move)
                score = -negamax(board, current_depth - 1, -beta, -alpha)
                board.pop()
                
                if score > current_best_score:
                    current_best_score = score
                    current_best_move = move
                    
                if score > alpha:
                    alpha = score
            
            if current_best_move is not None:
                best_move = current_best_move
                best_eval = current_best_score if board.turn == chess.WHITE else -current_best_score
                
    except TimeOutException:
        while len(board.move_stack) > original_stack_len:
            board.pop()
    except Exception:
        while len(board.move_stack) > original_stack_len:
            board.pop()

    return best_move, best_eval