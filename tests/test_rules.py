import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np

import engine
import random_moves
import territory
from gameboard import GameBoard

def board_with(player_territories: list[str], armies: int = 1) -> GameBoard:
    owners = np.zeros(42, dtype = bool)
    for name in player_territories:
        owners[territory.indexer(name)] = True
    return GameBoard(np.full(42, armies), owners)

def test_map_is_standard_risk():
    assert (territory.adjMatrix == territory.adjMatrix.T).all()
    assert territory.adjMatrix.sum() // 2 == 83
    assert (territory.continents.sum(0) == 1).all()
    assert territory.check_adjacency(territory.indexer("north africa"), territory.indexer("brazil"))

def test_new_boards_do_not_share_arrays():
    a, b = GameBoard(), GameBoard()
    assert a.armies is not b.armies and a.owners is not b.owners
    assert a.owners.sum() == 21 and sorted(a.armies) == sorted([1, 2, 3] * 14)
    c = a.copy()
    c.armies[0] += 10
    assert a.armies[0] != c.armies[0]

def test_battle_win_tie_loss():
    board = board_with(["brazil"])
    brazil, peru = territory.indexer("brazil"), territory.indexer("peru")

    board.armies[brazil], board.armies[peru] = 5, 3
    board.battle(brazil, peru, 4)
    assert board.owners[peru] and board.armies[peru] == 1 and board.armies[brazil] == 1

    board = board_with(["brazil"])
    board.armies[brazil], board.armies[peru] = 5, 4
    board.battle(brazil, peru, 4)
    assert not board.owners[peru] and board.armies[peru] == 1

    board = board_with(["brazil"])
    board.armies[brazil], board.armies[peru] = 3, 5
    board.battle(brazil, peru, 2)
    assert not board.owners[peru] and board.armies[peru] == 3

def test_deploy_count_with_continent_bonus():
    board = board_with(["argentina", "brazil", "peru", "venezuela"])
    assert board.deploy_count(True) == 3 + 2
    # the AI owns the other 38 territories: 38 // 3 = 12, plus every continent except South America
    assert board.deploy_count(False) == 12 + 3 + 7 + 5 + 5 + 2

def test_move_checks():
    board = board_with(["brazil", "peru"], armies = 3)
    brazil, peru, argentina = (territory.indexer(n) for n in ("brazil", "peru", "argentina"))
    assert board.can_attack(True, brazil, argentina, 2)
    assert not board.can_attack(True, brazil, argentina, 3)   # must leave 1 behind
    assert not board.can_attack(True, brazil, peru, 1)        # can't attack yourself
    assert not board.can_attack(True, brazil, territory.indexer("india"), 1)  # not adjacent
    assert board.can_fortify(True, brazil, peru, 2)
    assert not board.can_fortify(True, brazil, argentina, 1)  # not owned

def test_total_connections():
    board = board_with(["alaska", "alberta", "ontario", "brazil"])
    connected = territory.total_connections(territory.indexer("alaska"), board.owners)
    assert set(territory.territory_names[connected]) == {"alberta", "ontario"}

def test_engine_only_touches_its_own_territories():
    for _ in range(20):
        board = GameBoard()
        before = board.copy()
        engine.deploy(board, False)
        changed = np.flatnonzero(board.armies != before.armies)
        assert len(changed) == 1 and not before.owners[changed[0]]

        engine.attack(board, False)
        engine.fortify(board, False)
        assert (board.armies >= 1).all()
        # the engine never loses territories on its own turn
        assert (~board.owners).sum() >= (~before.owners).sum()

def test_random_moves_stay_legal():
    for _ in range(50):
        board = GameBoard()
        for player in (True, False):
            random_moves.deploy(board, player)
            random_moves.attack(board, player)
            random_moves.fortify(board, player)
        assert (board.armies >= 1).all()

if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print("passed", name)
