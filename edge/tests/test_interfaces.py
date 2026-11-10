"""Tests for simulation components and the FakeClock."""

from __future__ import annotations

import numpy as np
import pytest

from farmguard.interfaces import Detection, DeterrentAction, Event
from farmguard.sim import (
    FakeClock,
    RealClock,
    SimCamera,
    SimClassifier,
    SimDeterrent,
    SimDetector,
    SimFarmClassifier,
    SimNotifier,
)
from farmguard.taxonomy import ThreatLevel


class TestFakeClock:
    """Verify FakeClock deterministic behaviour."""

    def test_initial_time(self, fake_clock: FakeClock) -> None:
        assert fake_clock.now() == 1_000_000.0
        assert fake_clock.monotonic() == 0.0

    def test_advance(self, fake_clock: FakeClock) -> None:
        fake_clock.advance(10.5)
        assert fake_clock.now() == 1_000_010.5
        assert fake_clock.monotonic() == 10.5

    def test_sleep_advances(self, fake_clock: FakeClock) -> None:
        fake_clock.sleep(5.0)
        assert fake_clock.now() == 1_000_005.0

    def test_multiple_advances(self, fake_clock: FakeClock) -> None:
        fake_clock.advance(1.0)
        fake_clock.advance(2.0)
        fake_clock.advance(3.0)
        assert fake_clock.monotonic() == 6.0


class TestRealClock:
    """Smoke-test the RealClock wrapper."""

    def test_now_positive(self) -> None:
        clock = RealClock()
        assert clock.now() > 0

    def test_monotonic_positive(self) -> None:
        clock = RealClock()
        assert clock.monotonic() > 0


class TestSimCamera:
    """Test the simulated camera."""

    def test_blank_frames(self) -> None:
        cam = SimCamera(width=320, height=240)
        cam.open()
        assert cam.is_open()
        ok, frame = cam.read()
        assert ok is True
        assert frame is not None
        assert frame.shape == (240, 320, 3)
        cam.close()
        assert cam.is_open() is False

    def test_read_when_closed(self) -> None:
        cam = SimCamera()
        ok, frame = cam.read()
        assert ok is False
        assert frame is None

    def test_properties(self) -> None:
        cam = SimCamera(width=1280, height=720, fps_val=30.0)
        assert cam.width == 1280
        assert cam.height == 720
        assert cam.fps == 30.0


class TestSimDetector:
    """Test the simulated detector."""

    def test_empty_by_default(self) -> None:
        det = SimDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        assert det.detect(frame) == []

    def test_configurable_detections(self) -> None:
        fake_det = Detection(bbox=(10, 20, 100, 200), confidence=0.9, label="animal")
        det = SimDetector(detections=[fake_det])
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        results = det.detect(frame)
        assert len(results) == 1
        assert results[0].confidence == 0.9


class TestSimClassifier:
    """Test the simulated species classifier."""

    def test_returns_unknown(self) -> None:
        cls = SimClassifier()
        crop = np.zeros((224, 224, 3), dtype=np.uint8)
        result = cls.classify(crop)
        assert result.species_id == "unknown_animal"
        assert result.is_uncertain is True
        assert result.threat_level == ThreatLevel.MEDIUM


class TestSimFarmClassifier:
    """Test the simulated farm-scene classifier."""

    def test_always_farmland(self) -> None:
        cls = SimFarmClassifier()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = cls.classify_scene(frame)
        assert result.is_farmland is True
        assert result.confidence == 1.0


class TestSimDeterrent:
    """Test the simulated deterrent."""

    def test_activate_logs(self) -> None:
        det = SimDeterrent()
        assert det.is_active() is False
        action = DeterrentAction(action_type="soft_beep", level=1)
        det.activate(action)
        assert det.is_active() is True
        assert len(det.log) == 1
        det.deactivate()
        assert det.is_active() is False


class TestSimNotifier:
    """Test the simulated notifier."""

    def test_send_alert_logs(self) -> None:
        notifier = SimNotifier()
        event = Event(species_id="wild_boar")
        result = notifier.send_alert(event, species=None)
        assert result is True
        assert len(notifier.sent) == 1

