# 🛡️ FarmGuard — Edge-AI Farmland Animal Detection

<!-- Badges -->
<!-- ![Build](https://img.shields.io/badge/build-passing-brightgreen) -->
<!-- ![Python](https://img.shields.io/badge/python-3.12-blue) -->
<!-- ![License](https://img.shields.io/badge/license-MIT-green) -->

> Humane, offline-first crop protection using edge AI on a laptop.

---

## Overview

FarmGuard is an edge-AI prototype that detects and classifies **27 species**
of farmland animals in real time, then triggers **humane deterrents** and
**multi-channel alerts** (audible beep, email, Telegram) to protect crops.

### Two-Model Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌──────────────────────┐
│   Camera     │───▶│  Stage 1:        │───▶│  Stage 2:            │
│   Feed       │    │  Farm Scene +    │    │  Species Classifier  │
│              │    │  Animal Detector │    │  (27 classes)        │
└─────────────┘    └──────────────────┘    └──────────────────────┘
                                                      │
                              ┌────────────────────────┘
                              ▼
                   ┌──────────────────────┐
                   │  Decision Engine     │
                   │  ┌────┐ ┌─────┐     │
                   │  │Beep│ │Email│     │
                   │  └────┘ └─────┘     │
                   │  ┌────────┐ ┌────┐  │
                   │  │Telegram│ │ DB │  │
                   │  └────────┘ └────┘  │
                   └──────────────────────┘
```

### Threat Classification

| Level | Species | Response |
|-------|---------|----------|
| 🔴 HIGH | Macaques, langurs, boar, nilgai | Full deterrent escalation |
| 🟡 MEDIUM | Peafowl, deer, hare, porcupine, cattle, squirrel, rat | Moderate deterrents |
| 🟢 LOW | Dogs, cats, horses, donkeys, camels, jackals, mongoose | Log only |
| ⚠️ DANGER | Cobra, krait, bear, leopard, elephant | Silent alert — NO deterrents |
| 🔵 SUPPRESS | Persons | Suppress all |
| ⚪ IGNORE | Vehicles | Ignore |

---

## Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd "Farmland Animal Detection"

# Install the edge package in development mode
pip install -e ./edge[dev]

# Validate configuration
farmguard validate-config --config config/farm.example.yaml

# Run with a video file (simulated mode)
farmguard run --config config/farm.example.yaml --source video.mp4 --simulate
```

---

## Project Structure

```
Farmland Animal Detection/
├── edge/                    # Python edge-AI package
│   ├── src/farmguard/       # Core modules
│   ├── tests/               # Test suite
│   └── pyproject.toml       # Package configuration
├── dashboard/               # Web dashboard (planned)
├── training/                # Model training (planned)
├── config/                  # YAML configuration files
├── models/                  # ONNX models (git-ignored)
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Saksham Gupta

