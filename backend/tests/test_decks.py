import pytest

from app.decks import (
    DECK_TYPES,
    DECK_VALUES,
    FLAVORS,
    SPECIAL_CARDS,
    get_all_decks,
    get_deck_cards,
)


def test_deck_types():
    assert "fibonacci" in DECK_TYPES
    assert "tshirt" in DECK_TYPES
    assert "powers2" in DECK_TYPES


def test_flavors():
    assert "technical" in FLAVORS
    assert "idioms" in FLAVORS
    assert "animals" in FLAVORS
    assert "software" in FLAVORS


def test_special_cards():
    values = [c["value"] for c in SPECIAL_CARDS]
    assert "?" in values
    assert "coffee" in values
    assert "infinity" in values


def test_get_deck_cards_fibonacci_technical():
    cards = get_deck_cards("fibonacci", "technical")
    # 11 fibonacci cards + 3 special = 14
    assert len(cards) == 14
    assert cards[0]["value"] == "0"
    assert cards[0]["label"] == "0"
    assert "description" in cards[0]
    # Last 3 are special
    assert cards[-1]["value"] == "infinity"
    assert cards[-2]["value"] == "coffee"
    assert cards[-3]["value"] == "?"


def test_get_deck_cards_tshirt_animals():
    cards = get_deck_cards("tshirt", "animals")
    assert len(cards) == 9  # 6 tshirt + 3 special
    assert cards[0]["value"] == "xs"
    assert "Ant" in cards[0]["description"]


def test_get_deck_cards_powers2_software():
    cards = get_deck_cards("powers2", "software")
    assert len(cards) == 10  # 7 powers2 + 3 special
    assert cards[0]["value"] == "1"


def test_get_deck_cards_invalid_deck():
    with pytest.raises(ValueError, match="Unknown deck type"):
        get_deck_cards("invalid", "technical")


def test_get_deck_cards_invalid_flavor():
    with pytest.raises(ValueError, match="Unknown flavor"):
        get_deck_cards("fibonacci", "nonexistent")


def test_all_deck_flavor_combinations():
    """Every deck_type + flavor combination should produce valid cards."""
    for dt in DECK_TYPES:
        for fl in FLAVORS:
            cards = get_deck_cards(dt, fl)
            expected_count = len(DECK_VALUES[dt]) + len(SPECIAL_CARDS)
            assert len(cards) == expected_count, f"Mismatch for {dt}/{fl}"
            for card in cards:
                assert "value" in card
                assert "label" in card
                assert "description" in card
                assert len(card["description"]) > 0


def test_get_all_decks():
    all_decks = get_all_decks()
    assert set(all_decks.keys()) == set(DECK_TYPES)
    for dt in DECK_TYPES:
        assert set(all_decks[dt].keys()) == set(FLAVORS)
        for fl in FLAVORS:
            assert len(all_decks[dt][fl]) > 0
