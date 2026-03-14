"""
Tier 1 – Data Loader
DatasetLoader: loads labeled gesture images from a directory tree
for optional offline training of a gesture classifier.

Expected directory structure:
    root/
        fist/       → Attack
        palm/       → Defend
        peace/      → Heal

Compatible with HaGRID (Kaggle) and custom in-domain recordings.
"""

import os
import cv2
import numpy as np


class DatasetLoader:
    # Maps folder names to game gesture labels
    GESTURE_MAP = {
        "fist":  "Attack",
        "palm":  "Defend",
        "peace": "Heal",
    }

    def __init__(self, root_dir: str, img_size: tuple = (64, 64)):
        """
        root_dir : path to the dataset root (contains fist/, palm/, peace/ folders)
        img_size : resize all images to this (W, H) before returning
        """
        self.root_dir = root_dir
        self.img_size = img_size

    def load_images(self) -> tuple:
        """
        Returns (X, y) where:
            X : list of BGR numpy arrays (resized)
            y : list of label strings ("Attack", "Defend", "Heal")
        """
        X, y = [], []
        for folder, label in self.GESTURE_MAP.items():
            folder_path = os.path.join(self.root_dir, folder)
            if not os.path.isdir(folder_path):
                print(f"[DatasetLoader] Warning: folder not found – {folder_path}")
                continue
            for fname in sorted(os.listdir(folder_path)):
                fpath = os.path.join(folder_path, fname)
                img = cv2.imread(fpath)
                if img is None:
                    continue
                img = cv2.resize(img, self.img_size)
                X.append(img)
                y.append(label)
        print(f"[DatasetLoader] Loaded {len(X)} images across {len(self.GESTURE_MAP)} classes.")
        return X, y

    def load_flat(self) -> tuple:
        """
        Convenience method: returns (X_flat, y) where X_flat is a 2-D array
        of flattened pixel values (n_samples, W*H*3), ready for sklearn.
        """
        X, y = self.load_images()
        X_flat = np.array([img.flatten().astype(np.float32) / 255.0 for img in X])
        return X_flat, y
