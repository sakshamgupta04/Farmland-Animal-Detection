"""Species taxonomy and threat classification for FarmGuard.

Contains the 27-species database with scientific names, threat levels,
crop damage profiles, and a registry for lookups.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class ThreatLevel(enum.Enum):
    """Threat classification for detected species.

    Each level maps to a display color for the dashboard.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DANGER = "danger"
    SUPPRESS = "suppress"
    IGNORE = "ignore"

    @property
    def color(self) -> str:
        """Return hex color for dashboard display."""
        colors: dict[str, str] = {
            "high": "#FF0000",
            "medium": "#FFA500",
            "low": "#00AA00",
            "danger": "#8B0000",
            "suppress": "#0000FF",
            "ignore": "#808080",
        }
        return colors[self.value]

    @property
    def label(self) -> str:
        """Return human-readable label."""
        return self.value.upper()


@dataclass(frozen=True)
class Species:
    """Immutable record for a single species in the FarmGuard taxonomy.

    Attributes:
        species_id: Unique snake_case identifier (e.g., ``'rhesus_macaque'``).
        common_name: English common name.
        scientific_name: Binomial Latin name (``'—'`` if not applicable).
        hindi_name: Name in Devanagari script.
        family: Taxonomic family (``'—'`` if not applicable).
        order: Taxonomic order (``'—'`` if not applicable).
        threat_level: Classified threat to crops / safety.
        crop_damage_types: Types of crops this species damages.
        is_beneficial: Whether the species is ecologically beneficial on farms.
        is_dangerous: Whether the species poses physical danger to humans.
        deterrent_allowed: Whether humane deterrents may be activated.
        alert_channels: Tuple of alert channel names to use.
        typical_weight_kg: ``(min_kg, max_kg)`` typical adult weight range.
        active_hours: Activity pattern (diurnal / nocturnal / crepuscular / unknown).
        model_class_index: Index in the species-classifier output vector.
    """

    species_id: str
    common_name: str
    scientific_name: str
    hindi_name: str
    family: str
    order: str
    threat_level: ThreatLevel
    crop_damage_types: tuple[str, ...]
    is_beneficial: bool
    is_dangerous: bool
    deterrent_allowed: bool
    alert_channels: tuple[str, ...]
    typical_weight_kg: tuple[float, float]
    active_hours: str
    model_class_index: int


# ---------------------------------------------------------------------------
# Canonical species list — 27 entries
# ---------------------------------------------------------------------------

_SPECIES_DATA: tuple[Species, ...] = (
    Species(
        species_id="rhesus_macaque",
        common_name="Rhesus Macaque",
        scientific_name="Macaca mulatta",
        hindi_name="रीसस बंदर",
        family="Cercopithecidae",
        order="Primates",
        threat_level=ThreatLevel.HIGH,
        crop_damage_types=("fruits", "vegetables", "grains"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(5.0, 11.0),
        active_hours="diurnal",
        model_class_index=0,
    ),
    Species(
        species_id="hanuman_langur",
        common_name="Hanuman Langur",
        scientific_name="Semnopithecus entellus",
        hindi_name="हनुमान लंगूर",
        family="Cercopithecidae",
        order="Primates",
        threat_level=ThreatLevel.HIGH,
        crop_damage_types=("fruits", "leaves"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(9.0, 21.0),
        active_hours="diurnal",
        model_class_index=1,
    ),
    Species(
        species_id="wild_boar",
        common_name="Wild Boar",
        scientific_name="Sus scrofa",
        hindi_name="जंगली सूअर",
        family="Suidae",
        order="Artiodactyla",
        threat_level=ThreatLevel.HIGH,
        crop_damage_types=("root_crops", "sugarcane", "paddy"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(50.0, 100.0),
        active_hours="nocturnal",
        model_class_index=2,
    ),
    Species(
        species_id="nilgai",
        common_name="Nilgai",
        scientific_name="Boselaphus tragocamelus",
        hindi_name="नीलगाय",
        family="Bovidae",
        order="Artiodactyla",
        threat_level=ThreatLevel.HIGH,
        crop_damage_types=("wheat", "mustard", "vegetables"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(120.0, 240.0),
        active_hours="crepuscular",
        model_class_index=3,
    ),
    Species(
        species_id="indian_peafowl",
        common_name="Indian Peafowl",
        scientific_name="Pavo cristatus",
        hindi_name="मोर",
        family="Phasianidae",
        order="Galliformes",
        threat_level=ThreatLevel.MEDIUM,
        crop_damage_types=("grains", "seeds"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(3.0, 6.0),
        active_hours="diurnal",
        model_class_index=4,
    ),
    Species(
        species_id="spotted_deer",
        common_name="Spotted Deer",
        scientific_name="Axis axis",
        hindi_name="चीतल",
        family="Cervidae",
        order="Artiodactyla",
        threat_level=ThreatLevel.MEDIUM,
        crop_damage_types=("young_shoots", "crops"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(35.0, 75.0),
        active_hours="crepuscular",
        model_class_index=5,
    ),
    Species(
        species_id="sambar_deer",
        common_name="Sambar Deer",
        scientific_name="Rusa unicolor",
        hindi_name="सांभर",
        family="Cervidae",
        order="Artiodactyla",
        threat_level=ThreatLevel.MEDIUM,
        crop_damage_types=("crops", "bark"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(100.0, 260.0),
        active_hours="crepuscular",
        model_class_index=6,
    ),
    Species(
        species_id="indian_hare",
        common_name="Indian Hare",
        scientific_name="Lepus nigricollis",
        hindi_name="खरगोश",
        family="Leporidae",
        order="Lagomorpha",
        threat_level=ThreatLevel.MEDIUM,
        crop_damage_types=("vegetables", "pulses"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(1.5, 3.5),
        active_hours="nocturnal",
        model_class_index=7,
    ),
    Species(
        species_id="indian_porcupine",
        common_name="Indian Porcupine",
        scientific_name="Hystrix indica",
        hindi_name="साही",
        family="Hystricidae",
        order="Rodentia",
        threat_level=ThreatLevel.MEDIUM,
        crop_damage_types=("root_crops", "tubers"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(11.0, 18.0),
        active_hours="nocturnal",
        model_class_index=8,
    ),
    Species(
        species_id="stray_cattle",
        common_name="Stray Cattle",
        scientific_name="Bos taurus",
        hindi_name="आवारा गाय",
        family="Bovidae",
        order="Artiodactyla",
        threat_level=ThreatLevel.MEDIUM,
        crop_damage_types=("grazes_crops",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(200.0, 500.0),
        active_hours="diurnal",
        model_class_index=9,
    ),
)

