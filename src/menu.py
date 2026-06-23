import sys
import tty
import termios
import math
import os
import json
import time
from colorama import Fore, Back, Style, init

init(autoreset=True)

ASCII_ART = r"""
  _  __                  _____ _     _           
 | |/ /                 / ____| |   (_)          
 | ' /_   _ _ __ ___   | (___ | |__  _ _ __ ___  
 |  <| | | | '__/ _ \   \___ \| '_ \| | '__/ _ \ 
 | . \ |_| | | | (_) |  ____) | | | | | | | (_) |
 |_|\_\__,_|_|  \___/  |_____/|_| |_|_|_|  \___/ 
"""

def get_rainbow_text(text):
    """
    Generates truecolor RGB rainbow text (lolcat style) using sine waves.
    """
    result = ""
    lines = text.split('\n')
    for row_idx, line in enumerate(lines):
        for col_idx, char in enumerate(line):
            freq = 0.1
            i = row_idx * 2 + col_idx 
            r = int(math.sin(freq * i + 0) * 127 + 128)
            g = int(math.sin(freq * i + 2 * math.pi / 3) * 127 + 128)
            b = int(math.sin(freq * i + 4 * math.pi / 3) * 127 + 128)
            result += f"\033[38;2;{r};{g};{b}m{char}"
        if row_idx < len(lines) - 1:
            result += "\n"
    result += "\033[0m"
    return result

def get_keypress():
    """
    Reads and returns a single keypress (including escape sequences) from the terminal.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def show_main_menu():
    """
    Displays the main interactive menu and returns the selected option index.
    """
    print(get_rainbow_text(ASCII_ART))
    print(Fore.RED + "      [ KUROSHIRO LEARNS TO PLAY CHESS ]" + Style.RESET_ALL + "\n")
    
    menu_items = ['Play New Game', 'Load Saved Game', 'Settings', 'Tutorial', 'About', 'Quit']
    current_row = 0
    
    print("\n" * len(menu_items))
    
    while True:
        sys.stdout.write(f"\033[{len(menu_items) + 1}A")
        for idx, row in enumerate(menu_items):
            if idx == current_row:
                sys.stdout.write("\r" + Fore.BLACK + Back.WHITE + f"  > {row} <  " + Style.RESET_ALL + "\033[K\n")
            else:
                sys.stdout.write("\r" + f"    {row}    " + "\033[K\n")
        
        sys.stdout.write("\r" + Fore.LIGHTBLACK_EX + "  (w/s, Arrows, k/j, 8/2 to move. Enter to select)" + Style.RESET_ALL + "\033[K\n")
        sys.stdout.flush()

        key = get_keypress()

        if key == '\x1b[A' or key.lower() in ['w', 'k', '8']:
            current_row = (current_row - 1) % len(menu_items)
        elif key == '\x1b[B' or key.lower() in ['s', 'j', '2']:
            current_row = (current_row + 1) % len(menu_items)
        elif key in ['\r', '\n']:
            sys.stdout.write(f"\033[{len(menu_items) + 1}A")
            for _ in range(len(menu_items) + 1):
                sys.stdout.write("\r\033[K\n")
            sys.stdout.write(f"\033[{len(menu_items) + 1}A")
            return current_row
        elif key == '\x03':
            return 5 

def show_load_menu():
    """
    Displays the Load Game menu with 3 slots and returns the selected slot key.
    """
    saves = {}
    if os.path.exists("saves.json"):
        try:
            with open("saves.json", "r") as f:
                saves = json.load(f)
        except:
            pass
    
    slot_keys = ['1', '2', '3']
    modes = []
    for k in slot_keys:
        if k in saves:
            modes.append(f"Slot {k}, {saves[k]['timestamp']}")
        else:
            modes.append(f"Slot {k}: [ EMPTY ]")
    modes.append("Back to Main Menu")
    
    current_row = 0
    print(Fore.CYAN + "=== 💾 LOAD SAVED GAME ===" + Style.RESET_ALL)
    print("\n" * len(modes))
    
    while True:
        sys.stdout.write(f"\033[{len(modes) + 1}A")
        for idx, row in enumerate(modes):
            if idx == current_row:
                sys.stdout.write("\r" + Fore.BLACK + Back.WHITE + f"  > {row} <  " + Style.RESET_ALL + "\033[K\n")
            else:
                sys.stdout.write("\r" + f"    {row}    " + "\033[K\n")
                
        sys.stdout.write("\r" + Fore.LIGHTBLACK_EX + "  (Enter to select)" + Style.RESET_ALL + "\033[K\n")
        sys.stdout.flush()

        key = get_keypress()
        if key == '\x1b[A' or key.lower() in ['w', 'k', '8']:
            current_row = (current_row - 1) % len(modes)
        elif key == '\x1b[B' or key.lower() in ['s', 'j', '2']:
            current_row = (current_row + 1) % len(modes)
        elif key in ['\r', '\n']:
            sys.stdout.write(f"\033[{len(modes) + 2}A")
            for _ in range(len(modes) + 3):
                sys.stdout.write("\r\033[K\n")
            sys.stdout.write(f"\033[{len(modes) + 3}A")
            
            if current_row < 3:
                slot = slot_keys[current_row]
                if slot in saves:
                    return slot
                else:
                    sys.stdout.write(Fore.RED + "Cannot load an empty slot!\n" + Style.RESET_ALL)
                    time.sleep(1)
                    sys.stdout.write("\033[1A\033[K")
                    continue
            else:
                return None # Back to menu

def show_settings_menu(current_mode):
    """
    Displays the settings menu for selecting the input mode and returns the updated mode.
    """
    modes = ['Interactive (wasd/arrows/khjl/8426)', 'Classic Typing (SAN Text)']
    current_row = 0 if current_mode == 'interactive' else 1
    
    print(Fore.CYAN + "=== ⚙️ SETTINGS: INPUT MODE ===" + Style.RESET_ALL)
    print("\n" * len(modes))
    
    while True:
        sys.stdout.write(f"\033[{len(modes) + 1}A")
        for idx, row in enumerate(modes):
            if idx == current_row:
                sys.stdout.write("\r" + Fore.BLACK + Back.WHITE + f"  > {row} <  " + Style.RESET_ALL + "\033[K\n")
            else:
                sys.stdout.write("\r" + f"    {row}    " + "\033[K\n")
                
        sys.stdout.write("\r" + Fore.LIGHTBLACK_EX + "  (Enter to save and return)" + Style.RESET_ALL + "\033[K\n")
        sys.stdout.flush()

        key = get_keypress()
        if key == '\x1b[A' or key.lower() in ['w', 'k', '8']:
            current_row = (current_row - 1) % len(modes)
        elif key == '\x1b[B' or key.lower() in ['s', 'j', '2']:
            current_row = (current_row + 1) % len(modes)
        elif key in ['\r', '\n']:
            sys.stdout.write(f"\033[{len(modes) + 2}A")
            for _ in range(len(modes) + 3):
                sys.stdout.write("\r\033[K\n")
            sys.stdout.write(f"\033[{len(modes) + 3}A")
            return 'interactive' if current_row == 0 else 'text'