# KuroShiro's New Chess Ever
A fully terminal-based Chess Engine featuring an intuitive, interactive UI. Powered by ***Negamax*** with ***Alpha-Beta Pruning*** and ***Quiescence Search***, this bot doesn't just calculate moves — it comes equipped with a highly toxic personality. It will mercilessly roast your blunders, laugh at your draw offers, and even throw up a satirical "Paywall" if you abuse the help features. Well, hope you not be frustrated (I really hope so  (｡･∀･)ﾉﾞ).


## Key Features
- **Interactive TUI**: Smooth cursor navigation and piece selection directly in your terminal using your preferred keybinds (WASD, HJKL, Arrows, or Numpad).

- **Dual Input Modes**: Easily toggle between the modern ***Interactive*** cursor mode and the ***Classic*** text-based mode (SAN) via the Settings menu. (would be loved by both modern and traditional players I guest (. ❛ ᴗ ❛.) ).

- **Robust Game Management**: A modern ***Main Menu*** integrated with a ***Save/Load*** system featuring 3 dedicated slots (saved locally via JSON).

- **Assist & "Pay-to-Win" Mechanics**: You get a limited number of ***Undos*** and ***Hints***. Run out, and the bot will freeze the board to hit you with a premium subscription prompt (prepare your money or keep playing without any hint or undo, and I don't recommend you to do that).

- **Advanced AI & Analytics**: Includes ***Opening Book*** integration, a real-time ***Evaluation Bar***, an anti-shuffling algorithm, and a visual tracker for captured pieces.


## Installation Guide
This project is optimized for environments that support ANSI truecolor and Unicode characters (Linux, macOS, or WSL / Unbuntu).

1. Clone the repository and navigate to the directory:

```bash
git clone <my-repo-link>
cd chess
```

2. Initialize and activate a Virtual Environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the engine as a local CLI package (this automatically handles all dependencies):

```bash
pip install -e .
```


## How to Play
Once installed and activated, you don't need to navigate to any specific folder. Just launch the game from anywhere in your terminal by typing:

```bash
kurochess
```

**Wanna know about the commands, rules or controls? Go find it yourself ヾ(≧▽≦)o**

> **Disclaimer**: This bot has no chill. Play at your own emotional risk.

****PS***: If you have any questions, feedback, or recommendations, feel free to reach out via the email on my GitHub profile!*


**NO LICENSE INCLUDED**