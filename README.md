# risk-engine

A deterministic version of the board game **Risk** in Python and NumPy, for 2 to 6 players on the classic 42-territory world map. Any mix of human and AI players works, in the terminal or on a clickable map. Humans take turns at the same keyboard (hotseat).

## Quick start

Requires Python 3.12+.

```bash
pip install -r requirements.txt
python main.py                      # terminal game; asks how many human and AI players
python main.py --humans 2 --ais 2   # 2 humans and 2 AIs, without asking
python main.py --humans 0 --ais 4   # watch 4 AIs play each other
python main.py --gui                # clickable map; pick the players on the start screen
python main.py --easy               # AIs use random moves instead of the engine
python main.py --seed 5             # replay the same starting board
```

The terminal game only needs `numpy`. The GUI also needs `opencv-python`, `pillow`, and tkinter (on Linux: `sudo apt install python3-tk`).

## Rules

- **Players:** 2 to 6 in total, any mix of humans and AIs. Humans take the first seats, then the AIs. Each player has a color: Green, Red, Blue, Yellow, Purple, Orange. Green goes first.
- **Setup:** the 42 territories are split randomly and as evenly as possible (21 each with 2 players, 7 each with 6), with 1–3 troops on every territory.
- **Turn:** deploy → attack (as many times as you want) → fortify (once).
- **Deploy:** you get `max(territories owned ÷ 3, 3)` troops, plus a bonus for each continent you fully hold: Asia 7, Europe 5, North America 5, Africa 3, South America 2, Oceania 2, plus any sets of cards you trade in (see below).
- **Attack:** from a territory with at least 2 troops into a bordering enemy territory, sending any number of troops but leaving at least 1 behind. There are no dice. The bigger side wins:
  - more attackers than defenders → you capture the territory, and your survivors (attackers − defenders) move in
  - equal → the defender is left with 1 troop
  - fewer attackers → the defender loses that many troops
- **Fortify:** move troops once between two of your territories joined by a chain of your own territories, leaving at least 1 behind.
- **Elimination:** a player who loses their last territory is out, and their turns are skipped.
- **Win:** own all 42 territories. A game with only AI players stops after 2000 turns if nobody has won, and shows the standings.

### Cards
Cards work like real Risk, except the deck is never shuffled, so nothing about them is random.
- **The deck:** 44 cards. There is one card per territory, each with a symbol (Infantry, Cavalry, or Artillery, 14 of each), plus 2 wilds. The deck is always drawn in the same, public order: the territories alphabetically from Afghanistan to Madagascar, a wild, Middle East to Yakutsk, then the other wild. Symbols go Infantry, Cavalry, Artillery in that alphabetical order (Afghanistan is Infantry, Alaska is Cavalry, Alberta is Artillery, and so on).
- **Earning:** if you captured at least one territory on your turn, you take the top card at the end of it (one card per turn at most). When the deck runs out, the traded-in cards become the new deck, in the order they were traded.
- **Sets:** three cards with the same symbol, one of each symbol, or any two cards with a wild.
- **Trading:** during your deploy phase, trade sets for extra troops. The value goes up with every set anyone trades: 4, 6, 8, 10, 12, 15, then 5 more each time. If one of the traded cards is a territory you own, 2 more troops go straight onto it (the first such card alphabetically, if there are several).
- **Forced trades:** with 5 or more cards at the start of your deploy phase, you must trade until you have 4 or fewer.
- **Taking cards:** eliminating a player gives you all their cards. If that leaves you with 6 or more, you trade down to 4 or fewer right away, place those troops, and then keep attacking.
- Everyone's cards are shown openly, since anyone could work them out from the deck order anyway.

### Terminal controls
Every prompt starts with the color of the player whose turn it is. Type territory names (any case), e.g. `eastern united states`. Type `help` to list every player's territories, troops, and cards, and press Enter on an empty line to skip or end a phase.

When you hold a set, deploy starts by showing your numbered cards and the next set's value. Type `best` to trade the best set, type three card numbers (e.g. `1 3 4`), or press Enter to skip (you can't skip if you're forced to trade).

### GUI controls
On the start screen, set the number of **Humans** and **AIs** (and **Easy AI** for random moves), then press **Start** or Space. The map colors each territory by its owner, and the bar under the instructions shows whose turn it is.

Click your territory (and the target, for attack or fortify), type a troop amount, and press **Confirm Action**. **Next Stage** / **Skip Stage** moves to the next phase. After a human's fortify phase, the turn passes to the next player. AI players move one after another, with a short pause between turns, and their moves appear in the log.

The line above the buttons shows your numbered cards, the next set's value, and how many cards everyone else holds. During deploy, press **Trade Best Set**, or type card numbers (e.g. `1 3 4`) in the box and press **Trade**. While a trade is forced, **Next Stage** stays off. After an elimination that forces a trade, the phase becomes **Card Deploy** until those troops are placed, then attacking continues.

## The AI

- **`engine.py`** (default): uses the heuristics in `scoring.py`, which weigh threat from neighboring enemy troops, held continents, choke points, and connectivity.
  - It trades its best set of cards only when forced to, since every set traded raises the value for the other players too.
  - It deploys all its troops to its most important territory that borders an enemy.
  - It keeps making the capture that most improves its board score (`minimax_attack`, looking `DEPTH` attacks ahead). For each capture it tries sending all but one troop, and sending only enough that the territory it leaves behind can't be taken next turn. The board score counts against territories an enemy could take next turn.
  - It fortifies its most important border territory from its least important connected one.
- **`random_moves.py`** (`--easy`): random but legal moves. It puts all its troops on one random border territory, keeps making random attacks it can win (stopping at random 10% of the time after each one), trades a random set only when forced, and fortifies at random.

`python simulate.py --games 200 --players 4` plays the engine against random-move players (here 3 of them) and reports the win rate. Engine wins over 60 games each (`--seed 1`):

| Players | Engine wins | By chance | Unfinished | Average turns |
|---|---|---|---|---|
| 2 | 44 | 30 | 0 | 28 |
| 3 | 29 | 20 | 2 | 146 |
| 4 | 19 | 15 | 3 | 280 |
| 6 | 11 | 10 | 1 | 396 |

## Project structure

| File | Role |
|---|---|
| `main.py` | Entry point: player choice, terminal turn loop, and command-line options |
| `gameboard.py` | `GameBoard`: troops and owners for every territory, cards (draw pile, hands, trades), battles, fortifying, move checks, deploy counts, turn order, win check; player colors and limits |
| `territory.py` | Map data: territory names, adjacency matrix, continents, bonuses, and helpers |
| `cards.py` | The card deck, symbols, set rules, set values, and the best-set choice |
| `player.py` | Terminal prompts for the human player |
| `engine.py` | Heuristic search AI |
| `scoring.py` | Board and territory scoring used by the engine |
| `random_moves.py` | Random AI |
| `interface/gui.py` | tkinter + OpenCV clickable map |
| `simulate.py` | Engine vs random-moves simulation |
| `tests/test_rules.py` | Rule tests (`python tests/test_rules.py` or `pytest`) |

The map state is two NumPy arrays: `armies` (troops per territory) and `owners` (the number of the player who owns each territory, 0 to 5). Territory `i` in both arrays is `territory.territory_names[i]`. The card state is plain lists on the board: `draw_pile`, `discard_pile`, `hands[player]`, and the `sets_traded` count. Each turn is `board.start_turn(player)`, then deploy, attack, and fortify, then `board.end_turn(player)`, which hands out the earned card. Every phase function takes the board and a player number, e.g. `engine.attack(board, 2)`. `board.owned(player)` gives a True/False mask of that player's territories.

## Not included
Dice (battles are decided by troop counts), random card draws, and more than 6 players.
