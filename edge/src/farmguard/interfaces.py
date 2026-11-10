"""Abstract interfaces and core data objects for FarmGuard.

Defines the contracts every pipeline component must satisfy, plus the
shared data structures passed between stages.
"""

from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from farmguard.taxonomy import ThreatLevel

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Data objects
# ---------------------------------------------------------------------------


@dataclass
class Detection:
    """A single bounding-box detection from the Stage-1 detector.

    Attributes:
        bbox: ``(x1, y1, x2, y2)`` normalised or pixel coordinates.
        confidence: Detection confidence in ``[0, 1]``.
        label: Detector label string (e.g., ``'animal'``).
        track_id: Tracker-assigned ID, or ``None`` before tracking.
    """

    bbox: tuple[float, float, float, float]
    confidence: float
    label: str
    track_id: int | None = None


@dataclass
class ClassificationResult:
    """Stage-2 species classification output.

    Attributes:
        species_id: Canonical species identifier.
        common_name: English common name.
        scientific_name: Binomial Latin name.
        hindi_name: Devanagari name.
        confidence: Top-class softmax confidence.
        threat_level: Mapped threat level.
        is_dangerous: Safety flag.
        is_uncertain: ``True`` when confidence < threshold.
        all_scores: Optional full score dictionary.
    """

    species_id: str
    common_name: str
    scientific_name: str
    hindi_name: str
    confidence: float
    threat_level: ThreatLevel
    is_dangerous: bool
    is_uncertain: bool
    all_scores: dict[str, float] | None = None


@dataclass
class SceneResult:
    """Farm scene classifier output.

    Attributes:
        is_farmland: Whether the frame is a farm scene.
        confidence: Scene classification confidence.
        scene_type: Descriptive scene label.
    """

    is_farmland: bool
    confidence: float
    scene_type: str


@dataclass
class DeterrentAction:
    """A deterrent activation command.

    Attributes:
        action_type: Action identifier (e.g. ``'soft_beep'``).
        level: Escalation level (0-based).
        sound_pattern: Optional beep pattern name.
    """

    action_type: str
    level: int
    sound_pattern: str | None = None


@dataclass
class Event:
    """A logged detection event for storage and alerting.

    Attributes:
        id: Unique UUID string.
        species_id: Detected species identifier.
        common_name: English name.
        scientific_name: Latin name.
        threat_level: Threat classification.
        confidence: Detection confidence.
        zone: Zone name where detected.
        started_at: UNIX timestamp of first detection.
        ended_at: UNIX timestamp of last detection, or ``None``.
        actions: List of actions taken.
        status: Event status (``'active'``, ``'resolved'``, etc.).
        thumbnail_path: Path to saved thumbnail image, or ``None``.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    species_id: str = ""
    common_name: str = ""
    scientific_name: str = ""
    threat_level: ThreatLevel = ThreatLevel.LOW
    confidence: float = 0.0
    zone: str = ""
    started_at: float = 0.0
    ended_at: float | None = None
    actions: list[str] = field(default_factory=list)
    status: str = "active"
    thumbnail_path: str | None = None


# ---------------------------------------------------------------------------
# Abstract interfaces
# ---------------------------------------------------------------------------


class Camera(abc.ABC):
    """Abstract camera / video source."""

    @abc.abstractmethod
    def open(self) -> None:
        """Open the camera source."""

    @abc.abstractmethod
    def read(self) -> tuple[bool, np.ndarray | None]:
        """Read the next frame. Returns ``(success, frame_or_None)``."""

    @abc.abstractmethod
    def close(self) -> None:
        """Release the camera resource."""

    @abc.abstractmethod
    def is_open(self) -> bool:
        """Return ``True`` if the camera is currently open."""

    @property
    @abc.abstractmethod
    def width(self) -> int:
        """Frame width in pixels."""

    @property
    @abc.abstractmethod
    def height(self) -> int:
        """Frame height in pixels."""

    @property
    @abc.abstractmethod
    def fps(self) -> float:
        """Frames per second."""


class Detector(abc.ABC):
    """Abstract animal detector (Stage 1)."""

    @abc.abstractmethod
    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Run detection on a frame and return bounding boxes."""


class Classifier(abc.ABC):
    """Abstract species classifier (Stage 2)."""

    @abc.abstractmethod
    def classify(self, crop: np.ndarray) -> ClassificationResult:
        """Classify a cropped animal image."""


class FarmSceneClassifier(abc.ABC):
    """Abstract farm-scene classifier."""

    @abc.abstractmethod
    def classify_scene(self, frame: np.ndarray) -> SceneResult:
        """Determine whether the frame shows a farmland scene."""


class Deterrent(abc.ABC):
    """Abstract deterrent actuator."""

    @abc.abstractmethod
    def activate(self, action: DeterrentAction) -> None:
        """Activate a deterrent action."""

    @abc.abstractmethod
    def deactivate(self) -> None:
        """Deactivate the current deterrent."""

    @abc.abstractmethod
    def is_active(self) -> bool:
        """Return ``True`` if a deterrent is currently active."""


class Notifier(abc.ABC):
    """Abstract alert notifier (email, Telegram, etc.)."""

    @abc.abstractmethod
    def send_alert(self, event: Event, species: object) -> bool:
        """Send an alert for a detection event. Returns ``True`` on success."""


class EventStore(abc.ABC):
    """Abstract event persistence layer."""

    @abc.abstractmethod
    def save_event(self, event: Event) -> None:
        """Persist an event."""

    @abc.abstractmethod
    def get_events(self, limit: int = 100, offset: int = 0) -> list[Event]:
        """Retrieve stored events with pagination."""

    @abc.abstractmethod
    def get_pending_sync(self) -> list[Event]:
        """Return events not yet synced to the cloud."""


class Clock(abc.ABC):
    """Abstract clock for testability."""

    @abc.abstractmethod
    def now(self) -> float:
        """Return current UNIX timestamp."""

    @abc.abstractmethod
    def monotonic(self) -> float:
        """Return monotonic time in seconds."""

    @abc.abstractmethod
    def sleep(self, seconds: float) -> None:
        """Sleep for the given duration."""

