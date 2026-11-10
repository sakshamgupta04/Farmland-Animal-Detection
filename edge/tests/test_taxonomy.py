"""Tests for the species taxonomy and SpeciesRegistry."""

from __future__ import annotations

import pytest

from farmguard.taxonomy import Species, ThreatLevel
from farmguard.taxonomy_ext import ALL_SPECIES, SpeciesRegistry


class TestSpeciesData:
    """Validate the canonical species list."""

    def test_total_count(self) -> None:
        assert len(ALL_SPECIES) == 27

    def test_unique_ids(self) -> None:
        ids = [s.species_id for s in ALL_SPECIES]
        assert len(ids) == len(set(ids))

    def test_unique_class_indices(self) -> None:
        indices = [s.model_class_index for s in ALL_SPECIES]
        assert sorted(indices) == list(range(27))

    def test_all_frozen(self) -> None:
        for sp in ALL_SPECIES:
            with pytest.raises(AttributeError):
                sp.species_id = "mutated"  # type: ignore[misc]


class TestSpeciesRegistry:
    """Test SpeciesRegistry lookup methods."""

    def test_get_by_id(self, registry: SpeciesRegistry) -> None:
        sp = registry.get("rhesus_macaque")
        assert sp.common_name == "Rhesus Macaque"
        assert sp.scientific_name == "Macaca mulatta"

    def test_get_by_id_missing(self, registry: SpeciesRegistry) -> None:
        with pytest.raises(KeyError):
            registry.get("unicorn")

    def test_get_by_class_index(self, registry: SpeciesRegistry) -> None:
        sp = registry.get_by_class_index(0)
        assert sp.species_id == "rhesus_macaque"

    def test_get_by_class_index_last(self, registry: SpeciesRegistry) -> None:
        sp = registry.get_by_class_index(26)
        assert sp.species_id == "vehicle"

    def test_get_by_class_index_missing(self, registry: SpeciesRegistry) -> None:
        with pytest.raises(KeyError):
            registry.get_by_class_index(999)

    def test_list_all_count(self, registry: SpeciesRegistry) -> None:
        assert len(registry.list_all()) == 27

    def test_list_all_sorted(self, registry: SpeciesRegistry) -> None:
        species = registry.list_all()
        indices = [s.model_class_index for s in species]
        assert indices == sorted(indices)

    def test_list_by_threat_level_high(self, registry: SpeciesRegistry) -> None:
        high = registry.list_by_threat_level(ThreatLevel.HIGH)
        assert len(high) == 4
        for sp in high:
            assert sp.threat_level == ThreatLevel.HIGH

    def test_list_by_threat_level_danger(self, registry: SpeciesRegistry) -> None:
        danger = registry.list_by_threat_level(ThreatLevel.DANGER)
        assert len(danger) == 5
        for sp in danger:
            assert sp.is_dangerous is True

    def test_list_harmful(self, registry: SpeciesRegistry) -> None:
        harmful = registry.list_harmful()
        for sp in harmful:
            assert sp.threat_level in (ThreatLevel.HIGH, ThreatLevel.MEDIUM)
        assert len(harmful) > 0

    def test_list_dangerous(self, registry: SpeciesRegistry) -> None:
        dangerous = registry.list_dangerous()
        expected_ids = {
            "indian_cobra", "common_krait", "sloth_bear",
            "indian_leopard", "indian_elephant",
        }
        actual_ids = {sp.species_id for sp in dangerous}
        assert actual_ids == expected_ids

    def test_list_beneficial(self, registry: SpeciesRegistry) -> None:
        beneficial = registry.list_beneficial()
        assert len(beneficial) == 1
        assert beneficial[0].species_id == "mongoose"

    def test_suppress_and_ignore(self, registry: SpeciesRegistry) -> None:
        person = registry.get("person")
        assert person.threat_level == ThreatLevel.SUPPRESS
        assert person.deterrent_allowed is False

        vehicle = registry.get("vehicle")
        assert vehicle.threat_level == ThreatLevel.IGNORE
        assert vehicle.deterrent_allowed is False

    def test_hindi_names_present(self, registry: SpeciesRegistry) -> None:
        for sp in registry.list_all():
            assert sp.hindi_name, f"{sp.species_id} missing hindi_name"


class TestThreatLevelEnum:
    """Test ThreatLevel properties."""

    def test_color_mapping(self) -> None:
        assert ThreatLevel.HIGH.color == "#FF0000"
        assert ThreatLevel.DANGER.color == "#8B0000"
        assert ThreatLevel.IGNORE.color == "#808080"

    def test_label(self) -> None:
        assert ThreatLevel.MEDIUM.label == "MEDIUM"

