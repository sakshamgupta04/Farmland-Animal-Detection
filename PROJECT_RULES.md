# FarmGuard — Project Rules

> **FarmGuard** is an edge-AI crop-protection prototype running on a **laptop**.
> It uses two models to detect and classify farmland animals, then triggers
> humane deterrents and multi-channel alerts to protect crops.

---

## 1. System Overview

### Two-Model Architecture

| Stage | Model | Purpose |
|-------|-------|---------|
| **Stage 1** | Farm Scene Classifier + Animal Detector | Confirm farmland scene; detect & locate animals |
| **Stage 2** | Species Classifier (27 classes) | Identify species with scientific names |

### Pipeline

```
camera → motion gate → farm scene check → stage-1 detector →
tracker + zone filter → stage-2 species classifier → temporal voting →
decision engine → alerts (beep + email + telegram + visual) + SQLite →
cloud sync → dashboard
```

### Three Alert Channels

1. **Audible beep** — graduated frequency patterns via system speaker
2. **Email (SMTP)** — with thumbnails, supports English and Hindi
3. **Telegram** — instant mobile alerts with rate limiting

---

## 2. Species Taxonomy

27 species with threat classification:

| Threat Level | Description | Action |
|-------------|-------------|--------|
| **HIGH** | Major crop raiders (macaques, boar, nilgai, langur) | Full deterrent escalation |
| **MEDIUM** | Moderate damage (peafowl, deer, hare, porcupine, cattle, squirrel, rat) | Moderate deterrents |
| **LOW** | Minimal damage (dogs, cats, horses, donkeys, camels, jackals, mongoose) | Log only |
| **DANGER** | Dangerous wildlife (cobra, krait, bear, leopard, elephant) | **Silent alert only — NO deterrents** |
| **SUPPRESS** | Persons | Suppress all actions |
| **IGNORE** | Vehicles | Ignore completely |

---

## 3. Hard Rules

### 3.1 Humane-Only Deterrents

- **NEVER** use harmful, injurious, or lethal methods.
- All deterrents are auditory or visual only.
- Volume is capped (`volume_cap` in config, default 0.7).
- Maximum deterrent duration: 5 seconds per activation.
- Minimum interval between activations: 15 seconds.
- Global kill switch in config (`deterrent.kill_switch`).

### 3.2 Dangerous Animal Safety

- **NEVER** activate deterrents for DANGER-level animals.
- Startling a cobra, bear, leopard, or elephant is **life-threatening**.
- DANGER detections trigger **silent alerts only** (email + telegram).
- Alert message must include: "DANGER — Do not approach."

### 3.3 Person/Privacy

- SUPPRESS all actions when a person is detected.
- **NEVER** store, transmit, or process facial features.
- Person thumbnails must be blurred before any storage or transmission.
- No audio recording of human speech.

### 3.4 Offline-First

- The system must work fully offline (no cloud dependency for core pipeline).
- Cloud sync and dashboard are optional enhancements.
- All models run locally via ONNX Runtime.
- SQLite for local event storage.

### 3.5 Honest Evaluation

- Report real metrics — no inflated numbers.
- Log all false positives and false negatives.
- Unknown detections must be labeled as `unknown_animal`, never forced into a class.
- Confidence thresholds must be respected; low-confidence results are uncertain.

---

## 4. Repository Layout

```
Farmland Animal Detection/
├── edge/                    # Python edge-AI package
│   ├── src/farmguard/       # Main package source
│   ├── tests/               # Unit and integration tests
│   └── pyproject.toml       # Package config
├── dashboard/               # Web dashboard (future)
├── training/                # Model training scripts (future)
├── scenarios/               # Test scenarios and fixtures
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── assets/sounds/           # Deterrent sound files
├── config/                  # Configuration files
├── models/                  # ONNX model files (git-ignored)
├── PROJECT_RULES.md
├── README.md
├── LICENSE
└── .gitignore
```

---

## 5. Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Numerics | numpy |
| Vision | opencv-python-headless |
| Inference | onnxruntime |
| Config | pydantic v2, pyyaml |
| HTTP | httpx |
| API/Dashboard | fastapi, uvicorn |
| System | psutil |
| Storage | sqlite3 (stdlib) |
| Testing | pytest, pytest-cov |
| Linting | ruff |

---

## 6. Code Standards

- **Python 3.12** — use modern type hints (`str | None`, not `Optional[str]`).
- **PEP 8** — enforced by ruff.
- **Type hints everywhere** — all function signatures, all class attributes.
- **Pydantic v2** for configuration; **dataclasses** for data objects.
- **Abstract base classes** for all interfaces.
- **Docstrings** on all public classes and methods.
- **Modules under 250 lines** — split if needed.
- **`from __future__ import annotations`** where needed for forward refs.
- **Never commit**: models (*.onnx, *.pt), videos, secrets, .env files.

