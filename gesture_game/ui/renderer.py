"""
Tier 3 – UI
Renderer: all cv2 drawing happens here. Keeps visual logic out of game logic.

draw()          → normal in-round HUD
draw_game_over()→ end-screen overlay
"""

import cv2


class Renderer:
    # BGR colours
    C = {
        "Attack":   (0,   0,   220),   # red
        "Defend":   (0,   200,  0),    # green
        "Heal":     (0,   220, 220),   # yellow
        "Unknown":  (120, 120, 120),   # grey
        "hp_full":  (0,   200,  50),
        "hp_empty": (40,   40,  40),
        "divider":  (180, 180, 180),
        "white":    (255, 255, 255),
        "cyan":     (255, 220,   0),
        "black":    (0,     0,   0),
    }

    # HP bar geometry
    BAR_W, BAR_H, BAR_GAP = 32, 22, 6

    # ------------------------------------------------------------------
    def draw(self, frame, game_state: dict,
             p1_gesture: str, p2_gesture: str,
             countdown_val=None, phase: str = "countdown"):
        """
        Draws the in-game HUD on top of `frame` (modified in-place).

        game_state keys: hp (dict), round (int), last_result (str)
        phase           : "countdown" | "decision" | "result"
        countdown_val   : integer 1-3 displayed during countdown phase
        """
        h, w = frame.shape[:2]
        mid   = w // 2

        # Center divider
        cv2.line(frame, (mid, 0), (mid, h), self.C["divider"], 2)

        # Round counter (top-center)
        self._put(frame, f"Round {game_state['round']}",
                  (mid - 55, 28), scale=0.75)

        # Player labels
        self._put(frame, "P1", (20, 40), scale=1.2, bold=True)
        self._put(frame, "P2", (mid + 20, 40), scale=1.2, bold=True)

        # HP bars
        self._draw_hp_bar(frame, game_state["hp"][1], x=20,        y=55, label="HP")
        self._draw_hp_bar(frame, game_state["hp"][2], x=mid + 20,  y=55, label="HP")

        # Gesture labels (bottom strip)
        if p1_gesture and p1_gesture != "Unknown":
            color = self.C.get(p1_gesture, self.C["Unknown"])
            self._put(frame, p1_gesture, (20, h - 50), scale=1.0,
                      color=color, bold=True)
        if p2_gesture and p2_gesture != "Unknown":
            color = self.C.get(p2_gesture, self.C["Unknown"])
            self._put(frame, p2_gesture, (mid + 20, h - 50), scale=1.0,
                      color=color, bold=True)

        # Phase overlay
        if phase == "countdown" and countdown_val is not None:
            self._center_text(frame, str(countdown_val), scale=4.0,
                              color=self.C["white"])
        elif phase == "decision":
            self._center_text(frame, "SHOW!", scale=2.5,
                              color=self.C["cyan"])
        elif phase == "result":
            msg = game_state.get("last_result", "")
            self._center_text(frame, msg, scale=0.75,
                              color=self.C["white"], y_off=80)

        return frame

    # ------------------------------------------------------------------
    def draw_game_over(self, frame, winner: int):
        """Darken the frame and display the winner."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]),
                      self.C["black"], -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        if winner == 0:
            msg = "DRAW!"
        else:
            msg = f"Player {winner} Wins!"

        self._center_text(frame, msg, scale=2.8, color=self.C["cyan"])
        self._center_text(frame, "R = Restart    Q = Quit",
                          scale=0.7, color=self.C["white"], y_off=90)
        return frame

    # ------------------------------------------------------------------
    # Private drawing helpers
    # ------------------------------------------------------------------

    def _draw_hp_bar(self, frame, hp: int, x: int, y: int,
                     label: str = "HP", max_hp: int = 3):
        self._put(frame, label, (x, y), scale=0.55)
        for i in range(max_hp):
            bx = x + i * (self.BAR_W + self.BAR_GAP)
            by = y + 6
            color = self.C["hp_full"] if i < hp else self.C["hp_empty"]
            cv2.rectangle(frame, (bx, by),
                          (bx + self.BAR_W, by + self.BAR_H), color, -1)
            cv2.rectangle(frame, (bx, by),
                          (bx + self.BAR_W, by + self.BAR_H),
                          self.C["white"], 1)

    def _put(self, frame, text: str, pos: tuple, scale: float = 0.8,
             color=None, bold: bool = False):
        color = color or self.C["white"]
        thickness = 2 if bold else 1
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX,
                    scale, color, thickness, cv2.LINE_AA)

    def _center_text(self, frame, text: str, scale: float = 1.5,
                     color=None, y_off: int = 0):
        color = color or self.C["white"]
        h, w  = frame.shape[:2]
        font  = cv2.FONT_HERSHEY_SIMPLEX
        thick = max(1, int(scale * 2))
        (tw, th), _ = cv2.getTextSize(text, font, scale, thick)
        x = (w - tw) // 2
        y = (h + th) // 2 + y_off
        # Drop-shadow for readability
        cv2.putText(frame, text, (x + 2, y + 2), font, scale,
                    self.C["black"], thick + 1, cv2.LINE_AA)
        cv2.putText(frame, text, (x, y), font, scale, color, thick, cv2.LINE_AA)
