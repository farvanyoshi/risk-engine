import itertools

import numpy as np
import numpy.typing as npt

import territory

'''
Risk cards, without any shuffling:
- Cards 0 to 41 are the territory cards, in the same order as territory.territory_names
- Cards 42 and 43 are wilds
- Every territory card has a symbol, and the deck is always drawn in DECK_ORDER, so everyone knows what comes next
'''

SYMBOLS: list[str] = ["Infantry", "Cavalry", "Artillery"]
WILDS: tuple[int, int] = (42, 43)

# The draw pile from top to bottom: the first half of the territories, a wild, the second half, and the other wild
DECK_ORDER: list[int] = list(range(0, 21)) + [WILDS[0]] + list(range(21, 42)) + [WILDS[1]]

# Troops for the 1st, 2nd, 3rd... set traded by anyone; after these, each set is worth 5 more than the last
SET_VALUES: list[int] = [4, 6, 8, 10, 12, 15]

# Extra troops placed on a traded card's territory if the trader owns it
TERRITORY_BONUS = 2

# A player with this many cards at the start of their deploy phase must trade
MUST_TRADE_HAND = 5
# Taking an eliminated player's cards and ending up with this many means trading right away
ELIMINATION_TRADE_HAND = 6

def is_wild(card: int) -> bool:
    return card in WILDS

def symbol(card: int) -> str:
    return "Wild" if is_wild(card) else SYMBOLS[card % 3]

def card_name(card: int) -> str:
    if is_wild(card):
        return "Wild"
    return f"{territory.territory_names[card].title()} ({symbol(card)})"

# Three of the same symbol, one of each symbol, or any two cards with a wild
def is_valid_set(cards: list[int]) -> bool:
    if len(cards) != 3 or len(set(cards)) != 3:
        return False
    if any(is_wild(card) for card in cards):
        return True
    symbols = {symbol(card) for card in cards}
    return len(symbols) == 1 or len(symbols) == 3

def all_sets(hand: list[int]) -> list[list[int]]:
    return [list(cards) for cards in itertools.combinations(hand, 3) if is_valid_set(list(cards))]

# Troops for a set when `sets_traded` sets have already been traded in the game
def set_value(sets_traded: int) -> int:
    if sets_traded < len(SET_VALUES):
        return SET_VALUES[sets_traded]
    return SET_VALUES[-1] + 5 * (sets_traded - len(SET_VALUES) + 1)

# The territory that gets the +2 bonus: the first card in the set (by card number) whose territory the trader owns
def bonus_territory(cards: list[int], owned: npt.NDArray[np.bool]) -> int | None:
    for card in sorted(cards):
        if not is_wild(card) and owned[card]:
            return card
    return None

# The set worth the most (counting the territory bonus), keeping wilds when possible, then using the lowest card numbers
def best_set(hand: list[int], owned: npt.NDArray[np.bool]) -> list[int] | None:
    sets = all_sets(hand)
    if not sets:
        return None
    return min(sets, key = lambda cards: (
        bonus_territory(cards, owned) is None,
        sum(is_wild(card) for card in cards),
        sorted(cards)
    ))

def trade_message(player_label: str, traded: list[int], troops: int, bonus: int | None) -> str:
    message = f"{player_label} traded {', '.join(card_name(card) for card in traded)} for {troops} troops"
    if bonus is not None:
        message += f", plus {TERRITORY_BONUS} on {territory.territory_names[bonus].title()}"
    return message
