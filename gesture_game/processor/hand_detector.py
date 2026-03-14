"""
Tier 2 – Processor
HandDetector: wraps the MediaPipe Tasks Hand Landmarker API (0.10.x+).

mp.solutions was removed in mediapipe 0.10.x.
The Tasks API requires a .task model file; it is auto-downloaded on first run.
"""

import os
import ssl
import time
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

_MODEL_URL  = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")


def _ensure_model():
    if not os.path.exists(_MODEL_PATH):
        print("[HandDetector] Downloading hand_landmarker.task (~8 MB)…")
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(_MODEL_URL, context=ctx) as r:
            with open(_MODEL_PATH, "wb") as f:
                f.write(r.read())
        print("[HandDetector] Model ready.")


class HandDetector:
    def __init__(self, max_hands: int = 1,
                 detection_confidence: float = 0.65,
                 tracking_confidence: float = 0.5):
        _ensure_model()
        base_opts = mp_python.BaseOptions(model_asset_path=_MODEL_PATH)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_opts,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=tracking_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self._landmarker = mp_vision.HandLandmarker.create_from_options(options)
        self._start_time = time.time()

    def detect(self, frame) -> list:
        """
        Run hand detection on a BGR frame.
        Returns a list of landmark lists (one per detected hand).
        Each landmark list has 21 objects with .x, .y, .z (normalised 0–1).
        """
        if frame is None:
            return []
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.time() - self._start_time) * 1000)
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        if not result.hand_landmarks:
            return []
        return list(result.hand_landmarks)

    def draw_landmarks(self, frame, landmarks_list: list):
        """Draw hand skeleton on frame in-place."""
        if not landmarks_list:
            return frame
        h, w = frame.shape[:2]
        # Connections between landmark indices (MediaPipe hand topology)
        connections = [
            (0,1),(1,2),(2,3),(3,4),          # thumb
            (0,5),(5,6),(6,7),(7,8),           # index
            (5,9),(9,10),(10,11),(11,12),       # middle
            (9,13),(13,14),(14,15),(15,16),     # ring
            (13,17),(17,18),(18,19),(19,20),    # pinky
            (0,17),                             # palm base
        ]
        for lm_list in landmarks_list:
            pts = [(int(lm.x * w), int(lm.y * h)) for lm in lm_list]
            for a, b in connections:
                cv2.line(frame, pts[a], pts[b], (0, 200, 0), 2)
            for pt in pts:
                cv2.circle(frame, pt, 4, (0, 255, 0), -1)
        return frame
