"""Threat classification engine for FarmGuard.

Produces actionable threat assessments, deterrent profiles, and alert
priorities from species detections.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

from farmguard.taxonomy import ThreatLevel
from farmguard.taxonomy_ext import SpeciesRegistry


class AlertPriority(enum.IntEnum):
    """Numeric alert priority — higher value = more urgent."""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass(frozen=True)
class ThreatAssessment:
    """Result of classifying a detected species' threat.

    Attributes:
        threat_level: The species' inherent threat level.
        alert_priority: Computed alert urgency.
        recommended_actions: Ordered list of action identifiers.
        reasoning: Human-readable explanation.
    """

    threat_level: ThreatLevel
    alert_priority: AlertPriority
    recommended_actions: tuple[str, ...]
    reasoning: str


@dataclass(frozen=True)
class DeterrentProfile:
    """Escalation and timing rules for a deterrent response.

    Attributes:
        escalation_steps: Ordered list of deterrent action names.
        cooldown_seconds: Seconds before the same escalation may repeat.
        min_interval_seconds: Minimum gap between any two activations.
        alert_channels: Channels to notify (e.g. ``("beep", "email")``).
    """

    escalation_steps: tuple[str, ...]
    cooldown_seconds: float
    min_interval_seconds: float
    alert_channels: tuple[str, ...]


# ---------------------------------------------------------------------------
# Pre-built escalation profiles
# ---------------------------------------------------------------------------

_ESCALATION: dict[ThreatLevel, tuple[str, ...]] = {
    ThreatLevel.HIGH: (
        "visual_flash",
        "soft_beep",
        "loud_beep",
        "distress_call",
        "max_deterrent",
    ),
    ThreatLevel.MEDIUM: ("visual_flash", "soft_beep", "loud_beep"),
    ThreatLevel.LOW: ("log_only",),
    ThreatLevel.DANGER: ("silent_alert_only",),
    ThreatLevel.SUPPRESS: ("suppress_all",),
    ThreatLevel.IGNORE: ("ignore",),
}

_COOLDOWN: dict[ThreatLevel, float] = {
    ThreatLevel.HIGH: 30.0,
    ThreatLevel.MEDIUM: 60.0,
    ThreatLevel.LOW: 120.0,
    ThreatLevel.DANGER: 0.0,
    ThreatLevel.SUPPRESS: 0.0,
    ThreatLevel.IGNORE: 0.0,
}

_MIN_INTERVAL: dict[ThreatLevel, float] = {
    ThreatLevel.HIGH: 15.0,
    ThreatLevel.MEDIUM: 30.0,
    ThreatLevel.LOW: 60.0,
    ThreatLevel.DANGER: 0.0,
    ThreatLevel.SUPPRESS: 0.0,
    ThreatLevel.IGNORE: 0.0,
}

_PRIORITY_MAP: dict[ThreatLevel, AlertPriority] = {
    ThreatLevel.DANGER: AlertPriority.CRITICAL,
    ThreatLevel.HIGH: AlertPriority.HIGH,
    ThreatLevel.MEDIUM: AlertPriority.MEDIUM,
    ThreatLevel.LOW: AlertPriority.LOW,
    ThreatLevel.SUPPRESS: AlertPriority.NONE,
    ThreatLevel.IGNORE: AlertPriority.NONE,
}


class ThreatDatabase:
    """Stateless engine that maps species detections to threat profiles.

    Args:
        registry: The species registry to look up species data.
    """

    def __init__(self, registry: SpeciesRegistry) -> None:
        self._registry = registry

    # -- public API ----------------------------------------------------

    def classify_threat(
        self,
        species_id: str,
        confidence: float,
    ) -> ThreatAssessment:
        """Produce a threat assessment for a detected species.

        Args:
            species_id: Species identifier (must exist in the registry).
            confidence: Detection confidence in ``[0, 1]``.

        Returns:
            A frozen ``ThreatAssessment`` with recommended actions.
        """
        species = self._registry.get(species_id)
        level = species.threat_level
        priority = _PRIORITY_MAP[level]
        actions = _ESCALATION[level]

        if confidence < 0.4:
            reasoning = (
                f"Low-confidence ({confidence:.0%}) detection of "
                f"{species.common_name} — treat as uncertain."
            )
            actions = ("log_only",)
            priority = AlertPriority.LOW
        elif level == ThreatLevel.DANGER:
            reasoning = (
                f"DANGER — {species.common_name} ({species.scientific_name}) "
                f"detected at {confidence:.0%}. Do NOT approach. Silent alert sent."
            )
        elif level == ThreatLevel.HIGH:
            reasoning = (
                f"High-threat crop raider {species.common_name} detected at "
                f"{confidence:.0%}. Escalating deterrents."
            )
        elif level == ThreatLevel.MEDIUM:
            reasoning = (
                f"Moderate-threat species {species.common_name} detected at "
                f"{confidence:.0%}. Applying moderate deterrents."
            )
        elif level == ThreatLevel.SUPPRESS:
            reasoning = "Person detected — suppressing all actions."
        elif level == ThreatLevel.IGNORE:
            reasoning = "Vehicle detected — ignoring."
        else:
            reasoning = (
                f"Low-threat species {species.common_name} detected at "
                f"{confidence:.0%}. Logging only."
            )

        return ThreatAssessment(
            threat_level=level,
            alert_priority=priority,
            recommended_actions=actions,
            reasoning=reasoning,
        )

    def get_deterrent_profile(self, species_id: str) -> DeterrentProfile:
        """Return the deterrent escalation profile for a species.

        Args:
            species_id: Species identifier.

        Returns:
            A ``DeterrentProfile`` with escalation steps and timing.
        """
        species = self._registry.get(species_id)
        level = species.threat_level

        return DeterrentProfile(
            escalation_steps=_ESCALATION[level],
            cooldown_seconds=_COOLDOWN[level],
            min_interval_seconds=_MIN_INTERVAL[level],
            alert_channels=species.alert_channels,
        )

    def is_deterrent_safe(self, species_id: str) -> bool:
        """Return ``True`` if it is safe to activate deterrents.

        Returns ``False`` for dangerous animals and persons.
        """
        species = self._registry.get(species_id)
        return species.deterrent_allowed

    def get_alert_priority(self, species_id: str) -> AlertPriority:
        """Return the alert priority for a species.

        Args:
            species_id: Species identifier.

        Returns:
            An ``AlertPriority`` enum value.
        """
        species = self._registry.get(species_id)
        return _PRIORITY_MAP[species.threat_level]

