import contextlib
import io
import os
import random
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np

import cards
import engine
import gameboard
import random_moves
import territory
from gameboard import GameBoard

# Builds a board where each listed player owns the named territories and `rest` owns everything else
def board_with(territories: dict[int, list[str]], num_players: int = 2, rest: int = 1, armies: int = 1) -> GameBoard:
    owners = np.full(42, rest)
    for player, names in territories.items():
        for name in names:
            owners[territory.indexer(name)] = player
    return GameBoard(num_players, np.full(42, armies), owners)

def quietly(function, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        function(*args)

def test_map_is_standard_risk():
    assert (territory.adjMatrix == territory.adjMatrix.T).all()
    assert territory.adjMatrix.sum() // 2 == 83
    assert (territory.continents.sum(0) == 1).all()
    assert territory.check_adjacency(territory.indexer("north africa"), territory.indexer("brazil"))

def test_new_boards_do_not_share_arrays():
    a, b = GameBoard(), GameBoard()
    assert a.armies is not b.armies and a.owners is not b.owners
    assert (a.owners == 0).sum() == 21 and sorted(a.armies) == sorted([1, 2, 3] * 14)
    c = a.copy()
    c.armies[0] += 10
    assert a.armies[0] != c.armies[0] and c.num_players == a.num_players

def test_setup_splits_territories_evenly():
    for num_players in range(gameboard.MIN_PLAYERS, gameboard.MAX_PLAYERS + 1):
        counts = np.bincount(GameBoard(num_players).owners, minlength = num_players)
        assert len(counts) == num_players and counts.max() - counts.min() <= 1
    for bad in (1, 7):
        try:
            GameBoard(bad)
        except ValueError:
            continue
        raise AssertionError(f"{bad} players should not be allowed")

def test_player_counts():
    assert gameboard.check_player_counts(1, 1) is None
    assert gameboard.check_player_counts(0, 6) is None
    assert gameboard.check_player_counts(1, 0) is not None
    assert gameboard.check_player_counts(4, 3) is not None
    assert gameboard.player_name(0, 2) == "Green (human)" and gameboard.player_name(2, 2) == "Blue (AI)"

def test_battle_win_tie_loss():
    brazil, peru = territory.indexer("brazil"), territory.indexer("peru")

    board = board_with({0: ["brazil"]})
    board.armies[brazil], board.armies[peru] = 5, 3
    board.battle(brazil, peru, 4)
    assert board.owners[peru] == 0 and board.armies[peru] == 1 and board.armies[brazil] == 1

    board = board_with({0: ["brazil"]})
    board.armies[brazil], board.armies[peru] = 5, 4
    board.battle(brazil, peru, 4)
    assert board.owners[peru] == 1 and board.armies[peru] == 1

    board = board_with({0: ["brazil"]})
    board.armies[brazil], board.armies[peru] = 3, 5
    board.battle(brazil, peru, 2)
    assert board.owners[peru] == 1 and board.armies[peru] == 3

def test_capture_goes_to_the_attacker():
    # Blue (2) attacks Red (1) in a three player game; Green (0) is not involved
    board = board_with({1: ["peru"], 2: ["brazil"]}, num_players = 3, rest = 0)
    brazil, peru = territory.indexer("brazil"), territory.indexer("peru")
    board.armies[brazil] = 4
    board.battle(brazil, peru, 3)
    assert board.owners[peru] == 2
    assert not board.is_alive(1)

def test_deploy_count_with_continent_bonus():
    board = board_with({0: ["argentina", "brazil", "peru", "venezuela"]})
    assert board.deploy_count(0) == 3 + 2
    # player 1 owns the other 38 territories: 38 // 3 = 12, plus every continent except South America
    assert board.deploy_count(1) == 12 + 3 + 7 + 5 + 5 + 2

def test_move_checks():
    board = board_with({0: ["brazil", "peru"]}, armies = 3)
    brazil, peru, argentina = (territory.indexer(n) for n in ("brazil", "peru", "argentina"))
    assert board.can_attack(0, brazil, argentina, 2)
    assert not board.can_attack(0, brazil, argentina, 3)   # must leave 1 behind
    assert not board.can_attack(0, brazil, peru, 1)        # can't attack yourself
    assert not board.can_attack(0, brazil, territory.indexer("india"), 1)  # not adjacent
    assert board.can_fortify(0, brazil, peru, 2)
    assert not board.can_fortify(0, brazil, argentina, 1)  # not owned

def test_total_connections():
    board = board_with({0: ["alaska", "alberta", "ontario", "brazil"]})
    connected = territory.total_connections(territory.indexer("alaska"), board.owned(0))
    assert set(territory.territory_names[connected]) == {"alberta", "ontario"}

def test_turn_order_skips_eliminated_players():
    # four players, but Red (1) owns nothing
    board = board_with({2: ["brazil"], 3: ["peru"]}, num_players = 4, rest = 0)
    assert board.alive_players() == [0, 2, 3]
    assert board.next_player(0) == 2 and board.next_player(2) == 3 and board.next_player(3) == 0
    assert board.winner() is None

    board = board_with({}, num_players = 4, rest = 3)
    assert board.winner() == 3 and board.next_player(3) == 3

def test_standings():
    board = board_with({1: ["brazil", "peru"], 2: ["india"]}, num_players = 3, rest = 0)
    assert [row[0] for row in board.standings()] == [0, 1, 2]

def test_engine_only_touches_its_own_territories():
    for num_players in (2, 4, 6):
        for _ in range(10):
            board = GameBoard(num_players)
            player = num_players - 1
            before = board.copy()
            quietly(engine.deploy, board, player)
            changed = np.flatnonzero(board.armies != before.armies)
            assert len(changed) == 1 and before.owners[changed[0]] == player

            quietly(engine.attack, board, player)
            quietly(engine.fortify, board, player)
            assert (board.armies >= 1).all()
            # the engine never loses territories on its own turn, and only takes them from others
            assert board.owned(player).sum() >= before.owned(player).sum()
            assert np.all((board.owners == before.owners) | (board.owners == player))

def test_random_moves_stay_legal():
    for num_players in (2, 3, 6):
        for _ in range(20):
            board = GameBoard(num_players)
            for player in board.alive_players():
                quietly(random_moves.deploy, board, player)
                quietly(random_moves.attack, board, player)
                quietly(random_moves.fortify, board, player)
            assert (board.armies >= 1).all()

def test_multiplayer_games_finish():
    # seeded so the test always plays the same games
    random.seed(0)
    np.random.seed(0)
    for num_players in (3, 6):
        board = GameBoard(num_players)
        current, turns = 0, 0
        while not board.is_won() and turns < 3000:
            ai = engine if current % 2 == 0 else random_moves
            board.start_turn(current)
            quietly(ai.deploy, board, current)
            quietly(ai.attack, board, current)
            if not board.is_won():
                quietly(ai.fortify, board, current)
                board.end_turn(current)
            # every card is always in exactly one place
            assert sorted(sum(board.hands, []) + board.draw_pile + board.discard_pile) == list(range(44))
            current = board.next_player(current)
            turns += 1
        assert board.is_won(), f"{num_players} player game did not finish"
        assert board.sets_traded > 0

def test_deck():
    assert sorted(cards.DECK_ORDER) == list(range(44))
    assert cards.DECK_ORDER[21] == 42 and cards.DECK_ORDER[-1] == 43
    symbols = [cards.symbol(card) for card in range(44)]
    assert symbols.count("Infantry") == symbols.count("Cavalry") == symbols.count("Artillery") == 14
    assert symbols.count("Wild") == 2
    assert cards.card_name(0) == "Afghanistan (Infantry)" and cards.card_name(42) == "Wild"

def test_valid_sets():
    assert cards.is_valid_set([0, 3, 6])        # three Infantry
    assert cards.is_valid_set([0, 1, 2])        # one of each
    assert cards.is_valid_set([0, 3, 42])       # two cards and a wild
    assert cards.is_valid_set([42, 43, 5])      # two wilds and a card
    assert not cards.is_valid_set([0, 3, 1])    # Infantry, Infantry, Cavalry
    assert not cards.is_valid_set([0, 3])       # too few
    assert not cards.is_valid_set([0, 0, 3])    # the same card twice
    assert cards.all_sets([0, 3, 1, 4]) == []   # two Infantry and two Cavalry make no set
    assert len(cards.all_sets([0, 1, 2, 3, 4])) > 0  # any 5 cards always hold a set

def test_set_values_escalate():
    assert [cards.set_value(n) for n in range(8)] == [4, 6, 8, 10, 12, 15, 20, 25]

def test_earning_cards():
    board = board_with({0: ["brazil"]})
    brazil, peru = territory.indexer("brazil"), territory.indexer("peru")

    # no capture, no card
    board.start_turn(0)
    assert board.end_turn(0) is None and board.hands[0] == []

    # a capture earns the top card, and only one per turn
    board.start_turn(0)
    board.armies[brazil] = 5
    board.battle(brazil, peru, 4)
    assert board.end_turn(0) == cards.DECK_ORDER[0] and board.hands[0] == [cards.DECK_ORDER[0]]
    assert board.end_turn(0) is None and board.draw_pile[0] == cards.DECK_ORDER[1]

    # an empty draw pile reuses traded cards in the order they were traded
    board.draw_pile, board.discard_pile = [], [7, 5]
    board.start_turn(0)
    board.armies[peru] = 5
    board.battle(peru, territory.indexer("argentina"), 4)
    assert board.end_turn(0) == 7 and board.draw_pile == [5] and board.discard_pile == []

def test_trading():
    board = board_with({0: ["afghanistan", "argentina"]}, armies = 1)
    board.hands[0] = [0, 3, 6, 42]
    troops, bonus = board.trade(0, [0, 3, 6])
    # Afghanistan is the first owned territory in the set, so it gets the +2
    assert troops == 4 and bonus == 0 and board.armies[0] == 3 and board.armies[territory.indexer("argentina")] == 1
    assert board.hands[0] == [42] and board.discard_pile == [0, 3, 6] and board.sets_traded == 1
    assert cards.set_value(board.sets_traded) == 6

    for bad in ([42, 1, 2], [0, 3, 6]):    # cards not in hand
        try:
            board.trade(0, bad)
        except ValueError:
            continue
        raise AssertionError("trading cards not in hand should fail")

def test_best_set_is_deterministic():
    owned = np.zeros(42, dtype = bool)
    owned[territory.indexer("peru")] = True
    # Peru (28) is Cavalry: prefers a set with an owned territory, and keeps the wild when it can
    assert sorted(cards.best_set([0, 3, 28, 42, 2], owned)) == [0, 2, 28]
    assert sorted(cards.best_set([0, 3, 6, 42, 1], owned)) == [0, 3, 6]
    assert cards.best_set([0, 1, 42], np.zeros(42, dtype = bool)) == [0, 1, 42]
    assert cards.best_set([0, 3], owned) is None

def test_forced_trades_and_taking_cards():
    # Green (0) eliminates Red (1), who only owns Peru, and takes Red's cards
    board = board_with({1: ["peru"], 2: ["india"]}, num_players = 3, rest = 0)
    board.hands[0] = [0, 1, 2]
    board.hands[1] = [3, 4, 5]
    assert not board.must_trade(0)
    board.armies[territory.indexer("brazil")] = 5
    board.battle(territory.indexer("brazil"), territory.indexer("peru"), 4)
    assert board.hands[0] == [0, 1, 2, 3, 4, 5] and board.hands[1] == []
    assert board.must_trade(0, cards.ELIMINATION_TRADE_HAND)

    # the engine trades down to 4 or fewer cards and places the troops
    before = int(board.armies.sum())
    quietly(engine.place_troops, board, 0, quietly_trade(board, 0))
    assert len(board.hands[0]) <= 4 and board.sets_traded == 1 and int(board.armies.sum()) >= before + 4

def quietly_trade(board: GameBoard, player: int) -> int:
    with contextlib.redirect_stdout(io.StringIO()):
        return engine.trade_cards(board, player)

def test_engine_trades_when_it_must():
    board = board_with({0: ["afghanistan", "argentina", "china"]}, armies = 2)
    board.hands[0] = [0, 3, 6, 1, 42]
    before = int(board.armies.sum())
    quietly(engine.deploy, board, 0)
    # deploy count 3, the 4 troop set, and +2 on Afghanistan
    assert board.sets_traded == 1 and len(board.hands[0]) == 2 and int(board.armies.sum()) == before + 3 + 4 + 2

def test_cards_are_deterministic():
    # the same board and the same moves give exactly the same cards
    def play(seed: int) -> tuple:
        np.random.seed(seed)
        board = GameBoard(3)
        current = 0
        for _ in range(60):
            if board.is_won():
                break
            board.start_turn(current)
            quietly(engine.deploy, board, current)
            quietly(engine.attack, board, current)
            if not board.is_won():
                quietly(engine.fortify, board, current)
                board.end_turn(current)
            current = board.next_player(current)
        return board.hands, board.draw_pile, board.discard_pile, board.sets_traded, board.armies.tolist(), board.owners.tolist()
    assert play(3) == play(3)

if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print("passed", name)
