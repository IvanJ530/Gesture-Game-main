"""
Tier 2 – Processor
GameEngine: Singleton holding all authoritative game state.

Rules
─────
  Attack  vs  Attack  → both -1 HP
  Attack  vs  Defend  → blocked (no damage)
  Attack  vs  Heal    → attacker deals 1 damage; defender was mid-heal
  Defend  vs  Defend  → nothing happens
  Defend  vs  Heal    → healer gains 1 HP (defender can't stop healing)
  Heal    vs  Heal    → both +1 HP
  Unknown on either side → nothing happens, no round counted
"""


class GameEngine:
    MAX_HP = 3

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._init_state()
            cls._instance = instance
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self):
        """Restart the game from scratch."""
        self._init_state()

    def resolve(self, g1: str, g2: str) -> str:
        """
        Apply rules for one completed round.

        g1, g2 : gesture strings for player 1 and player 2.
        Returns: human-readable result message.
        Updates self.hp, self.round, self.winner.
        """
        if g1 == "Unknown" or g2 == "Unknown":
            self.last_result = "Round skipped — gesture not recognised."
            return self.last_result

        self.round += 1
        self.last_gestures = {1: g1, 2: g2}
        msg = self._apply_rules(g1, g2)
        self.last_result = msg

        # Check for game-over
        if self.hp[1] <= 0 and self.hp[2] <= 0:
            self.winner = 0          # draw
        elif self.hp[1] <= 0:
            self.winner = 2
        elif self.hp[2] <= 0:
            self.winner = 1

        return msg

    def is_game_over(self) -> bool:
        return self.winner is not None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_state(self):
        self.hp            = {1: self.MAX_HP, 2: self.MAX_HP}
        self.round         = 0
        self.winner        = None          # None | 0 (draw) | 1 | 2
        self.last_gestures = {1: None, 2: None}
        self.last_result   = ""

    def _apply_rules(self, g1: str, g2: str) -> str:
        A, D, H = "Attack", "Defend", "Heal"

        # Symmetric: build canonical pair so we only need half the branches
        pair = (g1, g2)

        if pair == (A, A):
            self._damage(1, 1)
            self._damage(2, 1)
            return "Both Attack! Both lose 1 HP."

        if pair == (A, D):
            return "P1 Attacks — P2 Defends! Blocked."

        if pair == (D, A):
            return "P2 Attacks — P1 Defends! Blocked."

        if pair == (A, H):
            self._damage(2, 1)
            return "P1 Attacks P2 mid-heal! P2 -1 HP."

        if pair == (H, A):
            self._damage(1, 1)
            return "P2 Attacks P1 mid-heal! P1 -1 HP."

        if pair == (D, D):
            return "Both Defend. Stalemate."

        if pair == (D, H):
            self._heal(2, 1)
            return "P1 Defends. P2 Heals. P2 +1 HP."

        if pair == (H, D):
            self._heal(1, 1)
            return "P2 Defends. P1 Heals. P1 +1 HP."

        if pair == (H, H):
            self._heal(1, 1)
            self._heal(2, 1)
            return "Both Heal! Both +1 HP."

        return f"Unhandled gestures: {g1} vs {g2}"

    def _damage(self, player: int, amount: int):
        self.hp[player] = max(0, self.hp[player] - amount)

    def _heal(self, player: int, amount: int):
        self.hp[player] = min(self.MAX_HP, self.hp[player] + amount)
