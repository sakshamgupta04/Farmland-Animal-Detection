# 🌾 FarmGuard — End-to-End Master Plan

> AI-Powered Farmland Animal Detection, Classification & Alert System

---

## Executive Summary

FarmGuard is a **two-model AI system** that:
1. **Model 1 — Farm Scene Detector**: Detects whether the camera is looking at farmland and identifies animals within it (bounding boxes).
2. **Model 2 — Species Classifier**: Takes each detected animal crop and classifies it to the **real species name** (e.g., *Macaca mulatta* — Rhesus Macaque, *Sus scrofa* — Wild Boar).
3. **Threat Engine**: Cross-references the identified species against a **crop-threat database** to decide if the animal is harmful.
4. **Alert System**: Triggers **audible beeps** (laptop speakers) and **email/Telegram notifications** to the farmer.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        📹 INPUT LAYER                                   │
│  Camera Source (Webcam / Video File / IP Camera)                        │
│  → FPS Limiter → Frame Quality Check                                    │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   🔍 MODEL 1: FARM + ANIMAL DETECTOR                    │
│                                                                         │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────────────┐  │
│  │ Motion Gate   │──▶│ Farm Scene       │──▶│ Animal Detector        │  │
│  │ (BG Subtract) │   │ Classifier       │   │ (YOLOv8-nano ONNX)    │  │
│  │               │   │ (MobileNetV3)    │   │ → animal/person/vehicle│  │
│  └──────────────┘   └──────────────────┘   └──────────┬─────────────┘  │
│                                                        │                │
│                                          ┌─────────────▼─────────────┐ │
│                                          │ IoU Tracker + Zone Filter │ │
│                                          └─────────────┬─────────────┘ │
└────────────────────────────────────────────────────────┬────────────────┘
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   🏷️ MODEL 2: SPECIES CLASSIFIER                       │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │ Best Crop Select  │─▶│ Species Classify  │─▶│ Temporal Voting     │  │
│  │ (Sharpest/Largest)│  │ (EfficientNet-   │  │ (N of M frames)     │  │
│  │                   │  │  Lite ONNX)      │  │                      │  │
│  └──────────────────┘  └──────────────────┘  └──────────┬───────────┘  │
│                                                          │              │
│                                            ┌─────────────▼───────────┐ │
│                                            │ Taxonomy Mapper         │ │
│                                            │ Common → Scientific Name│ │
│                                            └─────────────┬───────────┘ │
└──────────────────────────────────────────────────────────┬──────────────┘
                                                           │
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        🧠 DECISION ENGINE                               │
│                                                                         │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────────────┐  │
│  │ Threat DB    │──▶│ State Machine     │──▶│ Rules Engine           │  │
│  │ Lookup       │   │ IDLE→WATCHING→    │   │ Quiet Hrs / Person     │  │
│  │              │   │ CONFIRMED→DETER   │   │ Suppression / Escalate │  │
│  └──────────────┘   └──────────────────┘   └──────────┬─────────────┘  │
└────────────────────────────────────────────────────────┬────────────────┘
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        🔔 ALERT SYSTEM (3 Channels)                     │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ 🔊 Audible   │  │ 📧 Email     │  │ 📱 Telegram  │  │ 💡 Visual  │ │
│  │ Beep         │  │ SMTP/SendGrid│  │ Bot API      │  │ Screen     │ │
│  │ (Speakers)   │  │              │  │              │  │ Flash      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└────────────────────────────────────────────────────────┬────────────────┘
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     💾 STORAGE & DASHBOARD                              │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ SQLite       │─▶│ Cloud Sync   │─▶│ Dashboard    │  │ Live       │ │
│  │ Event Store  │  │ (Supabase)   │  │ (Next.js)    │  │ Monitor    │ │
│  │ (Offline)    │  │              │  │              │  │ (FastAPI)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 The Two Core Models

### Model 1: Farm Scene Detector + Animal Locator

| Component | Detail |
|---|---|
| **Farm Scene Classifier** | MobileNetV3-Small (2.5M params), checks every 30s if camera sees farmland |
| **Animal Detector** | YOLOv8-nano (3.2M params) or MegaDetector v5, finds bounding boxes |
| **Output** | Bounding boxes labeled: `animal`, `person`, `vehicle` |
| **Speed** | 15-30 FPS on CPU laptop |
| **Format** | ONNX (FP32 primary, INT8 optional) |

### Model 2: Species Classifier (The Real Name Giver)

| Component | Detail |
|---|---|
| **Architecture** | EfficientNet-Lite0 (4.7M params) |
| **Input** | 224×224 cropped animal region |
| **Output** | 27 species classes with scientific + common + Hindi names |
| **Confidence** | Temperature-scaled; below 0.6 → "Unknown Animal" |
| **Training Data** | iNaturalist, camera-trap datasets, custom Indian farm photos |

---

## 📋 Full Species Taxonomy & Threat Classification (27 Species)

### 🔴 HIGH Threat — Active Crop Raiders (Deterrent: Sound + Visual)

| # | Common Name | Scientific Name | Hindi | Crops Damaged |
|---|---|---|---|---|
| 1 | Rhesus Macaque | *Macaca mulatta* | रीसस बंदर | Fruits, vegetables, grains |
| 2 | Hanuman Langur | *Semnopithecus entellus* | हनुमान लंगूर | Fruits, leaves |
| 3 | Wild Boar | *Sus scrofa* | जंगली सूअर | Root crops, sugarcane, paddy |
| 4 | Nilgai (Blue Bull) | *Boselaphus tragocamelus* | नीलगाय | Wheat, mustard, vegetables |

### 🟡 MEDIUM Threat — Moderate Crop Damage (Deterrent: Sound only)

| # | Common Name | Scientific Name | Hindi | Crops Damaged |
|---|---|---|---|---|
| 5 | Indian Peafowl | *Pavo cristatus* | मोर | Grains, seeds |
| 6 | Spotted Deer | *Axis axis* | चीतल | Young shoots, crops |
| 7 | Sambar Deer | *Rusa unicolor* | सांभर | Crops, bark |
| 8 | Indian Hare | *Lepus nigricollis* | खरगोश | Vegetables, pulses |
| 9 | Indian Porcupine | *Hystrix indica* | साही | Root crops, tubers |
| 10 | Stray Cattle | *Bos taurus* (stray) | आवारा गाय | Grazes crops |
| 11 | Palm Squirrel | *Funambulus palmarum* | गिलहरी | Fruits, nuts |
| 12 | Field Rat | *Rattus spp.* | चूहा | Stored grain, field crops |

### 🟢 LOW Threat — Minimal/No Crop Damage (Log only)

| # | Common Name | Scientific Name | Hindi | Notes |
|---|---|---|---|---|
| 13 | Stray Dog | *Canis lupus familiaris* | कुत्ता | Rarely damages crops |
| 14 | Domestic Cat | *Felis catus* | बिल्ली | No crop damage |
| 15 | Domestic Horse | *Equus caballus* | घोड़ा | May graze if stray |
| 16 | Domestic Donkey | *Equus asinus* | गधा | May graze if stray |
| 17 | Camel | *Camelus dromedarius* | ऊँट | May browse trees |
| 18 | Indian Jackal | *Canis aureus* | सियार | Rarely damages crops |
| 19 | Mongoose | *Herpestes edwardsii* | नेवला | **Beneficial** — pest control! |

### ⚠️ DANGER — Dangerous Animals (ALERT ONLY — NO Deterrent!)

| # | Common Name | Scientific Name | Hindi | Why Dangerous |
|---|---|---|---|---|
| 20 | Indian Cobra | *Naja naja* | नाग | Venomous — snakebite risk |
| 21 | Common Krait | *Bungarus caeruleus* | करैत | Venomous — snakebite risk |
| 22 | Sloth Bear | *Melursus ursinus* | भालू | Can attack when provoked |
| 23 | Indian Leopard | *Panthera pardus fusca* | तेंदुआ | Apex predator — avoid contact |
| 24 | Indian Elephant | *Elephas maximus* | हाथी | Can cause fatalities if agitated |

### 🚫 Special Classes

| # | Common Name | Behavior |
|---|---|---|
| 25 | Person | SUPPRESS all deterrents when present |
| 26 | Vehicle | IGNORE completely |
| 27 | Unknown Animal | Alert only, no deterrent |

---

## 🔔 Alert System — 3 Channels

### Channel 1: Audible Beep (Laptop Speakers)

```
Escalation Patterns:
  Level 1 → Visual flash only              (0 seconds)
  Level 2 → 3 short beeps (800Hz, 200ms)   (after 10s)
  Level 3 → 2 long beeps (1000Hz, 500ms)   (after 30s)
  Level 4 → Rapid fire (1200Hz × 10)       (after 60s)
  Level 5 → Continuous + urgent notify      (after 90s)

Safety:
  • Volume cap: 70% max (applied to WAV data, not OS volume)
  • Demo volume: 30%
  • Max duration: 5 seconds per burst
  • Min interval: 15 seconds between bursts
  • Mute button + kill switch always available
  • No sound device? → continues with visual + notifications
```

### Channel 2: Email Alert (SMTP / SendGrid)

```
Triggers when:
  • HIGH threat animal confirmed → immediate email
  • DANGER animal detected → URGENT email (different template)
  • MEDIUM threat animal → email after 5-minute cooldown
  • LOW threat → no email (log only)

Template includes:
  • Species name (common + scientific + Hindi)
  • Threat level with color badge
  • Timestamp and zone location
  • Confidence percentage
  • Thumbnail attachment (if available)
  • Actions taken by the system
  • Known crop damage types for this species
  • "Mute for 1 hour" link
```

### Channel 3: Telegram Bot

```
Same trigger rules as email
Sends: text message + thumbnail photo
Rate limited: max 5 messages per minute
Offline? → queues and sends when internet returns
Templates in English and Hindi
```

---

## 🧠 Decision Engine — State Machine

```
                    ┌─────────────────────────────────────────┐
                    │           PERSON DETECTED?               │
                    │    YES → SUPPRESS ALL DETERRENTS         │
                    │           (keep tracking, keep alerting) │
                    └─────────────────────────────────────────┘

  ┌──────┐   Motion    ┌──────────┐  Animal    ┌───────────┐
  │ IDLE │───detected──▶│ WATCHING │──detected─▶│ CONFIRMED │
  └──┬───┘             └────┬─────┘            └─────┬─────┘
     │                      │                        │
     │◀──no motion──────────┘    Threat confirmed    │
     │                        (N/M vote passed)      │
     │                                               ▼
     │                                     ┌───────────────┐
     │                                     │  DETERRING    │
     │                                     │  Level 1→2→3  │
     │                                     └───────┬───────┘
     │                                             │
     │                          ┌──────────────────┤
     │                          │                  │
     │                          ▼                  ▼
     │                 ┌──────────────┐   ┌──────────────┐
     │                 │ ESCALATING   │   │  COOLDOWN    │
     │                 │ Level 4→5    │   │  (5 min)     │
     │                 └──────────────┘   └──────┬───────┘
     │                                           │
     │◀──────────────────────────────────────────┘

  DANGEROUS ANIMAL? → Skip to ALERT ONLY (no deterrents ever)
  STORM CONTROL: >10 triggers in 30 min → QUIET mode for 15 min
```

---

## 📅 14-Phase Build Plan with Timeline

| Phase | Content | Time | Milestone |
|---|---|---|---|
| **0** | Project setup, rules, .gitignore | Day 1 | — |
| **1** | Monorepo skeleton, config, interfaces, taxonomy | Days 2-4 | — |
| **2** | Camera sources + motion gate | Days 5-7 | — |
| **3** | **Model 1: Farm classifier + animal detector** | Days 8-14 | — |
| **4** | **Model 2: Species classifier (real names)** | Days 15-21 | — |
| **5** | Tracker, zones, voting, decision engine | Days 22-28 | — |
| **6** | **Alert system (beep + email + telegram)** | Days 29-35 | — |
| **7** | Event store + live monitor | Days 36-42 | **v0.1** |
| **8** | Cloud dashboard (Supabase + Next.js) | Days 43-52 | — |
| **9** | Cloud sync + device pairing | Days 53-63 | **v0.3** |
| **10** | Training pipeline + model training | Days 64-77 | — |
| **11** | Evaluation + soak testing | Days 78-84 | **v0.5** |
| **12** | Demo packaging + scenarios | Days 85-91 | **v0.8** |
| **13** | Hardening + documentation + release | Days 92-98 | **v1.0** |
| **14** | _(Optional)_ Browser playground | +1-2 weeks | — |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Edge Runtime | Python 3.12, OpenCV, ONNX Runtime (CPU) |
| Models | YOLOv8-nano, MobileNetV3, EfficientNet-Lite |
| Training | PyTorch, timm, albumentations (Colab/Kaggle) |
| Config | Pydantic v2 + YAML |
| Local Storage | SQLite (WAL mode) |
| Live Monitor | FastAPI + vanilla JS |
| Dashboard | Next.js + TypeScript + Tailwind |
| Database | Supabase (PostgreSQL) |
| Alerts | winsound + SMTP + Telegram Bot API |
| Deployment | Vercel (free) + local laptop |
| Linting | Ruff + ESLint + TypeScript |
| Testing | pytest + vitest |

---

## 🚨 Hard Rules (Non-Negotiable)

1. **HUMANE ONLY** — Sound and light deterrents only. Never harm animals.
2. **DANGEROUS ANIMAL PROTOCOL** — NO deterrents for snakes, bears, leopards, elephants. Alert-only.
3. **PERSON SUPPRESSION** — When a person is detected, ALL deterrents are suppressed.
4. **PRIVACY** — No face identification, no person images stored/uploaded.
5. **OFFLINE-FIRST** — Detection and deterrents work without internet. Always.
6. **HONEST EVALUATION** — Never fabricate numbers. "Not measured" is acceptable.
7. **NO FIELD CLAIMS** — Never claim field-tested, crop damage reduced, or deterrent success.
8. **VOLUME SAFETY** — Audio data is pre-scaled; OS volume doesn't override caps.
9. **SECRETS** — Environment variables only; never log tokens or keys.
10. **MODELS OUT OF GIT** — .onnx, .pt, .pth files are never committed.

---

## 📂 Project Structure

```
Farmland Animal Detection/
├── docs/
│   ├── MASTER_PLAN.md          ← You are here
│   ├── MODELS.md               ← How to get/train each model
│   ├── EVALUATION.md           ← Testing protocol
│   ├── DEMO.md                 ← Demo script and shot list
│   ├── DESIGN.md               ← Architecture decisions
│   ├── PRIVACY.md              ← Privacy policy
│   └── FUTURE_HARDWARE.md      ← Raspberry Pi port guide
├── edge/
│   ├── pyproject.toml
│   └── src/farmguard/
│       ├── __init__.py
│       ├── cli.py              ← Command-line interface
│       ├── config.py           ← Pydantic config + YAML loader
│       ├── interfaces.py       ← Abstract Camera, Detector, etc.
│       ├── taxonomy.py         ← 27-species database
│       ├── threat_db.py        ← Threat classification engine
│       ├── camera.py           ← Webcam, video, IP camera
│       ├── motion.py           ← Motion gate (BG subtraction)
│       ├── farm_classifier.py  ← Model 1a: farm scene check
│       ├── detector.py         ← Model 1b: YOLO animal detector
│       ├── classifier.py       ← Model 2: species classifier
│       ├── tracker.py          ← IoU multi-object tracker
│       ├── zones.py            ← Protected zone polygons
│       ├── voting.py           ← Temporal voting (N of M)
│       ├── decision.py         ← State machine + escalation
│       ├── events.py           ← Event lifecycle
│       ├── store.py            ← SQLite event store
│       ├── alerts/
│       │   ├── beep.py         ← Audible beep (winsound)
│       │   ├── email_alert.py  ← Email (SMTP/SendGrid)
│       │   ├── telegram.py     ← Telegram Bot API
│       │   ├── visual.py       ← Screen flash
│       │   └── alert_manager.py← Orchestrates all channels
│       └── monitor/
│           ├── server.py       ← FastAPI live monitor
│           └── static/         ← HTML/CSS/JS for monitor UI
├── dashboard/                  ← Next.js cloud dashboard
├── training/                   ← Training scripts + notebooks
├── config/
│   └── farm.example.yaml       ← Example config (all species)
├── models/
│   └── manifest.yaml           ← Model metadata (models git-ignored)
├── scripts/
│   ├── verify.py               ← Lint + test runner
│   ├── setup.ps1               ← Windows setup
│   └── setup.sh                ← Linux/Mac setup
├── assets/sounds/              ← Beep WAVs + SOURCES.md
├── scenarios/                  ← Demo scenario YAML files
├── PROJECT_RULES.md
├── README.md
├── LICENSE
└── .gitignore
```

---

## ✅ Immediate Next Steps

Phase 0+1 is being built right now:
- Project skeleton with all config files
- Species taxonomy with all 27 species
- Threat database with classification engine
- Abstract interfaces + simulation implementations
- CLI entry point
- Tests for everything above

**After that, we build Model 1 (farm + animal detector) and Model 2 (species classifier).**

---

*Plan created: 10 Nov 2026 | Author: Saksham Gupta | Built with Antigravity*

