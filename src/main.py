import chess
import os
import json
import random
import time   
import sys    
from colorama import Fore, Style
from src.brain import get_best_move, evaluate_board
from src.board_manager import print_board
from src.menu import show_main_menu, get_keypress, show_settings_menu, show_load_menu
from src.trash_talk import (
    get_reaction, get_resign_quote, get_draw_accept_quote, 
    get_draw_reject_quote, get_undo_quote, get_hint_quote
)

SAVE_FILE = "saves.json"
DEFAULT_LIMIT = 3

def clear_screen():
    """Clears the terminal screen securely."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_user_color():
    """Prompts the user to select their side (White, Black, or Random)."""
    print(Fore.YELLOW + "=== SETUP NEW GAME ===" + Style.RESET_ALL)
    while True:
        choice = input(Fore.GREEN + "Choose side (w: White, b: Black, r: Random): " + Style.RESET_ALL).strip().lower()
        if choice in ['w', 'b']:
            return choice == 'w'
        elif choice == 'r':
            return random.choice([True, False])
        print(Fore.YELLOW + "Invalid input. Please enter 'w', 'b', or 'r'." + Style.RESET_ALL)

def get_difficulty():
    """Prompts the user to select AI difficulty."""
    levels = { 'bg': 1, 'e': 2, 'm': 3, 'i': 4, 'h': 5, 'im': 6 }
    print(Fore.CYAN + "\nSelect Difficulty:" + Style.RESET_ALL)
    print("[bg] Beginner | [e] Easy | [m] Medium | [i] Intermediate | [h] Hard | [im] Impossible")
    
    while True:
        choice = input(Fore.GREEN + "Your choice: " + Style.RESET_ALL).strip().lower()
        if choice in levels:
            return levels[choice]
        print(Fore.YELLOW + "Invalid difficulty code. Try again." + Style.RESET_ALL)
        
def print_fixed_header(bot_chat_memory):
    """Prints a static 2-line header zone to prevent the board from shifting dynamically."""
    if bot_chat_memory:
        lines = [line for line in bot_chat_memory.strip().split('\n') if line]
        for i in range(2):
            if i < len(lines):
                print(lines[i] + "\033[K")
            else:
                print("\033[K")
    else:
        print("\033[K\n\033[K")

def load_all_saves():
    """Loads all save slots from the JSON file."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_game_to_slot(slot_str, board, user_is_white, depth, undo_count, hint_count):
    """Writes the current game state to a specific slot in the JSON save file."""
    saves = load_all_saves()
    saves[slot_str] = {
        "moves": " ".join([move.uci() for move in board.move_stack]),
        "user_is_white": user_is_white,
        "depth": depth,
        "undo_count": undo_count,
        "hint_count": hint_count,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(saves, f, indent=4)

def load_game_from_slot(slot_str):
    """Reconstructs the chess board and state variables from a specific JSON save slot."""
    saves = load_all_saves()
    if slot_str in saves:
        data = saves[slot_str]
        board = chess.Board()
        for move_uci in data["moves"].split():
            if move_uci:
                board.push(chess.Move.from_uci(move_uci))
        return board, data["user_is_white"], data["depth"], data["undo_count"], data["hint_count"]
    return None

def prompt_save_slot(board, user_is_white, depth, undo_count, hint_count):
    """Displays an interactive prompt for saving the game into 1 of 3 slots."""
    saves = load_all_saves()
    sys.stdout.write("\033[2A\033[J") 
    
    print(Fore.CYAN + "=== 💾 SELECT SAVE SLOT ===" + Style.RESET_ALL)
    for i in range(1, 4):
        s = str(i)
        if s in saves:
            print(f"[{i}] Overwrite Slot {i} ({saves[s]['timestamp']})")
        else:
            print(f"[{i}] Save to empty Slot {i}")
    print("[c] Cancel")
    
    while True:
        slot_choice = input(Fore.GREEN + "Choose slot (1/2/3/c): " + Style.RESET_ALL).strip().lower()
        if slot_choice in ['1', '2', '3']:
            save_game_to_slot(slot_choice, board, user_is_white, depth, undo_count, hint_count)
            return True, slot_choice
        elif slot_choice == 'c':
            return False, None

def get_interactive_input(board, user_is_white, last_move, current_eval, bot_chat_memory):
    """Handles TUI cursor traversal, directional keybinds, and game execution commands."""
    cursor_file = 4
    cursor_rank = 3 if user_is_white else 4
    selected_square = None
    
    sys.stdout.write("\033[2J\033[H") 
    
    while True:
        cursor_square = chess.square(cursor_file, cursor_rank)
        sys.stdout.write("\033[?25l\033[H")
        
        print_fixed_header(bot_chat_memory)
        print_board(board, user_is_white, last_move, current_eval, cursor_square, selected_square)
        
        sys.stdout.write("\033[K")
        print(Fore.GREEN + "🎯 Move: wasd/hjkl/numpad/arrows | Select: enter | Command: ':'" + Style.RESET_ALL)
        sys.stdout.flush()
        
        key = get_keypress()
        
        if key == '\x1b[A' or key.lower() in ['w', 'k', '8']: 
            cursor_rank = min(7, cursor_rank + 1) if user_is_white else max(0, cursor_rank - 1)
        elif key == '\x1b[B' or key.lower() in ['s', 'j', '2']: 
            cursor_rank = max(0, cursor_rank - 1) if user_is_white else min(7, cursor_rank + 1)
        elif key == '\x1b[D' or key.lower() in ['a', 'h', '4', 'â']: 
            cursor_file = max(0, cursor_file - 1) if user_is_white else min(7, cursor_file + 1)
        elif key == '\x1b[C' or key.lower() in ['d', 'l', '6', 'đ']: 
            cursor_file = min(7, cursor_file + 1) if user_is_white else max(0, cursor_file - 1)
            
        elif key in ['\r', '\n']:
            if selected_square is None:
                piece = board.piece_at(cursor_square)
                if piece and piece.color == board.turn:
                    selected_square = cursor_square
            else:
                if selected_square == cursor_square:
                    selected_square = None 
                else:
                    move = chess.Move(selected_square, cursor_square)
                    piece = board.piece_at(selected_square)
                    if piece and piece.piece_type == chess.PAWN:
                        if (board.turn == chess.WHITE and cursor_rank == 7) or (board.turn == chess.BLACK and cursor_rank == 0):
                            move = chess.Move(selected_square, cursor_square, promotion=chess.QUEEN)
                            
                    if move in board.legal_moves:
                        sys.stdout.write("\033[1A\033[K\033[?25h")
                        return move.uci() 
                    else:
                        selected_square = None 

        elif key == '\x1b': 
            if selected_square is not None:
                selected_square = None
            else:
                sys.stdout.write("\033[?25h")
                return 'quit'
            
        elif key == ':':
            sys.stdout.write("\033[1A\033[K\033[?25h")
            cmd = input(Fore.YELLOW + "Command (:re, :d, :u, :h, :q, :s): " + Style.RESET_ALL).strip().lower()
            if cmd in ['re', 'resign']: return 're'
            if cmd in ['d', 'draw']: return 'd'
            if cmd in ['u', 'undo']: return 'u'
            if cmd in ['h', 'hint']: return 'h'
            if cmd in ['q', 'quit']: return 'quit'
            if cmd in ['s', 'save']: return 'save'
            if cmd in ['n', 'new']: return 'new'

        elif key.lower() == 'q' or key == '\x03':
            sys.stdout.write("\033[?25h")
            return 'quit'
        elif key == '\x13': 
            return 'save'
        elif key == '\x0e': 
            return 'new'

def play_game(input_mode='interactive', load_slot=None):
    """Main application loop for managing player moves, executing AI responses, and routing commands."""
    sys.stdout.write("\033[2J\033[H")
    
    if load_slot:
        loaded_data = load_game_from_slot(load_slot)
        if not loaded_data:
            return 'menu'
        board, user_is_white, depth, undo_count, hint_count = loaded_data
        bot_chat_memory = Fore.CYAN + "[Bot chat]: Thought you ran away? Let's finish this!" + Style.RESET_ALL
    else:
        user_is_white = get_user_color()
        depth = get_difficulty()
        board = chess.Board()
        undo_count, hint_count = DEFAULT_LIMIT, DEFAULT_LIMIT
        bot_chat_memory = Fore.CYAN + "[Bot chat]: Let's get to work! Prepare yourself." + Style.RESET_ALL
        
    bot_is_white = not user_is_white
    last_move = board.move_stack[-1] if board.move_stack else None
    current_eval = evaluate_board(board)
    
    while not board.is_game_over(claim_draw=True):
        if board.can_claim_draw():
            sys.stdout.write("\033[2J\033[H")
            print_board(board, user_is_white, last_move, current_eval)
            print(Fore.YELLOW + "\n=== GAME OVER: DRAW (Repetition) ===" + Style.RESET_ALL)
            print(Fore.MAGENTA + "[Bot chat]: You're too stubborn. We're done here!" + Style.RESET_ALL)
            break

        is_user_turn = (board.turn == user_is_white)
                       
        if is_user_turn:
            old_score = current_eval
            while True:
                if input_mode == 'interactive':
                    user_cmd = get_interactive_input(board, user_is_white, last_move, current_eval, bot_chat_memory)
                    bot_chat_memory = ""
                else:
                    sys.stdout.write("\033[2J\033[H") 
                    if bot_chat_memory:
                        print(bot_chat_memory)
                        bot_chat_memory = ""
                    print_board(board, user_is_white, last_move, current_eval)
                    
                    raw_input = input(Fore.GREEN + "\n Move (e.g., e4) or Cmd (re/d/u/h/q/s): " + Style.RESET_ALL).strip()
                    user_cmd = raw_input.lower()
                    
                    if user_cmd in ['q', 'quit']: user_cmd = 'quit'
                    if user_cmd in ['s', 'save']: user_cmd = 'save'
                    if user_cmd in ['n', 'new']: user_cmd = 'new'

                if user_cmd == 'quit':
                    sys.stdout.write(f"\033[{10}A\033[J") 
                    while True:
                        ans = input(Fore.YELLOW + "⚠️ Are you sure you want to quit? The game data will be lost if you don't save (y/n): " + Style.RESET_ALL).strip().lower()
                        if ans == 'y':
                            return 'menu'
                        elif ans == 'n':
                            break
                        else:
                            print(Fore.RED + "Please write 'y' or 'n', idiot!" + Style.RESET_ALL) 
                    continue

                elif user_cmd == 'save':
                    saved, slot = prompt_save_slot(board, user_is_white, depth, undo_count, hint_count)
                    if saved:
                        bot_chat_memory = Fore.GREEN + f"[System]: Game saved to Slot {slot}!" + Style.RESET_ALL
                    else:
                        bot_chat_memory = Fore.YELLOW + "[System]: Save cancelled." + Style.RESET_ALL
                    continue

                elif user_cmd == 'new':
                    ans = input(Fore.YELLOW + "⚠️ Abandon current game and start a New Game? (y/n): " + Style.RESET_ALL).strip().lower()
                    if ans == 'y':
                        return 'restart' 
                    continue

                elif user_cmd in ['resign', 're']:
                    sys.stdout.write("\033[2J\033[H")
                    print_board(board, user_is_white, last_move, current_eval)
                    print(Fore.MAGENTA + f"\n[Bot Chat]: {get_resign_quote()}" + Style.RESET_ALL)
                    print(Fore.YELLOW + "=== YOU SURRENDERED. BOT WINS! ===" + Style.RESET_ALL)
                    print(Fore.LIGHTBLACK_EX + "\n[Ctrl+N] or [n] for New Game | [Enter] to return to Main Menu" + Style.RESET_ALL)
                    while True:
                        key = get_keypress()
                        if key == '\x0e' or key.lower() == 'n': return 'restart'
                        elif key in ['\r', '\n']: return 'menu'

                elif user_cmd in ['draw', 'd']:
                    bot_score = current_eval if bot_is_white else -current_eval
                    if bot_score < -200:
                        print(Fore.MAGENTA + f"\n[Bot Chat]: {get_draw_accept_quote()}" + Style.RESET_ALL)
                        print(Fore.YELLOW + "=== GAME OVER: DRAW (Bot accepted) ===" + Style.RESET_ALL)
                        break
                    else:
                        print(Fore.MAGENTA + f"\n[Bot Chat]: {get_draw_reject_quote()}" + Style.RESET_ALL)
                        time.sleep(2)
                        continue 

                elif user_cmd in ['undo', 'u']:
                    if undo_count > 0:
                        if len(board.move_stack) >= 2:
                            board.pop()
                            board.pop()
                            undo_count -= 1
                            bot_chat_memory = Fore.MAGENTA + f"[Bot Chat]: {get_undo_quote()} ({undo_count} left)" + Style.RESET_ALL
                            last_move = board.move_stack[-1] if board.move_stack else None
                            current_eval = evaluate_board(board)
                            continue
                        else:
                            print(Fore.YELLOW + "Nothing to undo yet!" + Style.RESET_ALL)
                            time.sleep(1)
                            continue
                    else:
                        sys.stdout.write("\033[2J\033[H")
                        print_board(board, user_is_white, last_move, current_eval)
                        print(Fore.RED + "\n" + "="*45)
                        print(" 🔒 CHESS PREMIUM SUBSCRIPTION REQUIRED 🔒".center(45))
                        print("="*45)
                        print(" You are out of free Undos!")
                        print(" Upgrade to VIP for only $99.99/month.")
                        print(" [1] Take my money! (Pay)")
                        print(" [2] I'm too broke. (No need)")
                        print("="*45 + Style.RESET_ALL)
                        
                        while True:
                            pay_choice = input(Fore.GREEN + "Choose (1/2): " + Style.RESET_ALL).strip()
                            if pay_choice == '1':
                                print(Fore.MAGENTA + "\n[Bot Chat]: LMAO! Python scripts don't take credit cards. Make a move!" + Style.RESET_ALL)
                                break
                            elif pay_choice == '2':
                                print(Fore.MAGENTA + "\n[Bot Chat]: Broke AND bad at chess. Stop begging!" + Style.RESET_ALL)
                                break
                            else:
                                print(Fore.YELLOW + "Press 1 or 2, genius." + Style.RESET_ALL)
                        time.sleep(3)
                    continue

                elif user_cmd in ['hint', 'h']:
                    if hint_count > 0:
                        hint_count -= 1
                        hint_move, _ = get_best_move(board, depth=3) if random.random() < 0.5 else (random.choice(list(board.legal_moves)), 0)
                        bot_chat_memory = Fore.MAGENTA + f"[Bot Chat]: {get_hint_quote()}\n" + Style.RESET_ALL
                        bot_chat_memory += Fore.CYAN + f"💡 Hint: TRY PLAYING {board.san(hint_move)}" + Style.RESET_ALL
                        continue
                    else:
                        sys.stdout.write("\033[2J\033[H")
                        print_board(board, user_is_white, last_move, current_eval)
                        print(Fore.RED + "\n" + "="*45)
                        print(" 🔒 CHESS PREMIUM SUBSCRIPTION REQUIRED 🔒".center(45))
                        print("="*45)
                        print(" You are out of free Hints!")
                        print(" Unlock the Grandmaster AI for $49.99.")
                        print(" [1] Take my money! (Pay)")
                        print(" [2] I'm too broke. (No need)")
                        print("="*45 + Style.RESET_ALL)
                        
                        while True:
                            pay_choice = input(Fore.GREEN + "Choose (1/2): " + Style.RESET_ALL).strip()
                            if pay_choice == '1':
                                print(Fore.MAGENTA + "\n[Bot Chat]: Error 404: Bank account not found. Play the game!" + Style.RESET_ALL)
                                break
                            elif pay_choice == '2':
                                print(Fore.MAGENTA + "\n[Bot Chat]: Empty wallet, empty head. Make a move!" + Style.RESET_ALL)
                                break
                            else:
                                print(Fore.YELLOW + "Press 1 or 2, genius." + Style.RESET_ALL)
                        time.sleep(3)
                    continue

                else:
                    try:
                        move = chess.Move.from_uci(user_cmd) if input_mode == 'interactive' else board.parse_san(raw_input)
                        board.push(move)
                        last_move = move
                        current_eval = evaluate_board(board)
                        break 
                    except ValueError:
                        bot_chat_memory = Fore.YELLOW + "Invalid move! Try again." + Style.RESET_ALL
                        continue

        else:
            sys.stdout.write("\033[2J\033[H")
            print_fixed_header(bot_chat_memory)
            if bot_chat_memory:
                print(bot_chat_memory)
                bot_chat_memory = ""
                
            print_board(board, user_is_white, last_move, current_eval)
            print(Fore.CYAN + f"Bot is thinking (Depth {depth})...\033[K" + Style.RESET_ALL)
            sys.stdout.flush()
            
            old_score = current_eval
            bot_move, new_score = get_best_move(board, depth=depth)
            
            reaction = get_reaction(old_score, new_score, bot_is_white)
            if reaction: 
                bot_chat_memory += Fore.MAGENTA + f"[Bot Chat]: {reaction}\n" + Style.RESET_ALL
            
            if bot_move:
                bot_chat_memory += Fore.CYAN + f"Bot played: {board.san(bot_move)}" + Style.RESET_ALL
                board.push(bot_move)
                last_move = bot_move
                current_eval = new_score

    sys.stdout.write("\033[2J\033[H")
    print_board(board, user_is_white, last_move, current_eval)
    print(Fore.YELLOW + "=== GAME OVER ===" + Style.RESET_ALL)
    print("Result:", board.result(claim_draw=True))
    
    print(Fore.LIGHTBLACK_EX + "\n[Ctrl+N] or [n] for New Game | [Enter] to return to Main Menu" + Style.RESET_ALL)
    while True:
        key = get_keypress()
        if key == '\x0e' or key.lower() == 'n': 
            return 'restart'
        elif key in ['\r', '\n']:
            return 'menu'

def main():
    current_input_mode = 'interactive' 
    
    while True:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
        
        choice = show_main_menu()
        
        if choice == 0: 
            while True:
                result = play_game(current_input_mode, load_slot=None)
                if result == 'restart':
                    continue 
                else:
                    break 
                    
        elif choice == 1: 
            sys.stdout.write("\033[2J\033[H")
            selected_slot = show_load_menu()
            if selected_slot:
                while True:
                    result = play_game(current_input_mode, load_slot=selected_slot)
                    if result == 'restart':
                        selected_slot = None 
                        continue 
                    else:
                        break
            
        elif choice == 2: 
            sys.stdout.write("\033[2J\033[H")
            current_input_mode = show_settings_menu(current_input_mode)
            
        elif choice == 3: 
            sys.stdout.write("\033[2J\033[H")
            print(Fore.CYAN + "=== HOW TO PLAY ===" + Style.RESET_ALL)
            print("- Movement (Interactive): WASD, HJKL, Arrows, Numpad")
            print("- Movement (Classic): Type standard chess notation (e.g., e4, Nf3)")
            print("- Commands: u (Undo), h (Hint), re (Resign), d (Draw)")
            print("- System: q/Ctrl+C/ESC (Quit), Ctrl+S (Save), Ctrl+N (New Game)")
            print(Fore.LIGHTBLACK_EX + "\nPress Enter to return to Main Menu..." + Style.RESET_ALL)
            input()
            
        elif choice == 4: 
            sys.stdout.write("\033[2J\033[H")
            print(Fore.YELLOW + "Developer: KuroShiro" + Style.RESET_ALL)
            print("A really good (or toxic) beginner loves chess (That's all, or not...)")
            print(Fore.LIGHTBLACK_EX + "\nPress Enter to return to Main Menu..." + Style.RESET_ALL)
            input()
            
        elif choice == 5: 
            sys.stdout.write("\033[2J\033[H")
            print(Fore.RED + "Escaping already? Goodbye." + Style.RESET_ALL)
            break

if __name__ == "__main__":
    main()