"""
Tier 1 – Data Loader
WebcamLoader: Singleton that owns the camera capture.

Uses ffmpeg piped to a background thread so the main loop always gets
the LATEST frame with no latency, and the FaceTime HD Camera is selected
by name (not by index) so the iPhone Continuity Camera is never used.
"""

import sys
import re
import subprocess
import threading
import numpy as np


def _av_index_by_name(name: str) -> str:
    """Return the AVFoundation index string for the named device."""
    result = subprocess.run(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True, text=True, timeout=5
    )
    for line in result.stderr.splitlines():
        m = re.search(r'\[(\d+)\]\s+(.+)', line)
        if m and name.lower() in m.group(2).lower():
            return m.group(1)
    raise RuntimeError(f"Camera '{name}' not found in AVFoundation device list.")


class WebcamLoader:
    _instance = None

    CAMERA_NAME = "FaceTime HD Camera"   # ← change here if needed
    WIDTH       = 1280
    HEIGHT      = 720
    FPS         = 30

    def __new__(cls):
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._latest_frame = None
            instance._lock         = threading.Lock()
            instance._running      = True

            av_idx = _av_index_by_name(cls.CAMERA_NAME)
            print(f"[WebcamLoader] '{cls.CAMERA_NAME}' → AVFoundation index {av_idx}")

            frame_bytes = cls.WIDTH * cls.HEIGHT * 3
            proc = subprocess.Popen([
                "ffmpeg",
                "-fflags", "nobuffer",          # disable input buffering
                "-flags",  "low_delay",          # minimise decoder delay
                "-f",      "avfoundation",
                "-framerate", str(cls.FPS),
                "-video_size", f"{cls.WIDTH}x{cls.HEIGHT}",
                "-i",      av_idx,
                "-vf",     f"scale={cls.WIDTH}:{cls.HEIGHT}",
                "-pix_fmt","bgr24",
                "-f",      "rawvideo",
                "-"
            ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

            instance._proc = proc

            # Background thread: continuously reads frames from ffmpeg pipe
            # and keeps only the latest one → zero queue latency for caller
            def _reader():
                while instance._running:
                    raw = proc.stdout.read(frame_bytes)
                    if len(raw) < frame_bytes:
                        break
                    frame = np.frombuffer(raw, dtype=np.uint8).reshape(
                        (cls.HEIGHT, cls.WIDTH, 3)).copy()
                    with instance._lock:
                        instance._latest_frame = frame

            t = threading.Thread(target=_reader, daemon=True)
            t.start()
            instance._thread = t

            # Wait until first frame arrives
            print("[WebcamLoader] Waiting for first frame…")
            import time
            for _ in range(100):
                with instance._lock:
                    if instance._latest_frame is not None:
                        break
                time.sleep(0.05)
            print("[WebcamLoader] Camera ready.")

            cls._instance = instance
        return cls._instance

    def get_frame(self):
        """Returns the latest captured frame (BGR numpy array)."""
        with self._lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None

    def release(self):
        self._running = False
        self._proc.terminate()
        WebcamLoader._instance = None
