import random

RESIGN_QUOTES = [
    "Waving the white flag already? What a coward!",
    "Escaping before it gets any uglier. Probably your best move all game.",
    "Fast on the 'resign' button. Muscle memory from typing 'GG' too much?"
]

DRAW_ACCEPT_QUOTES = [
    "You looked so pathetic, I felt bad. Here's your charity draw.",
    "Draw! Now you're free to go back to reading 'Chess for Dummies'.",
    "Fine, I'll show mercy. Wouldn't want you to uninstall the game in tears."
]

DRAW_REJECT_QUOTES = [
    "A draw? In your dreams, kid. I'm about to end your whole career!",
    "Begging for a draw while getting crushed? The audacity.",
    "No draw! I'm playing until you physically beg for mercy."
]

UNDO_QUOTES = [
    "Another mouse slip? Or is your brain just lagging?",
    "I'll let you take it back, but a trash position is still trash, even if you undo 10 times.",
    "Takeback? Fine, I'll play blindfolded just to keep it fair."
]

HINT_QUOTES = [
    "Crying for a hint? Fine, try this one...",
    "The master is giving you a move. Whether it wins or blunders, that's on you!",
    "Here is a god-tier move (or a massive blunder, guess we'll find out)."
]

PAYWALL_QUOTES = [
    "Out of free trials! Please swipe a $50 gift card to unlock the VIP package.",
    "Premium feature locked. Please insert your credit card into the nearest USB port.",
    "Your free trial has expired. Upgrade to Premium if you want to keep embarrassing yourself!"
]

def get_resign_quote():
    return random.choice(RESIGN_QUOTES)

def get_draw_accept_quote():
    return random.choice(DRAW_ACCEPT_QUOTES)

def get_draw_reject_quote():
    return random.choice(DRAW_REJECT_QUOTES)

def get_undo_quote():
    return random.choice(UNDO_QUOTES)

def get_hint_quote():
    return random.choice(HINT_QUOTES)

def get_reaction(old_score, new_score, bot_is_white):
    """
    Evaluates the score difference between moves and returns a toxic string response based on the evaluation.
    """
    if bot_is_white:
        user_diff = old_score - new_score 
    else:
        user_diff = new_score - old_score 

    if user_diff < -300:
        quotes = [
            "Absolute blunder... Textbooks call that a sacrifice, I just call it a charity handout.",
            "Are you using ChatGPT to play? Because it looks like it just disconnected.",
            "How many brain cells did you burn trying to come up with that move?",
            "Chess clearly isn't your forte. Maybe stick to Checkers?"
        ]
        return random.choice(quotes)

    elif user_diff > 300:
        quotes = [
            "You're definitely using an engine! No human actually plays like that.",
            "Pure luck. That was a mouse slip...",
            "Don't get cocky. I just let you have that to see what you'd do."
        ]
        return random.choice(quotes)

    elif random.random() < 0.45: 
        quotes = [
            "Hurry up! My CPU is literally freezing to death waiting for you.",
            "Did you really spend all that time just to calculate a blunder?",
            "Yawn... Are you done yet?",
            "I just took a full nap and you STILL haven't made a move."
        ]
        return random.choice(quotes)

    return ""