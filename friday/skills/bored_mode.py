# skills/bored_mode.py
import random
from skills.os_control import open_youtube, open_spotify, open_netflix, open_url


JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs, Sir.",
    "I told my computer I needed a break. Now it will not stop sending me Kit-Kat ads, Sir.",
    "Why do Java developers wear glasses? Because they do not C sharp, Sir.",
    "A SQL query walks into a bar, walks up to two tables and asks, may I join you? Sir.",
    "Why was the computer cold? It left its Windows open, Sir.",
    "I would tell you a UDP joke, Sir, but you might not get it.",
    "There are 10 types of people in the world, Sir. Those who understand binary and those who do not.",
]

FUN_FACTS = [
    "Did you know, Sir, that a group of flamingos is called a flamboyance? Fitting, I think.",
    "Honey never spoils, Sir. Archaeologists have found 3000 year old honey in Egyptian tombs that was still edible.",
    "The shortest war in history lasted only 38 to 45 minutes, Sir. It was between Britain and Zanzibar in 1896.",
    "Octopuses have three hearts, Sir. Two pump blood to the gills and one pumps it to the rest of the body.",
    "A day on Venus is longer than a year on Venus, Sir. It rotates so slowly.",
    "The founder of Match.com lost his girlfriend to someone she met on Match.com, Sir.",
]

ACTIVITIES = [
    ("music", "Shall I put on some music to lift the mood, Sir?", open_spotify),
    ("youtube", "Perhaps a good video on YouTube, Sir?", open_youtube),
    ("netflix", "There is always Netflix, Sir. A good series never fails.", open_netflix),
]


def handle_bored() -> tuple[str, callable | None]:
    """
    Handle when Sir is bored.
    Returns (response_text, action_function_or_None)
    """
    choice = random.randint(1, 4)

    if choice == 1:
        joke = random.choice(JOKES)
        fact = random.choice(FUN_FACTS)
        response = (
            f"Allow me to brighten your day, Sir. {joke} "
            f"And here is something fascinating — {fact} "
            f"Shall I put on some music or find something interesting on YouTube?"
        )
        return response, None

    elif choice == 2:
        response = (
            "Right then Sir, I refuse to let you be bored on my watch. "
            "I am opening Spotify for you. Music has been scientifically proven to boost mood and productivity. "
            "Shall I also pull up something on YouTube while we are at it?"
        )
        return response, open_spotify

    elif choice == 3:
        response = (
            "Boredom is simply the brain asking for stimulation, Sir. "
            "Let me open YouTube — there is an entire universe of content waiting for you. "
            "Or shall I find something specific? Just say the word."
        )
        return response, lambda: open_youtube("")

    else:
        fact = random.choice(FUN_FACTS)
        response = (
            f"I have just the cure for boredom, Sir. {fact} "
            "I could also open Netflix if you fancy something more immersive. "
            "Or perhaps a quick game? Just tell me what sounds good."
        )
        return response, open_netflix


def suggest_activity(time_of_day: str = "") -> str:
    """Proactive suggestion based on time."""
    suggestions = {
        "morning": "Good morning Sir. Might I suggest starting with some light music while you plan your day?",
        "afternoon": "The afternoon slump is real Sir. A short break and some music might do wonders.",
        "evening": "Evening Sir. Perhaps some Netflix to wind down after a productive day?",
        "night": "It is getting late Sir. Shall I put on something relaxing to help you unwind?",
    }
    return suggestions.get(time_of_day, random.choice(list(suggestions.values())))
