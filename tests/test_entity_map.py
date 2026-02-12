import pytest

from wago_modbus.entity_map import entity_map_to_json, parse_entity_map


def test_parse_simple_yaml_entities() -> None:
    raw = """
entities:
  - name: Kitchen Blind
    type: cover
    modbus_address: 32032
    reversed: true
  - name: Garden Light
    type: switch
    address: 33184
"""
    entity_map = parse_entity_map(raw)

    assert entity_map.sensors == ()
    assert entity_map.climates == ()
    assert len(entity_map.covers) == 1
    assert len(entity_map.switches) == 1
    assert entity_map.covers[0].key == "kitchen_blind"
    assert entity_map.covers[0].reversed is True
    assert entity_map.switches[0].key == "garden_light"
    assert entity_map.switches[0].reversed is False


def test_parse_simple_entities_supports_type_alias_and_string_bool() -> None:
    raw = {
        "entities": [
            {
                "name": "Hallway Light",
                "type": "coil",
                "address": "33185",
                "reversed": "yes",
            }
        ]
    }
    entity_map = parse_entity_map(raw)

    assert len(entity_map.switches) == 1
    assert entity_map.switches[0].address == 33185
    assert entity_map.switches[0].reversed is True


def test_parse_full_format_supports_reversed_flags() -> None:
    raw = {
        "sensors": [],
        "climates": [],
        "switches": [{"key": "s1", "name": "Switch 1", "address": 100, "reversed": 1}],
        "covers": [{"key": "c1", "name": "Cover 1", "address": 200, "reversed": True}],
    }

    entity_map = parse_entity_map(raw)
    payload = entity_map_to_json(entity_map)

    assert entity_map.switches[0].reversed is True
    assert entity_map.covers[0].reversed is True
    assert '"reversed": true' in payload


def test_parse_simple_entities_rejects_unknown_type() -> None:
    raw = {"entities": [{"name": "Bad", "type": "sensor", "address": 1}]}
    with pytest.raises(ValueError):
        parse_entity_map(raw)
