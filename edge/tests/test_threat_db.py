"""Tests for the ThreatDatabase engine."""

from __future__ import annotations

import pytest

from farmguard.taxonomy import ThreatLevel
from farmguard.taxonomy_ext import SpeciesRegistry
from farmguard.threat_db import AlertPriority, ThreatDatabase


class TestThreatClassification:
    """Verify threat assessments for each threat level."""

    def test_high_threat(self, threat_db: ThreatDatabase) -> None:
        result = threat_db.classify_threat("rhesus_macaque", 0.9)
        assert result.threat_level == ThreatLevel.HIGH
        assert result.alert_priority == AlertPriority.HIGH
        assert "visual_flash" in result.recommended_actions
        assert "max_deterrent" in result.recommended_actions

    def test_medium_threat(self, threat_db: ThreatDatabase) -> None:
        result = threat_db.classify_threat("indian_peafowl", 0.8)
        assert result.threat_level == ThreatLevel.MEDIUM
        assert result.alert_priority == AlertPriority.MEDIUM
        assert "loud_beep" in result.recommended_actions
        assert "max_deterrent" not in result.recommended_actions

    def test_low_threat(self, threat_db: ThreatDatabase) -> None:
        result = threat_db.classify_threat("stray_dog", 0.7)
        assert result.threat_level == ThreatLevel.LOW
        assert result.alert_priority == AlertPriority.LOW
        assert result.recommended_actions == ("log_only",)

    def test_danger_threat(self, threat_db: ThreatDatabase) -> None:
        result = threat_db.classify_threat("indian_cobra", 0.85)
        assert result.threat_level == ThreatLevel.DANGER
        assert result.alert_priority == AlertPriority.CRITICAL
        assert result.recommended_actions == ("silent_alert_only",)
        assert "Do NOT approach" in result.reasoning

    def test_suppress_person(self, threat_db: ThreatDatabase) -> None:
        result = threat_db.classify_threat("person", 0.95)
        assert result.threat_level == ThreatLevel.SUPPRESS
        assert result.alert_priority == AlertPriority.NONE
        assert result.recommended_actions == ("suppress_all",)

    def test_ignore_vehicle(self, threat_db: ThreatDatabase) -> None:
        result = threat_db.classify_threat("vehicle", 0.9)
        assert result.threat_level == ThreatLevel.IGNORE
        assert result.alert_priority == AlertPriority.NONE
        assert result.recommended_actions == ("ignore",)

    def test_low_confidence_overrides(self, threat_db: ThreatDatabase) -> None:
        result = threat_db.classify_threat("wild_boar", 0.2)
        assert result.recommended_actions == ("log_only",)
        assert result.alert_priority == AlertPriority.LOW
        assert "uncertain" in result.reasoning


class TestDeterrentProfiles:
    """Verify deterrent escalation profiles."""

    def test_high_escalation_steps(self, threat_db: ThreatDatabase) -> None:
        profile = threat_db.get_deterrent_profile("wild_boar")
        assert len(profile.escalation_steps) == 5
        assert profile.escalation_steps[0] == "visual_flash"
        assert profile.escalation_steps[-1] == "max_deterrent"

    def test_medium_escalation_steps(self, threat_db: ThreatDatabase) -> None:
        profile = threat_db.get_deterrent_profile("spotted_deer")
        assert len(profile.escalation_steps) == 3

    def test_danger_silent_only(self, threat_db: ThreatDatabase) -> None:
        profile = threat_db.get_deterrent_profile("indian_leopard")
        assert profile.escalation_steps == ("silent_alert_only",)

    def test_cooldown_times(self, threat_db: ThreatDatabase) -> None:
        assert threat_db.get_deterrent_profile("nilgai").cooldown_seconds == 30.0
        assert threat_db.get_deterrent_profile("indian_hare").cooldown_seconds == 60.0
        assert threat_db.get_deterrent_profile("stray_dog").cooldown_seconds == 120.0

    def test_alert_channels(self, threat_db: ThreatDatabase) -> None:
        profile = threat_db.get_deterrent_profile("rhesus_macaque")
        assert "beep" in profile.alert_channels
        assert "email" in profile.alert_channels


class TestDeterrentSafety:
    """Verify that dangerous animals never get deterrents."""

    @pytest.mark.parametrize(
        "species_id",
        ["indian_cobra", "common_krait", "sloth_bear", "indian_leopard", "indian_elephant"],
    )
    def test_dangerous_not_safe(self, threat_db: ThreatDatabase, species_id: str) -> None:
        assert threat_db.is_deterrent_safe(species_id) is False

    def test_person_not_safe(self, threat_db: ThreatDatabase) -> None:
        assert threat_db.is_deterrent_safe("person") is False

    def test_high_threat_is_safe(self, threat_db: ThreatDatabase) -> None:
        assert threat_db.is_deterrent_safe("rhesus_macaque") is True
        assert threat_db.is_deterrent_safe("wild_boar") is True

    def test_low_threat_not_safe(self, threat_db: ThreatDatabase) -> None:
        # LOW-threat animals have deterrent_allowed=False
        assert threat_db.is_deterrent_safe("stray_dog") is False


class TestAlertPriority:
    """Verify alert priority mapping."""

    def test_danger_is_critical(self, threat_db: ThreatDatabase) -> None:
        assert threat_db.get_alert_priority("indian_cobra") == AlertPriority.CRITICAL

    def test_high_is_high(self, threat_db: ThreatDatabase) -> None:
        assert threat_db.get_alert_priority("nilgai") == AlertPriority.HIGH

    def test_medium_is_medium(self, threat_db: ThreatDatabase) -> None:
        assert threat_db.get_alert_priority("indian_peafowl") == AlertPriority.MEDIUM

    def test_low_is_low(self, threat_db: ThreatDatabase) -> None:
        assert threat_db.get_alert_priority("mongoose") == AlertPriority.LOW

    def test_person_is_none(self, threat_db: ThreatDatabase) -> None:
        assert threat_db.get_alert_priority("person") == AlertPriority.NONE

    def test_vehicle_is_none(self, threat_db: ThreatDatabase) -> None:
        assert threat_db.get_alert_priority("vehicle") == AlertPriority.NONE

