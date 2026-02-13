from __future__ import annotations

SPECIAL_CARDS: list[dict] = [
    {"value": "?", "label": "?", "description": {
        "en": "Not enough information to estimate — story needs refinement",
        "de": "Nicht genug Informationen — Story muss verfeinert werden",
    }},
    {"value": "coffee", "label": "☕", "description": {
        "en": "Need a break — estimation is mentally taxing",
        "de": "Pause nötig — Schätzen ist anstrengend",
    }},
    {"value": "infinity", "label": "∞", "description": {
        "en": "Too large to estimate — must be split into smaller stories",
        "de": "Zu groß zum Schätzen — muss in kleinere Stories aufgeteilt werden",
    }},
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
# Each description is a dict with "en" and "de" translations.

_FIBONACCI_DESCRIPTIONS: dict[str, list[dict]] = {
    "technical": [
        {"en": "Already done or no effort needed", "de": "Bereits erledigt oder kein Aufwand nötig"},
        {"en": "Trivial — a few minutes, no risk", "de": "Trivial — wenige Minuten, kein Risiko"},
        {"en": "Very small, well-understood task (baseline reference)", "de": "Sehr klein, gut verstanden (Referenzaufgabe)"},
        {"en": "Small task, slightly more involved than a 1", "de": "Kleine Aufgabe, etwas mehr als eine 1"},
        {"en": "Small-to-medium, straightforward but needs some thought", "de": "Klein bis mittel, einfach aber braucht etwas Überlegung"},
        {"en": "Medium effort, moderate complexity", "de": "Mittlerer Aufwand, moderate Komplexität"},
        {"en": "Large — significant complexity, consider splitting", "de": "Groß — erhebliche Komplexität, Aufteilen erwägen"},
        {"en": "Very large — high complexity and uncertainty, should be split", "de": "Sehr groß — hohe Komplexität und Unsicherheit, sollte aufgeteilt werden"},
        {"en": "Extremely large — too big for a single sprint", "de": "Extrem groß — zu viel für einen einzelnen Sprint"},
        {"en": "Epic-level — must be decomposed", "de": "Epic-Niveau — muss zerlegt werden"},
        {"en": "Massive — a project unto itself, must be decomposed", "de": "Riesig — ein Projekt für sich, muss zerlegt werden"},
    ],
    "idioms": [
        {"en": "Done deal — it's already there, nothing to do", "de": "Abgemacht — ist schon da, nichts zu tun"},
        {"en": "Falling off a log — so easy you could do it in your sleep", "de": "Kinderleicht — das geht im Schlaf"},
        {"en": "Low-hanging fruit — practically done for you", "de": "Tiefhängende Früchte — fast schon erledigt"},
        {"en": "Piece of cake — still pretty easy, grab a fork", "de": "Ein Kinderspiel — immer noch leicht, ran an den Kuchen"},
        {"en": "Not rocket science — needs some thought, but no PhD required", "de": "Keine Raketenwissenschaft — braucht etwas Nachdenken, aber kein Doktortitel nötig"},
        {"en": "Middle of the road — decent chunk of work, no surprises expected", "de": "Mittelmaß — ordentliches Stück Arbeit, keine Überraschungen"},
        {"en": "An arm and a leg — getting too big for one person to carry alone", "de": "Ganz schön happig — zu viel für eine Person allein"},
        {"en": "Just squeaking by — one more point and this must be broken down", "de": "Gerade noch so — ein Punkt mehr und es muss aufgeteilt werden"},
        {"en": "Eggs in many baskets — seriously, start breaking this down", "de": "Viele Baustellen — ernsthaft, fang an aufzuteilen"},
        {"en": "Down the rabbit hole — you'll need a map and a flashlight", "de": "Ab in den Kaninchenbau — du brauchst eine Karte und eine Taschenlampe"},
        {"en": "Here be monsters — way too big, run away and decompose", "de": "Hier lauern Drachen — viel zu groß, weglaufen und zerlegen"},
    ],
    "animals": [
        {"en": "No animal needed, nothing to do", "de": "Kein Tier nötig, nichts zu tun"},
        {"en": "Ant — tiny, carry it without thinking", "de": "Ameise — winzig, ohne Nachdenken erledigt"},
        {"en": "Mouse — small, quick, fits in your hand", "de": "Maus — klein, schnell, passt in die Hand"},
        {"en": "Rabbit — small but hops around a bit", "de": "Hase — klein, aber hüpft etwas herum"},
        {"en": "Cat — independent, needs a little attention", "de": "Katze — eigenständig, braucht etwas Aufmerksamkeit"},
        {"en": "Dog — loyal effort, needs a real walk", "de": "Hund — treuer Aufwand, braucht einen richtigen Spaziergang"},
        {"en": "Wolf — pack-level work, getting serious", "de": "Wolf — Rudelarbeit, wird ernst"},
        {"en": "Bear — big and powerful, respect it", "de": "Bär — groß und mächtig, Respekt zeigen"},
        {"en": "Hippo — deceptively dangerous, don't underestimate", "de": "Nilpferd — täuschend gefährlich, nicht unterschätzen"},
        {"en": "Elephant — massive, you'll need the whole herd", "de": "Elefant — massiv, du brauchst die ganze Herde"},
        {"en": "Whale — ocean-sized, decompose or drown", "de": "Wal — ozeangroß, zerlegen oder untergehen"},
    ],
    "software": [
        {"en": "Noop — no operation, it's a no-op", "de": "Noop — keine Operation, ein No-Op"},
        {"en": "Config change — flip a flag, change a constant", "de": "Config-Änderung — Flag umschalten, Konstante ändern"},
        {"en": "One-liner fix — a single well-understood code change", "de": "Einzeiler-Fix — eine einzelne, gut verstandene Codeänderung"},
        {"en": "Small bug fix — track it down, patch it, test it", "de": "Kleiner Bugfix — finden, patchen, testen"},
        {"en": "Simple feature — a form, a button, a new endpoint", "de": "Einfaches Feature — ein Formular, ein Button, ein neuer Endpunkt"},
        {"en": "Feature with tests — real feature work with edge cases", "de": "Feature mit Tests — echte Feature-Arbeit mit Grenzfällen"},
        {"en": "Multi-component — touches several files/modules, needs coordination", "de": "Mehrere Komponenten — betrifft mehrere Dateien/Module, braucht Koordination"},
        {"en": "Subsystem — new subsystem or major rework of an existing one", "de": "Subsystem — neues Subsystem oder größerer Umbau eines bestehenden"},
        {"en": "Architecture change — structural change across the codebase", "de": "Architekturänderung — strukturelle Änderung quer durch die Codebasis"},
        {"en": "Platform migration — moving to a new framework/platform", "de": "Plattform-Migration — Umzug auf ein neues Framework/Plattform"},
        {"en": "Full rewrite — start from scratch, are you sure?", "de": "Komplett-Neubau — von vorne anfangen, bist du sicher?"},
    ],
}

_TSHIRT_DESCRIPTIONS: dict[str, list[dict]] = {
    "technical": [
        {"en": "Trivial effort", "de": "Trivialer Aufwand"},
        {"en": "Simple, well-understood", "de": "Einfach, gut verstanden"},
        {"en": "Moderate effort and complexity", "de": "Moderater Aufwand und Komplexität"},
        {"en": "Significant effort, may need splitting", "de": "Erheblicher Aufwand, Aufteilen erwägen"},
        {"en": "High complexity, should be split", "de": "Hohe Komplexität, sollte aufgeteilt werden"},
        {"en": "Must be decomposed into smaller items", "de": "Muss in kleinere Teile zerlegt werden"},
    ],
    "idioms": [
        {"en": "Falling off a log", "de": "Kinderleicht"},
        {"en": "Piece of cake", "de": "Ein Kinderspiel"},
        {"en": "Middle of the road", "de": "Mittelmaß"},
        {"en": "An arm and a leg", "de": "Ganz schön happig"},
        {"en": "Down the rabbit hole", "de": "Ab in den Kaninchenbau"},
        {"en": "Here be monsters", "de": "Hier lauern Drachen"},
    ],
    "animals": [
        {"en": "Ant — tiny", "de": "Ameise — winzig"},
        {"en": "Mouse — small and quick", "de": "Maus — klein und schnell"},
        {"en": "Dog — needs a real walk", "de": "Hund — braucht einen richtigen Spaziergang"},
        {"en": "Bear — big and powerful", "de": "Bär — groß und mächtig"},
        {"en": "Elephant — massive", "de": "Elefant — massiv"},
        {"en": "Whale — ocean-sized", "de": "Wal — ozeangroß"},
    ],
    "software": [
        {"en": "Config change", "de": "Config-Änderung"},
        {"en": "One-liner fix", "de": "Einzeiler-Fix"},
        {"en": "Simple feature", "de": "Einfaches Feature"},
        {"en": "Multi-component change", "de": "Mehrere Komponenten"},
        {"en": "Subsystem rework", "de": "Subsystem-Umbau"},
        {"en": "Architecture change", "de": "Architekturänderung"},
    ],
}

_POWERS2_DESCRIPTIONS: dict[str, list[dict]] = {
    "technical": [
        {"en": "Baseline — simplest meaningful task", "de": "Basis — einfachste sinnvolle Aufgabe"},
        {"en": "Twice the baseline effort", "de": "Doppelter Basisaufwand"},
        {"en": "Half a day's focused work", "de": "Ein halber Tag konzentrierte Arbeit"},
        {"en": "About a day — moderate complexity", "de": "Ungefähr ein Tag — moderate Komplexität"},
        {"en": "Multi-day — significant complexity", "de": "Mehrere Tage — erhebliche Komplexität"},
        {"en": "Large — consider splitting", "de": "Groß — Aufteilen erwägen"},
        {"en": "Very large — must be decomposed", "de": "Sehr groß — muss zerlegt werden"},
    ],
    "idioms": [
        {"en": "Low-hanging fruit", "de": "Tiefhängende Früchte"},
        {"en": "Piece of cake", "de": "Ein Kinderspiel"},
        {"en": "Not rocket science", "de": "Keine Raketenwissenschaft"},
        {"en": "Middle of the road", "de": "Mittelmaß"},
        {"en": "An arm and a leg", "de": "Ganz schön happig"},
        {"en": "Down the rabbit hole", "de": "Ab in den Kaninchenbau"},
        {"en": "Here be monsters", "de": "Hier lauern Drachen"},
    ],
    "animals": [
        {"en": "Mouse — small and quick", "de": "Maus — klein und schnell"},
        {"en": "Rabbit — hops around a bit", "de": "Hase — hüpft etwas herum"},
        {"en": "Dog — needs a real walk", "de": "Hund — braucht einen richtigen Spaziergang"},
        {"en": "Wolf — pack-level work", "de": "Wolf — Rudelarbeit"},
        {"en": "Bear — big and powerful", "de": "Bär — groß und mächtig"},
        {"en": "Elephant — massive", "de": "Elefant — massiv"},
        {"en": "Whale — ocean-sized", "de": "Wal — ozeangroß"},
    ],
    "software": [
        {"en": "One-liner fix", "de": "Einzeiler-Fix"},
        {"en": "Small bug fix", "de": "Kleiner Bugfix"},
        {"en": "Simple feature", "de": "Einfaches Feature"},
        {"en": "Feature with tests", "de": "Feature mit Tests"},
        {"en": "Multi-component change", "de": "Mehrere Komponenten"},
        {"en": "Subsystem rework", "de": "Subsystem-Umbau"},
        {"en": "Architecture change", "de": "Architekturänderung"},
    ],
}

_ALL_DESCRIPTIONS: dict[str, dict[str, list[dict]]] = {
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
