"""Species taxonomy continued — remaining species and the SpeciesRegistry."""

from __future__ import annotations

from farmguard.taxonomy import Species, ThreatLevel, _SPECIES_DATA

# ---------------------------------------------------------------------------
# Species 10–26
# ---------------------------------------------------------------------------

_SPECIES_DATA_EXT: tuple[Species, ...] = (
    Species(
        species_id="stray_dog",
        common_name="Stray Dog",
        scientific_name="Canis lupus familiaris",
        hindi_name="कुत्ता",
        family="Canidae",
        order="Carnivora",
        threat_level=ThreatLevel.LOW,
        crop_damage_types=("rarely",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=("email",),
        typical_weight_kg=(10.0, 25.0),
        active_hours="diurnal",
        model_class_index=10,
    ),
    Species(
        species_id="domestic_cat",
        common_name="Domestic Cat",
        scientific_name="Felis catus",
        hindi_name="बिल्ली",
        family="Felidae",
        order="Carnivora",
        threat_level=ThreatLevel.LOW,
        crop_damage_types=("none",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=("email",),
        typical_weight_kg=(3.0, 5.0),
        active_hours="crepuscular",
        model_class_index=11,
    ),
    Species(
        species_id="domestic_horse",
        common_name="Domestic Horse",
        scientific_name="Equus caballus",
        hindi_name="घोड़ा",
        family="Equidae",
        order="Perissodactyla",
        threat_level=ThreatLevel.LOW,
        crop_damage_types=("may_graze",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=("email",),
        typical_weight_kg=(380.0, 550.0),
        active_hours="diurnal",
        model_class_index=12,
    ),
    Species(
        species_id="domestic_donkey",
        common_name="Domestic Donkey",
        scientific_name="Equus asinus",
        hindi_name="गधा",
        family="Equidae",
        order="Perissodactyla",
        threat_level=ThreatLevel.LOW,
        crop_damage_types=("may_graze",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=("email",),
        typical_weight_kg=(100.0, 250.0),
        active_hours="diurnal",
        model_class_index=13,
    ),
    Species(
        species_id="camel",
        common_name="Camel",
        scientific_name="Camelus dromedarius",
        hindi_name="ऊँट",
        family="Camelidae",
        order="Artiodactyla",
        threat_level=ThreatLevel.LOW,
        crop_damage_types=("may_browse",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=("email",),
        typical_weight_kg=(300.0, 600.0),
        active_hours="diurnal",
        model_class_index=14,
    ),
    Species(
        species_id="indian_cobra",
        common_name="Indian Cobra",
        scientific_name="Naja naja",
        hindi_name="नाग",
        family="Elapidae",
        order="Squamata",
        threat_level=ThreatLevel.DANGER,
        crop_damage_types=("none",),
        is_beneficial=False,
        is_dangerous=True,
        deterrent_allowed=False,
        alert_channels=("email", "telegram"),
        typical_weight_kg=(0.5, 2.5),
        active_hours="nocturnal",
        model_class_index=15,
    ),
    Species(
        species_id="common_krait",
        common_name="Common Krait",
        scientific_name="Bungarus caeruleus",
        hindi_name="करैत",
        family="Elapidae",
        order="Squamata",
        threat_level=ThreatLevel.DANGER,
        crop_damage_types=("none",),
        is_beneficial=False,
        is_dangerous=True,
        deterrent_allowed=False,
        alert_channels=("email", "telegram"),
        typical_weight_kg=(0.3, 1.5),
        active_hours="nocturnal",
        model_class_index=16,
    ),
    Species(
        species_id="sloth_bear",
        common_name="Sloth Bear",
        scientific_name="Melursus ursinus",
        hindi_name="भालू",
        family="Ursidae",
        order="Carnivora",
        threat_level=ThreatLevel.DANGER,
        crop_damage_types=("minor",),
        is_beneficial=False,
        is_dangerous=True,
        deterrent_allowed=False,
        alert_channels=("email", "telegram"),
        typical_weight_kg=(55.0, 145.0),
        active_hours="nocturnal",
        model_class_index=17,
    ),
    Species(
        species_id="indian_leopard",
        common_name="Indian Leopard",
        scientific_name="Panthera pardus fusca",
        hindi_name="तेंदुआ",
        family="Felidae",
        order="Carnivora",
        threat_level=ThreatLevel.DANGER,
        crop_damage_types=("none",),
        is_beneficial=False,
        is_dangerous=True,
        deterrent_allowed=False,
        alert_channels=("email", "telegram"),
        typical_weight_kg=(30.0, 70.0),
        active_hours="nocturnal",
        model_class_index=18,
    ),
    Species(
        species_id="indian_elephant",
        common_name="Indian Elephant",
        scientific_name="Elephas maximus",
        hindi_name="हाथी",
        family="Elephantidae",
        order="Proboscidea",
        threat_level=ThreatLevel.DANGER,
        crop_damage_types=("massive",),
        is_beneficial=False,
        is_dangerous=True,
        deterrent_allowed=False,
        alert_channels=("email", "telegram"),
        typical_weight_kg=(2700.0, 5000.0),
        active_hours="crepuscular",
        model_class_index=19,
    ),
    Species(
        species_id="indian_jackal",
        common_name="Indian Jackal",
        scientific_name="Canis aureus",
        hindi_name="सियार",
        family="Canidae",
        order="Carnivora",
        threat_level=ThreatLevel.LOW,
        crop_damage_types=("rarely",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=("email",),
        typical_weight_kg=(6.0, 14.0),
        active_hours="nocturnal",
        model_class_index=20,
    ),
    Species(
        species_id="mongoose",
        common_name="Indian Grey Mongoose",
        scientific_name="Herpestes edwardsii",
        hindi_name="नेवला",
        family="Herpestidae",
        order="Carnivora",
        threat_level=ThreatLevel.LOW,
        crop_damage_types=("none",),
        is_beneficial=True,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=("email",),
        typical_weight_kg=(0.9, 1.8),
        active_hours="diurnal",
        model_class_index=21,
    ),
    Species(
        species_id="palm_squirrel",
        common_name="Three-striped Palm Squirrel",
        scientific_name="Funambulus palmarum",
        hindi_name="गिलहरी",
        family="Sciuridae",
        order="Rodentia",
        threat_level=ThreatLevel.MEDIUM,
        crop_damage_types=("fruits", "nuts"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(0.1, 0.2),
        active_hours="diurnal",
        model_class_index=22,
    ),
    Species(
        species_id="rat",
        common_name="Indian Field Rat",
        scientific_name="Rattus spp.",
        hindi_name="चूहा",
        family="Muridae",
        order="Rodentia",
        threat_level=ThreatLevel.MEDIUM,
        crop_damage_types=("stored_grain", "field_crops"),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=True,
        alert_channels=("beep", "email", "telegram"),
        typical_weight_kg=(0.1, 0.3),
        active_hours="nocturnal",
        model_class_index=23,
    ),
    Species(
        species_id="unknown_animal",
        common_name="Unknown Animal",
        scientific_name="—",
        hindi_name="अज्ञात जानवर",
        family="—",
        order="—",
        threat_level=ThreatLevel.MEDIUM,
        crop_damage_types=("unknown",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=("email", "telegram"),
        typical_weight_kg=(0.0, 0.0),
        active_hours="unknown",
        model_class_index=24,
    ),
    Species(
        species_id="person",
        common_name="Person",
        scientific_name="Homo sapiens",
        hindi_name="व्यक्ति",
        family="Hominidae",
        order="Primates",
        threat_level=ThreatLevel.SUPPRESS,
        crop_damage_types=("—",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=(),
        typical_weight_kg=(40.0, 100.0),
        active_hours="diurnal",
        model_class_index=25,
    ),
    Species(
        species_id="vehicle",
        common_name="Vehicle",
        scientific_name="—",
        hindi_name="वाहन",
        family="—",
        order="—",
        threat_level=ThreatLevel.IGNORE,
        crop_damage_types=("—",),
        is_beneficial=False,
        is_dangerous=False,
        deterrent_allowed=False,
        alert_channels=(),
        typical_weight_kg=(0.0, 0.0),
        active_hours="—",
        model_class_index=26,
    ),
)

# Merge both halves into the full list
ALL_SPECIES: tuple[Species, ...] = _SPECIES_DATA + _SPECIES_DATA_EXT


class SpeciesRegistry:
    """Singleton-style registry for looking up species by various keys.

    Example::

        registry = SpeciesRegistry()
        sp = registry.get("rhesus_macaque")
        print(sp.scientific_name)  # Macaca mulatta
    """

    def __init__(self) -> None:
        self._by_id: dict[str, Species] = {s.species_id: s for s in ALL_SPECIES}
        self._by_index: dict[int, Species] = {s.model_class_index: s for s in ALL_SPECIES}

    # -- single lookups ------------------------------------------------

    def get(self, species_id: str) -> Species:
        """Return a species by its unique ID, or raise ``KeyError``."""
        return self._by_id[species_id]

    def get_by_class_index(self, index: int) -> Species:
        """Return a species by its model class index, or raise ``KeyError``."""
        return self._by_index[index]

    # -- list queries --------------------------------------------------

    def list_all(self) -> list[Species]:
        """Return all 27 species in canonical order."""
        return sorted(self._by_id.values(), key=lambda s: s.model_class_index)

    def list_by_threat_level(self, level: ThreatLevel) -> list[Species]:
        """Return species matching the given threat level."""
        return [s for s in self.list_all() if s.threat_level == level]

    def list_harmful(self) -> list[Species]:
        """Return species with HIGH or MEDIUM threat level."""
        return [
            s
            for s in self.list_all()
            if s.threat_level in (ThreatLevel.HIGH, ThreatLevel.MEDIUM)
        ]

    def list_dangerous(self) -> list[Species]:
        """Return species flagged as dangerous to humans."""
        return [s for s in self.list_all() if s.is_dangerous]

    def list_beneficial(self) -> list[Species]:
        """Return species flagged as ecologically beneficial."""
        return [s for s in self.list_all() if s.is_beneficial]

