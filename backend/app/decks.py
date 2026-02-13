from __future__ import annotations

SPECIAL_CARDS: list[dict] = [
    {"value": "?", "label": "?", "description": "Not enough information to estimate — story needs refinement"},
    {"value": "coffee", "label": "☕", "description": "Need a break — estimation is mentally taxing"},
    {"value": "infinity", "label": "∞", "description": "Too large to estimate — must be split into smaller stories"},
]

DECK_VALUES: dict[str, list[dict]] = {
    "fibonacci": [
        {"value": "0", "label": "0"},
        {"value": "0.5", "label": "½"},
        {"value": "1", "label": "1"},
        {"value": "2", "label": "2"},
        {"value": "3", "label": "3"},
        {"value": "5", "label": "5"},
        {"value": "8", "label": "8"},
        {"value": "13", "label": "13"},
        {"value": "20", "label": "20"},
        {"value": "40", "label": "40"},
        {"value": "100", "label": "100"},
    ],
    "tshirt": [
        {"value": "xs", "label": "XS"},
        {"value": "s", "label": "S"},
        {"value": "m", "label": "M"},
        {"value": "l", "label": "L"},
        {"value": "xl", "label": "XL"},
        {"value": "xxl", "label": "XXL"},
    ],
    "powers2": [
        {"value": "1", "label": "1"},
        {"value": "2", "label": "2"},
        {"value": "4", "label": "4"},
        {"value": "8", "label": "8"},
        {"value": "16", "label": "16"},
        {"value": "32", "label": "32"},
        {"value": "64", "label": "64"},
    ],
}

# Description flavors — keyed by (deck_type, flavor) → list of descriptions
# Each list is positionally matched to the deck values above.

_FIBONACCI_DESCRIPTIONS: dict[str, list[str]] = {
    "technical": [
        "Already done or no effort needed",
        "Trivial — a few minutes, no risk",
        "Very small, well-understood task (baseline reference)",
        "Small task, slightly more involved than a 1",
        "Small-to-medium, straightforward but needs some thought",
        "Medium effort, moderate complexity",
        "Large — significant complexity, consider splitting",
        "Very large — high complexity and uncertainty, should be split",
        "Extremely large — too big for a single sprint",
        "Epic-level — must be decomposed",
        "Massive — a project unto itself, must be decomposed",
    ],
    "idioms": [
        "Done deal — it's already there, nothing to do",
        "Falling off a log — so easy you could do it in your sleep",
        "Low-hanging fruit — practically done for you",
        "Piece of cake — still pretty easy, grab a fork",
        "Not rocket science — needs some thought, but no PhD required",
        "Middle of the road — decent chunk of work, no surprises expected",
        "An arm and a leg — getting too big for one person to carry alone",
        "Just squeaking by — one more point and this must be broken down",
        "Eggs in many baskets — seriously, start breaking this down",
        "Down the rabbit hole — you'll need a map and a flashlight",
        "Here be monsters — way too big, run away and decompose",
    ],
    "animals": [
        "No animal needed, nothing to do",
        "Ant — tiny, carry it without thinking",
        "Mouse — small, quick, fits in your hand",
        "Rabbit — small but hops around a bit",
        "Cat — independent, needs a little attention",
        "Dog — loyal effort, needs a real walk",
        "Wolf — pack-level work, getting serious",
        "Bear — big and powerful, respect it",
        "Hippo — deceptively dangerous, don't underestimate",
        "Elephant — massive, you'll need the whole herd",
        "Whale — ocean-sized, decompose or drown",
    ],
    "software": [
        "Noop — no operation, it's a no-op",
        "Config change — flip a flag, change a constant",
        "One-liner fix — a single well-understood code change",
        "Small bug fix — track it down, patch it, test it",
        "Simple feature — a form, a button, a new endpoint",
        "Feature with tests — real feature work with edge cases",
        "Multi-component — touches several files/modules, needs coordination",
        "Subsystem — new subsystem or major rework of an existing one",
        "Architecture change — structural change across the codebase",
        "Platform migration — moving to a new framework/platform",
        "Full rewrite — start from scratch, are you sure?",
    ],
}

_TSHIRT_DESCRIPTIONS: dict[str, list[str]] = {
    "technical": [
        "Trivial effort",
        "Simple, well-understood",
        "Moderate effort and complexity",
        "Significant effort, may need splitting",
        "High complexity, should be split",
        "Must be decomposed into smaller items",
    ],
    "idioms": [
        "Falling off a log",
        "Piece of cake",
        "Middle of the road",
        "An arm and a leg",
        "Down the rabbit hole",
        "Here be monsters",
    ],
    "animals": [
        "Ant — tiny",
        "Mouse — small and quick",
        "Dog — needs a real walk",
        "Bear — big and powerful",
        "Elephant — massive",
        "Whale — ocean-sized",
    ],
    "software": [
        "Config change",
        "One-liner fix",
        "Simple feature",
        "Multi-component change",
        "Subsystem rework",
        "Architecture change",
    ],
}

_POWERS2_DESCRIPTIONS: dict[str, list[str]] = {
    "technical": [
        "Baseline — simplest meaningful task",
        "Twice the baseline effort",
        "Half a day's focused work",
        "About a day — moderate complexity",
        "Multi-day — significant complexity",
        "Large — consider splitting",
        "Very large — must be decomposed",
    ],
    "idioms": [
        "Low-hanging fruit",
        "Piece of cake",
        "Not rocket science",
        "Middle of the road",
        "An arm and a leg",
        "Down the rabbit hole",
        "Here be monsters",
    ],
    "animals": [
        "Mouse — small and quick",
        "Rabbit — hops around a bit",
        "Dog — needs a real walk",
        "Wolf — pack-level work",
        "Bear — big and powerful",
        "Elephant — massive",
        "Whale — ocean-sized",
    ],
    "software": [
        "One-liner fix",
        "Small bug fix",
        "Simple feature",
        "Feature with tests",
        "Multi-component change",
        "Subsystem rework",
        "Architecture change",
    ],
}

_ALL_DESCRIPTIONS: dict[str, dict[str, list[str]]] = {
    "fibonacci": _FIBONACCI_DESCRIPTIONS,
    "tshirt": _TSHIRT_DESCRIPTIONS,
    "powers2": _POWERS2_DESCRIPTIONS,
}

DECK_TYPES = list(DECK_VALUES.keys())
FLAVORS = ["technical", "idioms", "animals", "software"]


def get_deck_cards(deck_type: str, flavor: str) -> list[dict]:
    """Return card list with descriptions for a deck_type + flavor combo."""
    values = DECK_VALUES.get(deck_type)
    if values is None:
        raise ValueError(f"Unknown deck type: {deck_type}")
    descriptions = _ALL_DESCRIPTIONS.get(deck_type, {}).get(flavor)
    if descriptions is None:
        raise ValueError(f"Unknown flavor '{flavor}' for deck '{deck_type}'")

    cards = []
    for card, desc in zip(values, descriptions):
        cards.append({**card, "description": desc})
    # Append special cards
    cards.extend(SPECIAL_CARDS)
    return cards


def get_all_decks() -> dict:
    """Return all deck definitions for the /api/decks endpoint."""
    result = {}
    for deck_type in DECK_TYPES:
        result[deck_type] = {}
        for flavor in FLAVORS:
            result[deck_type][flavor] = get_deck_cards(deck_type, flavor)
    return result
