"""Simulation / stub implementations of FarmGuard interfaces.

Used for testing, demos, and running the pipeline without real hardware
or trained models.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np

from farmguard.interfaces import (
    Camera,
    ClassificationResult,
    Classifier,
    Detection,
    Detector,
    Deterrent,
    DeterrentAction,
    Event,
    EventStore,
    FarmSceneClassifier,
    Notifier,
    SceneResult,
    Clock,
)
from farmguard.taxonomy import ThreatLevel

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Clock implementations
# ---------------------------------------------------------------------------


class RealClock(Clock):
    """Clock backed by the system clock."""

    def now(self) -> float:
        """Return current UNIX timestamp."""
        return time.time()

    def monotonic(self) -> float:
        """Return monotonic time."""
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        """Sleep for ``seconds``."""
        time.sleep(seconds)


class FakeClock(Clock):
    """Deterministic clock for tests.

    Advance time manually with :meth:`advance`.
    """

    def __init__(self, start: float = 1_000_000.0) -> None:
        self._now = start
        self._mono = 0.0

    def now(self) -> float:
        """Return the fake UNIX timestamp."""
        return self._now

    def monotonic(self) -> float:
        """Return the fake monotonic time."""
        return self._mono

    def sleep(self, seconds: float) -> None:
        """Advance the clock by ``seconds`` (does not actually block)."""
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        """Manually advance both clocks."""
        self._now += seconds
        self._mono += seconds


# ---------------------------------------------------------------------------
# Simulation components
# ---------------------------------------------------------------------------


class SimCamera(Camera):
    """Simulated camera that reads from a video file or generates blank frames.

    Args:
        source: Path to a video file, or ``None`` for blank frames.
        width: Frame width (used for blank frames).
        height: Frame height (used for blank frames).
        fps_val: Simulated FPS value.
    """

    def __init__(
        self,
        source: str | None = None,
        width: int = 640,
        height: int = 480,
        fps_val: float = 15.0,
    ) -> None:
        self._source = source
        self._width = width
        self._height = height
        self._fps_val = fps_val
        self._open = False
        self._cap: object | None = None

    def open(self) -> None:
        """Open the camera / video source."""
        if self._source and Path(self._source).exists():
            import cv2  # type: ignore[import-untyped]

            self._cap = cv2.VideoCapture(self._source)
            self._open = True
        else:
            self._open = True

    def read(self) -> tuple[bool, np.ndarray | None]:
        """Read the next frame."""
        if not self._open:
            return False, None
        if self._cap is not None:
            import cv2  # type: ignore[import-untyped]

            ret, frame = self._cap.read()  # type: ignore[union-attr]
            return ret, frame if ret else None
        # Generate a blank frame
        frame = np.zeros((self._height, self._width, 3), dtype=np.uint8)
        return True, frame

    def close(self) -> None:
        """Release the camera."""
        if self._cap is not None:
            self._cap.release()  # type: ignore[union-attr]
        self._open = False
        self._cap = None

    def is_open(self) -> bool:
        """Return ``True`` if the camera is open."""
        return self._open

    @property
    def width(self) -> int:
        """Frame width."""
        return self._width

    @property
    def height(self) -> int:
        """Frame height."""
        return self._height

    @property
    def fps(self) -> float:
        """Frames per second."""
        return self._fps_val


class SimDetector(Detector):
    """Simulated detector that returns configurable fake detections."""

    def __init__(self, detections: list[Detection] | None = None) -> None:
        self._detections = detections or []

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Return pre-configured detections (ignores the frame)."""
        return list(self._detections)


class SimClassifier(Classifier):
    """Simulated classifier that always returns ``'unknown_animal'``."""

    def classify(self, crop: np.ndarray) -> ClassificationResult:
        """Return an 'unknown_animal' result."""
        return ClassificationResult(
            species_id="unknown_animal",
            common_name="Unknown Animal",
            scientific_name="—",
            hindi_name="अज्ञात जानवर",
            confidence=0.0,
            threat_level=ThreatLevel.MEDIUM,
            is_dangerous=False,
            is_uncertain=True,
        )


class SimFarmClassifier(FarmSceneClassifier):
    """Simulated farm-scene classifier — always returns farmland."""

    def classify_scene(self, frame: np.ndarray) -> SceneResult:
        """Return ``is_farmland=True``."""
        return SceneResult(is_farmland=True, confidence=1.0, scene_type="farmland")


class SimDeterrent(Deterrent):
    """Simulated deterrent that only logs activations."""

    def __init__(self) -> None:
        self._active = False
        self.log: list[DeterrentAction] = []

    def activate(self, action: DeterrentAction) -> None:
        """Log the action."""
        logger.info("SimDeterrent: %s (level %d)", action.action_type, action.level)
        self._active = True
        self.log.append(action)

    def deactivate(self) -> None:
        """Mark inactive."""
        self._active = False

    def is_active(self) -> bool:
        """Return activation status."""
        return self._active


class SimNotifier(Notifier):
    """Simulated notifier that logs instead of sending."""

    def __init__(self) -> None:
        self.sent: list[Event] = []

    def send_alert(self, event: Event, species: object) -> bool:
        """Log the alert and return ``True``."""
        logger.info("SimNotifier: alert for %s", event.species_id)
        self.sent.append(event)
        return True

