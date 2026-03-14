"""
Tier 2 – Processor
GestureClassifier: Singleton that maps 21 MediaPipe hand landmarks
to one of three game gestures using finger-extension heuristics.

Landmark indices (MediaPipe Hands):
    Wrist      = 0
    Thumb      = 1-4   (tip = 4)
    Index      = 5-8   (tip = 8,  pip = 6)
    Middle     = 9-12  (tip = 12, pip = 10)
    Ring       = 13-16 (tip = 16, pip = 14)
    Pinky      = 17-20 (tip = 20, pip = 18)

Rules:
    Attack (Fist)   : all four fingers curled (tips below PIPs in image coords)
    Defend (Palm)   : all four fingers extended
    Heal   (Peace)  : index + middle extended, ring + pinky curled
"""


class GestureClassifier:
    ATTACK  = "Attack"
    DEFEND  = "Defend"
    HEAL    = "Heal"
    UNKNOWN = "Unknown"

    # (tip_index, pip_index) for the four fingers (excluding thumb)
    _FINGER_JOINTS = [(8, 6), (12, 10), (16, 14), (20, 18)]

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def predict(self, landmarks) -> str:
        """
        landmarks : list of 21 mediapipe NormalizedLandmark objects, or None.
        Returns   : one of ATTACK / DEFEND / HEAL / UNKNOWN.
        """
        if not landmarks or len(landmarks) < 21:
            return self.UNKNOWN

        fingers_up = self._fingers_extended(landmarks)
        n_up = sum(fingers_up)
        idx_up, mid_up, ring_up, pinky_up = fingers_up

        if n_up == 0:
            return self.ATTACK                          # Fist
        if n_up >= 4:
            return self.DEFEND                          # Open palm
        if idx_up and mid_up and not ring_up and not pinky_up:
            return self.HEAL                            # Peace / two fingers
        return self.UNKNOWN

    # ------------------------------------------------------------------
    def _fingers_extended(self, lm) -> list:
        """
        Returns [bool, bool, bool, bool] for index/middle/ring/pinky.
        A finger is 'up' when its tip is above (smaller y) its PIP joint.
        Image y increases downward, so tip.y < pip.y means extended.
        """
        return [lm[tip].y < lm[pip].y for tip, pip in self._FINGER_JOINTS]
