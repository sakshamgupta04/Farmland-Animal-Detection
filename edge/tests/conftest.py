"""Shared pytest fixtures for FarmGuard tests."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from farmguard.config import FarmGuardConfig
from farmguard.sim import FakeClock
from farmguard.taxonomy_ext import SpeciesRegistry
from farmguard.threat_db import ThreatDatabase


@pytest.fixture()
def registry() -> SpeciesRegistry:
    """Return a fresh SpeciesRegistry."""
    return SpeciesRegistry()


@pytest.fixture()
def threat_db(registry: SpeciesRegistry) -> ThreatDatabase:
    """Return a ThreatDatabase wired to the registry."""
    return ThreatDatabase(registry)


@pytest.fixture()
def fake_clock() -> FakeClock:
    """Return a FakeClock starting at 1 000 000."""
    return FakeClock(start=1_000_000.0)


@pytest.fixture()
def sample_config() -> FarmGuardConfig:
    """Return a default FarmGuardConfig."""
    return FarmGuardConfig()


@pytest.fixture()
def example_yaml_path() -> str:
    """Return path to the example YAML config."""
    path = Path(__file__).resolve().parents[2] / "config" / "farm.example.yaml"
    # Fallback to repo-root config
    if not path.exists():
        path = (
            Path(__file__).resolve().parents[3] / "config" / "farm.example.yaml"
        )
    return str(path)


@pytest.fixture()
def tmp_yaml(tmp_path: Path) -> Path:
    """Create a minimal valid YAML config file and return its path."""
    content = "camera:\n  source: '0'\n"
    p = tmp_path / "test_config.yaml"
    p.write_text(content, encoding="utf-8")
    return p

