# Gesture Game

A two-player real-time gesture battle game controlled entirely by hand gestures from a single webcam. Each round both players simultaneously show **Fist (Attack)**, **Open Hand (Defend)**, or **Peace Sign (Heal)**. The system locks both inputs, applies battle rules, and updates HP until one player reaches 0.

---

## Setup

### 1. Create the conda environment

```bash
conda create -n AMLPROJECT python=3.10 -y
```

### 2. Install packages (use the env's pip directly — avoids conda routing to system Python)

```bash
/opt/miniconda3/envs/AMLPROJECT/bin/pip install opencv-python==4.10.0.84 mediapipe==0.10.32 numpy==1.26.4
```

> **Why not `conda activate` then `pip install`?** On macOS, `pip` inside an activated conda env can silently resolve to the system pip and install into the wrong Python. Using the full path guarantees packages land in AMLPROJECT.

### 3. Install into the system Python (required for VS Code on macOS)

VS Code defaults to `/usr/local/bin/python3` regardless of conda. Run this once:

```bash
/usr/local/bin/python3 -m pip install opencv-python==4.10.0.84 mediapipe==0.10.32 numpy==1.26.4
```

### 4. Download the MediaPipe hand landmark model

mediapipe 0.10.x requires an explicit model file. Run once to download it (~8 MB):

```bash
curl -L "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" \
     -o gesture_game/processor/hand_landmarker.task
```

> The model is also auto-downloaded on first run if the file is missing.

### 5. Run the game

**From terminal:**
```bash
conda activate AMLPROJECT
cd gesture_game
/opt/miniconda3/envs/AMLPROJECT/bin/python main.py
```

**From VS Code:** open `gesture_game/main.py` and press Run.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `opencv-python` | 4.10.0.84 | Webcam capture, frame drawing, display window |
| `mediapipe` | 0.10.32 | 21-point hand landmark detection (CPU, real-time) |
| `numpy` | 1.26.4 | Frame slicing and landmark array ops |

> **Note:** numpy is pinned below 2.0 because mediapipe 0.10.x requires it.

---

## Gestures

| Gesture | Hand shape | Action |
|---|---|---|
| Attack | Fist (all fingers curled) | Deals 1 HP damage |
| Defend | Open palm (all fingers extended) | Blocks incoming attack |
| Heal | Peace sign (index + middle up) | Restores 1 HP (capped at 3) |

## Rules

- **Attack vs Attack** → both lose 1 HP
- **Attack vs Defend** → blocked, no damage
- **Attack vs Heal** → attacker hits; healer loses 1 HP
- **Defend vs Defend** → stalemate
- **Heal vs Heal** → both gain 1 HP

## Controls

| Key | Action |
|---|---|
| `Q` | Quit |
| `R` | Restart (on game-over screen) |

---

## Git Workflow

> **Never commit directly to `main`.** Always create a new branch for your work.

### First-time clone
```bash
git clone https://github.com/IvanJ530/Gesture-Game.git
cd Gesture-Game
```

### Every time you start working — create a new branch
```bash
# Create and switch to a new branch (use a descriptive name)
git checkout -b feature/your-feature-name

# Examples:
git checkout -b feature/gesture-classifier
git checkout -b fix/camera-latency
git checkout -b ivan/stability-filter
```

### Save your changes
```bash
# 1. See what files you changed
git status

# 2. Stage the files you want to commit
git add gesture_game/processor/gesture_classifier.py   # stage one file
git add gesture_game/                                   # stage a whole folder
git add .                                               # stage everything

# 3. Commit with a clear message
git commit -m "improve gesture classifier accuracy"

# 4. Push your branch to GitHub
git push -u origin feature/your-feature-name
```

### Keep your branch up to date with main
```bash
git checkout main
git pull origin main
git checkout feature/your-feature-name
git merge main
```

### Merge into main (via Pull Request — do NOT push directly to main)
1. Push your branch: `git push -u origin feature/your-feature-name`
2. Go to the repo on GitHub → click **"Compare & pull request"**
3. Have a teammate review it, then merge

### Useful commands
```bash
git log --oneline        # see commit history
git diff                 # see unstaged changes
git branch               # list all local branches
git checkout main        # switch back to main
```

---

## Project Structure

```
gesture_game/
├── data/
│   ├── webcam_loader.py       # Singleton — owns cv2.VideoCapture
│   └── dataset_loader.py      # Optional: load HaGRID dataset for training
├── processor/
│   ├── hand_detector.py       # MediaPipe wrapper, runs per half-frame
│   ├── gesture_classifier.py  # Singleton — landmark heuristics → Attack/Defend/Heal
│   ├── stability_filter.py    # Sliding-window vote to reduce prediction flicker
│   └── game_engine.py         # Singleton — HP, rules, round state
├── ui/
│   ├── renderer.py            # All cv2 drawing (HUD, HP bars, overlays)
│   └── logger.py              # Per-round CSV log written to logs/
└── main.py                    # State machine, wires all three tiers
```
