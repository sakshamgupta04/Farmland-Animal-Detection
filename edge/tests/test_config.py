"""Tests for FarmGuard configuration loading and validation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from farmguard.config import FarmGuardConfig, load_config, validate_config


class TestDefaultConfig:
    """Verify that a default config has sensible values."""

    def test_defaults_valid(self, sample_config: FarmGuardConfig) -> None:
        assert sample_config.camera.width == 1280
        assert sample_config.detector.confidence_threshold == 0.4
        assert sample_config.classifier.input_size == 224
        assert sample_config.deterrent.kill_switch is False

    def test_beep_patterns_present(self, sample_config: FarmGuardConfig) -> None:
        patterns = sample_config.beep.patterns
        assert "attention" in patterns
        assert "warning" in patterns
        assert "urgent" in patterns
        assert "danger_alert" in patterns

    def test_email_disabled_by_default(self, sample_config: FarmGuardConfig) -> None:
        assert sample_config.email.enabled is False

    def test_telegram_disabled_by_default(self, sample_config: FarmGuardConfig) -> None:
        assert sample_config.telegram.enabled is False


class TestConfigLoading:
    """Test YAML config loading."""

    def test_load_minimal_yaml(self, tmp_yaml: Path) -> None:
        cfg = load_config(str(tmp_yaml))
        assert cfg.camera.source == "0"
        # All other fields should get defaults
        assert cfg.detector.input_size == 640

    def test_load_missing_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.yaml")

    def test_load_empty_yaml(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.yaml"
        p.write_text("", encoding="utf-8")
        cfg = load_config(str(p))
        # Should produce a valid default config
        assert cfg.camera.width == 1280

    def test_load_partial_yaml(self, tmp_path: Path) -> None:
        content = yaml.dump({
            "camera": {"source": "test.mp4", "width": 1920},
            "deterrent": {"kill_switch": True},
        })
        p = tmp_path / "partial.yaml"
        p.write_text(content, encoding="utf-8")
        cfg = load_config(str(p))
        assert cfg.camera.source == "test.mp4"
        assert cfg.camera.width == 1920
        assert cfg.camera.height == 720  # default
        assert cfg.deterrent.kill_switch is True

    def test_load_example_yaml(self) -> None:
        # Try loading the shipped example config
        example = (
            Path(__file__).resolve().parents[2] / "config" / "farm.example.yaml"
        )
        if example.exists():
            cfg = load_config(str(example))
            assert cfg.camera.source == "0"


class TestConfigValidation:
    """Test the validate_config helper."""

    def test_validate_valid(self, tmp_yaml: Path) -> None:
        errors = validate_config(str(tmp_yaml))
        assert errors == []

    def test_validate_missing_file(self) -> None:
        errors = validate_config("nonexistent.yaml")
        assert len(errors) == 1
        assert "not found" in errors[0].lower()

    def test_validate_bad_yaml(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.yaml"
        p.write_text("camera:\n  width: not_a_number\n", encoding="utf-8")
        errors = validate_config(str(p))
        assert len(errors) >= 1

