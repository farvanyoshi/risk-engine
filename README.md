# risk-engine

A deterministic version of the board game **Risk** in Python and NumPy. You play against a computer opponent on the classic 42-territory world map, in the terminal or on a clickable map.

## Quick start

Requires Python 3.12+.

```bash
pip install -r requirements.txt
python main.py            # play in the terminal against the engine
python main.py --gui      # play on the clickable map
python main.py --easy     # play against random moves instead of the engine
python main.py --seed 5   # replay the same starting board
```

The terminal game only needs `numpy`. The GUI also needs `opencv-python`, `pillow`, and tkinter (on Linux: `sudo apt install python3-tk`).

## Rules

- **Setup:** the 42 territories are split randomly, 21 each, with 1–3 troops on every territory.
- **Turn:** deploy → attack (as many times as you want) → fortify (once).
- **Deploy:** you get `max(territories owned ÷ 3, 3)` troops, plus a bonus for each continent you fully hold: Asia 7, Europe 5, North America 5, Africa 3, South America 2, Oceania 2.
- **Attack:** from a territory with at least 2 troops into a bordering enemy territory, sending any number of troops but leaving at least 1 behind. There are no dice. The bigger side wins:
  - more attackers than defenders → you capture the territory, and your survivors (attackers − defenders) move in
  - equal → the defender is left with 1 troop
  - fewer attackers → the defender loses that many troops
- **Fortify:** move troops once between two of your territories joined by a chain of your own territories, leaving at least 1 behind.
- **Win:** own all 42 territories.

### Terminal controls
Type territory names (any case), e.g. `eastern united states`. Type `help` to list everyone's territories and troops, and press Enter on an empty line to skip or end a phase.

### GUI controls
Click your territory (and the target, for attack or fortify), type a troop amount, and press **Confirm Action**. **Next Stage** / **Skip Stage** moves to the next phase. The AI moves after your fortify phase, and its moves appear in the log.

## The AI

- **`engine.py`** (default): uses the heuristics in `scoring.py`, which weigh threat from neighboring enemy troops, held continents, choke points, and connectivity.
  - It deploys all its troops to its most important territory.
  - It keeps making the capture that most improves its board score (`minimax_attack`, looking `DEPTH` attacks ahead).
  - It fortifies its most important territory from its least important connected one.
- **`random_moves.py`** (`--easy`): random but legal moves.

`python simulate.py --games 200` plays the engine against random moves and reports the win rate.

## Project structure

| File | Role |
|---|---|
| `main.py` | Entry point: terminal game loop and command-line options |
| `gameboard.py` | `GameBoard`: troops and owners for every territory, battles, fortifying, move checks, deploy counts, win check |
| `territory.py` | Map data: territory names, adjacency matrix, continents, bonuses, and helpers |
| `player.py` | Terminal prompts for the human player |
| `engine.py` | Heuristic search AI |
| `scoring.py` | Board and territory scoring used by the engine |
| `random_moves.py` | Random AI |
| `interface/gui.py` | tkinter + OpenCV clickable map |
| `simulate.py` | Engine vs random-moves simulation |
| `tests/test_rules.py` | Rule tests (`python tests/test_rules.py` or `pytest`) |

The whole game state is two NumPy arrays: `armies` (troops per territory) and `owners` (`True` = player, `False` = AI). Territory `i` in both arrays is `territory.territory_names[i]`.

## Not included
Risk cards, dice, and more than two players.
