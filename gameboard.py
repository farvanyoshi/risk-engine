import numpy as np
import numpy.typing as npt
import cards
import territory

MIN_PLAYERS = 2
MAX_PLAYERS = 6

# Each player is known by a number from 0 up, and shown with one of these colors
PLAYER_COLORS: list[str] = ["Green", "Red", "Blue", "Yellow", "Purple", "Orange"]

# Games with only AI players stop after this many turns in case the AIs can't finish each other off
AI_ONLY_TURN_LIMIT = 2000

# Returns why a mix of human and AI players can't be used, or None if it can
def check_player_counts(humans: int, ais: int) -> str | None:
    if humans < 0 or ais < 0:
        return "The number of players can't be negative."
    if not MIN_PLAYERS <= humans + ais <= MAX_PLAYERS:
        return f"The game needs between {MIN_PLAYERS} and {MAX_PLAYERS} players in total."
    return None

# Humans take the first seats, then the AIs
def player_name(player: int, humans: int) -> str:
    return f"{PLAYER_COLORS[player]} ({'human' if player < humans else 'AI'})"

# Starting troops: every territory gets 1, 2, or 3 troops
INIT_ARMIES: npt.NDArray[np.integer] = np.array([1, 2, 3] * 14)

# Contains the common game code to all players
# owners[i] is the number of the player who owns territory i
class GameBoard:
    def __init__(self, num_players: int = 2, armies: npt.NDArray[np.integer] | None = None, owners: npt.NDArray[np.integer] | None = None) -> None:
        if not MIN_PLAYERS <= num_players <= MAX_PLAYERS:
            raise ValueError(f"The game needs between {MIN_PLAYERS} and {MAX_PLAYERS} players")
        self.num_players: int = num_players

        # every new game gets its own shuffled copy, and territories are split as evenly as possible
        self.armies: npt.NDArray[np.integer] = np.random.permutation(INIT_ARMIES) if armies is None else armies
        self.owners: npt.NDArray[np.integer] = np.random.permutation(np.arange(42) % num_players) if owners is None else owners

        # cards: the draw pile is always in the same order, and traded cards are reused in the order they were traded
        self.draw_pile: list[int] = list(cards.DECK_ORDER)
        self.discard_pile: list[int] = []
        self.hands: list[list[int]] = [[] for _ in range(num_players)]
        self.sets_traded: int = 0
        self.captured_this_turn: bool = False

    def copy(self):
        board = GameBoard(self.num_players, self.armies.copy(), self.owners.copy())
        board.draw_pile = self.draw_pile.copy()
        board.discard_pile = self.discard_pile.copy()
        board.hands = [hand.copy() for hand in self.hands]
        board.sets_traded = self.sets_traded
        board.captured_this_turn = self.captured_this_turn
        return board

    def owned(self, player: int) -> npt.NDArray[np.bool]:
        return self.owners == player

    def is_alive(self, player: int) -> bool:
        return bool(np.any(self.owners == player))

    def alive_players(self) -> list[int]:
        return [player for player in range(self.num_players) if self.is_alive(player)]

    # The next player still in the game after this one, wrapping around
    def next_player(self, player: int) -> int:
        for step in range(1, self.num_players + 1):
            candidate = (player + step) % self.num_players
            if self.is_alive(candidate):
                return candidate
        return player

    # The number of the player who owns every territory, or None if the game is still going
    def winner(self) -> int | None:
        if np.all(self.owners == self.owners[0]):
            return int(self.owners[0])
        return None

    def is_won(self) -> bool:
        return self.winner() is not None

    # (player, territories, troops) for every player still in the game, most territories first
    def standings(self) -> list[tuple[int, int, int]]:
        rows = [(player, int(np.count_nonzero(self.owned(player))), int(self.armies[self.owned(player)].sum())) for player in self.alive_players()]
        return sorted(rows, key = lambda row: (row[1], row[2]), reverse = True)

    # Troops given at the start of a turn: owned territories // 3 (minimum 3) plus continent bonuses
    def deploy_count(self, player: int) -> int:
        owned = self.owned(player)
        return max(int(np.count_nonzero(owned)) // 3, 3) + territory.continent_bonus(owned)

    def can_attack(self, player: int, start: int, end: int, attacking_troops: int) -> bool:
        owned = self.owned(player)
        return bool(
            owned[start] and not owned[end]
            and territory.adjMatrix[start][end]
            and 1 <= attacking_troops <= self.armies[start] - 1
        )

    def can_fortify(self, player: int, start: int, end: int, transferring_troops: int) -> bool:
        owned = self.owned(player)
        return bool(
            owned[start] and start != end
            and territory.total_connections(start, owned)[end]
            and 1 <= transferring_troops <= self.armies[start] - 1
        )

    # Deterministic battle: the bigger side wins and keeps the difference
    def battle(self, start: int, end: int, attacking_troops: int) -> None:
        self.armies[start] -= attacking_troops
        if attacking_troops > self.armies[end]:
            defender = int(self.owners[end])
            self.armies[end] = attacking_troops - self.armies[end]
            self.owners[end] = self.owners[start]
            self.captured_this_turn = True

            # eliminating a player hands their cards to the attacker
            if not self.is_alive(defender):
                self.hands[self.owners[start]] += self.hands[defender]
                self.hands[defender] = []
        elif attacking_troops == self.armies[end]:
            self.armies[end] = 1
        else:
            self.armies[end] -= attacking_troops

    def fortify(self, start: int, end: int, transferring_troops: int) -> None:
        self.armies[start] -= transferring_troops
        self.armies[end] += transferring_troops

    def start_turn(self, player: int) -> None:
        self.captured_this_turn = False

    # A player who captured a territory this turn takes the top card. Returns the card, or None
    def end_turn(self, player: int) -> int | None:
        if not self.captured_this_turn:
            return None
        self.captured_this_turn = False

        # when the draw pile runs out, traded cards are reused in the order they were traded
        if not self.draw_pile:
            self.draw_pile, self.discard_pile = self.discard_pile, []
        if not self.draw_pile:
            return None

        card = self.draw_pile.pop(0)
        self.hands[player].append(card)
        return card

    def must_trade(self, player: int, hand_size: int = cards.MUST_TRADE_HAND) -> bool:
        return len(self.hands[player]) >= hand_size

    # Trades a set of cards. Returns the troops to deploy and the territory that got the +2 bonus (or None)
    def trade(self, player: int, traded: list[int]) -> tuple[int, int | None]:
        if not cards.is_valid_set(traded) or not all(card in self.hands[player] for card in traded):
            raise ValueError("That is not a set of cards in your hand")

        for card in traded:
            self.hands[player].remove(card)
        self.discard_pile += traded

        troops = cards.set_value(self.sets_traded)
        self.sets_traded += 1

        bonus = cards.bonus_territory(traded, self.owned(player))
        if bonus is not None:
            self.armies[bonus] += cards.TERRITORY_BONUS
        return troops, bonus
