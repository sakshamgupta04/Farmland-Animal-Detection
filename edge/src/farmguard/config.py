"""Pydantic v2 configuration models for FarmGuard.

Provides typed, validated configuration with YAML loading support.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class CameraConfig(BaseModel):
    """Camera / video source settings."""

    source: str = "0"
    width: int = 1280
    height: int = 720
    fps_limit: float = 15.0
    reconnect_interval: float = 5.0
    quality_check_enabled: bool = True


class ZoneConfig(BaseModel):
    """Protected and ignored zone polygons."""

    protected: list[list[float]] = Field(default_factory=list)
    ignore: list[list[list[float]]] = Field(default_factory=list)


class DetectorConfig(BaseModel):
    """Stage-1 animal detector settings."""

    model_path: str = "models/detector.onnx"
    input_size: int = 640
    confidence_threshold: float = 0.4
    nms_threshold: float = 0.5
    thread_count: int = 2


class ClassifierConfig(BaseModel):
    """Stage-2 species classifier settings."""

    model_path: str = "models/species_classifier.onnx"
    input_size: int = 224
    confidence_threshold: float = 0.6
    unknown_threshold: float = 0.6
    labels_file: str = "models/species_labels.txt"
    temperature: float = 1.0


class FarmClassifierConfig(BaseModel):
    """Farm scene classifier settings."""

    model_path: str = "models/farm_classifier.onnx"
    input_size: int = 224
    confidence_threshold: float = 0.7
    check_interval_seconds: float = 30.0
    enabled: bool = True


class VotingConfig(BaseModel):
    """Temporal voting: require N detections in M frames."""

    n: int = 3
    m: int = 5


class TrackerConfig(BaseModel):
    """Object tracker settings."""

    max_age: int = 30
    min_hits: int = 3
    iou_threshold: float = 0.3


class DeterrentConfig(BaseModel):
    """Global deterrent limits and kill switch."""

    volume_cap: float = 0.7
    demo_volume: float = 0.3
    max_duration_seconds: float = 5.0
    min_interval_seconds: float = 15.0
    mute: bool = False
    kill_switch: bool = False


class BeepConfig(BaseModel):
    """Audible beep alert patterns: list of ``(frequency_hz, duration_ms)``."""

    enabled: bool = True
    patterns: dict[str, list[tuple[int, int]]] = Field(
        default_factory=lambda: {
            "attention": [(800, 200), (0, 100), (800, 200), (0, 100), (800, 200)],
            "warning": [(1000, 500), (0, 200), (1000, 500)],
            "urgent": [(1200, 100), (0, 50)] * 5,
            "danger_alert": [(600, 1000)],
        }
    )


class EmailConfig(BaseModel):
    """SMTP email alert settings (credentials via env vars)."""

    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    use_tls: bool = True
    from_address: str = ""
    to_addresses: list[str] = Field(default_factory=list)
    alert_cooldown_seconds: int = 300
    include_thumbnail: bool = True
    language: str = "en"


class TelegramConfig(BaseModel):
    """Telegram bot alert settings (token/chat_id via env vars)."""

    enabled: bool = False
    rate_limit_per_minute: int = 5
    include_thumbnail: bool = True
    language: str = "en"


class QuietHoursConfig(BaseModel):
    """Time window during which audible deterrents are silenced."""

    enabled: bool = False
    start: str = "22:00"
    end: str = "06:00"


class MonitorConfig(BaseModel):
    """Live monitoring / dashboard API server."""

    enabled: bool = True
    host: str = "127.0.0.1"
    port: int = 8765


class DemoConfig(BaseModel):
    """Demo mode overrides for presentations."""

    enabled: bool = False
    bypass_quiet_hours: bool = True
    use_demo_volume: bool = True


class RetentionConfig(BaseModel):
    """Event database retention limits."""

    max_events: int = 10000
    max_days: int = 90
    min_disk_free_mb: int = 500


class FarmGuardConfig(BaseModel):
    """Root configuration for FarmGuard."""

    camera: CameraConfig = Field(default_factory=CameraConfig)
    zones: ZoneConfig = Field(default_factory=ZoneConfig)
    detector: DetectorConfig = Field(default_factory=DetectorConfig)
    classifier: ClassifierConfig = Field(default_factory=ClassifierConfig)
    farm_classifier: FarmClassifierConfig = Field(default_factory=FarmClassifierConfig)
    voting: VotingConfig = Field(default_factory=VotingConfig)
    tracker: TrackerConfig = Field(default_factory=TrackerConfig)
    deterrent: DeterrentConfig = Field(default_factory=DeterrentConfig)
    beep: BeepConfig = Field(default_factory=BeepConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    quiet_hours: QuietHoursConfig = Field(default_factory=QuietHoursConfig)
    monitor: MonitorConfig = Field(default_factory=MonitorConfig)
    demo: DemoConfig = Field(default_factory=DemoConfig)
    retention: RetentionConfig = Field(default_factory=RetentionConfig)


# ---------------------------------------------------------------------------
# Loader helpers
# ---------------------------------------------------------------------------


def load_config(path: str | Path) -> FarmGuardConfig:
    """Load and validate a FarmGuard YAML config file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        A validated ``FarmGuardConfig`` instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        pydantic.ValidationError: If the YAML content is invalid.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return FarmGuardConfig.model_validate(raw)


def validate_config(path: str | Path) -> list[str]:
    """Validate a config file and return a list of error messages.

    Returns an empty list if valid.
    """
    errors: list[str] = []
    try:
        load_config(path)
    except FileNotFoundError as exc:
        errors.append(str(exc))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Validation error: {exc}")
    return errors

