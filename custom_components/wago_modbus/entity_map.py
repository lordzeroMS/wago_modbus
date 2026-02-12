from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - Home Assistant ships pyyaml
    yaml = None

from .const import (
    CLIMATE_DEFINITIONS,
    COIL_DEFINITIONS,
    CONF_ENTITY_MAP,
    COVER_DEFINITIONS,
    DATA_TYPE_INT16,
    DATA_TYPE_UINT16,
    PERCENTAGE,
    REGISTER_HOLDING,
    REGISTER_INPUT,
    SENSOR_DEFINITIONS,
    SensorDeviceClass,
    SensorStateClass,
    UnitOfTemperature,
)
from .const import ClimateDefinition, CoilDefinition, CoverDefinition, RegisterDefinition


@dataclass(frozen=True)
class EntityMap:
    sensors: tuple[RegisterDefinition, ...]
    climates: tuple[ClimateDefinition, ...]
    switches: tuple[CoilDefinition, ...]
    covers: tuple[CoverDefinition, ...]


def default_entity_map() -> EntityMap:
    return EntityMap(
        sensors=SENSOR_DEFINITIONS,
        climates=CLIMATE_DEFINITIONS,
        switches=COIL_DEFINITIONS,
        covers=COVER_DEFINITIONS,
    )


def default_entity_map_json() -> str:
    return entity_map_to_json(default_entity_map())


def entity_map_to_json(entity_map: EntityMap) -> str:
    payload = {
        "sensors": [_register_to_dict(item) for item in entity_map.sensors],
        "climates": [_climate_to_dict(item) for item in entity_map.climates],
        "switches": [_coil_to_dict(item) for item in entity_map.switches],
        "covers": [_cover_to_dict(item) for item in entity_map.covers],
    }
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)


def load_entity_map(entry) -> EntityMap:
    raw = entry.options.get(CONF_ENTITY_MAP)
    return parse_entity_map(raw)


def parse_entity_map(raw: Any) -> EntityMap:
    if raw in (None, ""):
        return default_entity_map()

    data = _load_entity_map_payload(raw)
    if isinstance(data, list):
        return _parse_simple_entities(data)
    if not isinstance(data, dict):
        raise ValueError("Entity map must be a JSON/YAML object or list")
    if "entities" in data:
        return _parse_simple_entities(_require_list(data, "entities"))

    sensors = tuple(_parse_register(item) for item in _read_items(data, "sensors"))
    climates = tuple(_parse_climate(item) for item in _read_items(data, "climates"))
    switches = tuple(_parse_coil(item) for item in _read_items(data, "switches"))
    covers = tuple(_parse_cover(item) for item in _read_items(data, "covers"))

    return EntityMap(
        sensors=sensors,
        climates=climates,
        switches=switches,
        covers=covers,
    )


def _load_entity_map_payload(raw: Any) -> Any:
    if isinstance(raw, (dict, list)):
        return raw
    if not isinstance(raw, str):
        raise ValueError("Entity map must be a JSON/YAML string, object, or list")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        if yaml is None:
            raise ValueError("Invalid entity map JSON/YAML")
        try:
            payload = yaml.safe_load(raw)
        except yaml.YAMLError as err:
            raise ValueError("Invalid entity map JSON/YAML") from err
        if payload is None:
            return {}
        return payload


def _read_items(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    items = data.get(key, [])
    if not isinstance(items, list):
        raise ValueError(f"Invalid {key}: expected a list")
    parsed_items: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid {key}: expected an object entry")
        parsed_items.append(item)
    return parsed_items


def _parse_simple_entities(items: list[dict[str, Any]]) -> EntityMap:
    switches: list[CoilDefinition] = []
    covers: list[CoverDefinition] = []
    seen_keys: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Invalid entities entry: expected an object")
        name = _require_str(item, "name")
        entity_type = _simple_entity_type(item)
        key = _simple_entity_key(item, name, entity_type, seen_keys)
        seen_keys.add(key)
        address = _simple_entity_address(item)
        reversed_flag = _optional_bool(item, "reversed")
        if entity_type == "switch":
            switches.append(
                CoilDefinition(
                    key=key,
                    name=name,
                    address=address,
                    reversed=reversed_flag,
                )
            )
        else:
            covers.append(
                CoverDefinition(
                    key=key,
                    name=name,
                    address=address,
                    reversed=reversed_flag,
                )
            )
    return EntityMap(
        sensors=(),
        climates=(),
        switches=tuple(switches),
        covers=tuple(covers),
    )


def _simple_entity_type(item: dict[str, Any]) -> str:
    raw_type = item.get("type", item.get("entity_type"))
    if not isinstance(raw_type, str):
        raise ValueError("Missing or invalid type")
    normalized = raw_type.strip().lower()
    if normalized in ("switch", "coil"):
        return "switch"
    if normalized == "cover":
        return "cover"
    raise ValueError(f"Invalid type '{raw_type}'")


def _simple_entity_address(item: dict[str, Any]) -> int:
    if "address" in item:
        return _require_int(item, "address")
    if "modbus_address" in item:
        return _require_int(item, "modbus_address")
    raise ValueError("Missing or invalid address")


def _simple_entity_key(
    item: dict[str, Any], name: str, entity_type: str, seen_keys: set[str]
) -> str:
    if "key" in item:
        key = _require_str(item, "key")
        if key in seen_keys:
            raise ValueError(f"Duplicate key '{key}'")
        return key

    base = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if not base:
        base = f"{entity_type}_{_simple_entity_address(item)}"
    candidate = base
    suffix = 2
    while candidate in seen_keys:
        candidate = f"{base}_{suffix}"
        suffix += 1
    return candidate


def _require_list(item: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = item.get(key)
    if not isinstance(value, list):
        raise ValueError(f"Missing or invalid {key}")
    return value


def _parse_register(item: dict[str, Any]) -> RegisterDefinition:
    key = _require_str(item, "key")
    name = _require_str(item, "name")
    address = _require_int(item, "address")
    register_type = item.get("register_type", REGISTER_INPUT)
    data_type = item.get("data_type", DATA_TYPE_INT16)
    scale = float(item.get("scale", 1.0))
    offset = float(item.get("offset", 0.0))
    precision = item.get("precision")
    unit = _map_unit(item.get("unit"))
    device_class = _map_device_class(item.get("device_class"))
    state_class = _map_state_class(item.get("state_class"))

    if register_type not in (REGISTER_INPUT, REGISTER_HOLDING):
        raise ValueError(f"Invalid register_type for {key}")
    if data_type not in (DATA_TYPE_INT16, DATA_TYPE_UINT16):
        raise ValueError(f"Invalid data_type for {key}")

    return RegisterDefinition(
        key=key,
        name=name,
        address=address,
        register_type=register_type,
        data_type=data_type,
        scale=scale,
        offset=offset,
        precision=int(precision) if precision is not None else None,
        unit=unit,
        device_class=device_class,
        state_class=state_class,
    )


def _parse_climate(item: dict[str, Any]) -> ClimateDefinition:
    return ClimateDefinition(
        key=_require_str(item, "key"),
        name=_require_str(item, "name"),
        current_temp_register=_require_int(item, "current_temp_register"),
        target_temp_register=_require_int(item, "target_temp_register"),
        scale=float(item.get("scale", 1.0)),
        precision=int(item.get("precision", 1)),
        min_temp=float(item.get("min_temp", 0.0)),
        max_temp=float(item.get("max_temp", 40.0)),
        temp_step=float(item.get("temp_step", 1.0)),
    )


def _parse_coil(item: dict[str, Any]) -> CoilDefinition:
    return CoilDefinition(
        key=_require_str(item, "key"),
        name=_require_str(item, "name"),
        address=_require_int(item, "address"),
        reversed=_optional_bool(item, "reversed"),
    )


def _parse_cover(item: dict[str, Any]) -> CoverDefinition:
    return CoverDefinition(
        key=_require_str(item, "key"),
        name=_require_str(item, "name"),
        address=_require_int(item, "address"),
        reversed=_optional_bool(item, "reversed"),
    )


def _require_str(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Missing or invalid {key}")
    return value


def _require_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if isinstance(value, bool) or value is None:
        raise ValueError(f"Missing or invalid {key}")
    try:
        return int(value)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Missing or invalid {key}") from err


def _optional_bool(item: dict[str, Any], key: str) -> bool:
    value = item.get(key)
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("1", "true", "yes", "on"):
            return True
        if normalized in ("0", "false", "no", "off"):
            return False
    raise ValueError(f"Missing or invalid {key}")


def _map_unit(unit: str | None) -> str | None:
    if not unit:
        return None
    unit_value = unit.strip()
    if unit_value.lower() in ("c", "°c", "celsius"):
        return UnitOfTemperature.CELSIUS
    if unit_value in ("%", "percent", "percentage"):
        return PERCENTAGE
    return unit


def _map_device_class(value: str | None) -> str | None:
    if not value:
        return None
    key = value.strip().upper()
    if hasattr(SensorDeviceClass, key):
        return getattr(SensorDeviceClass, key)
    return value


def _map_state_class(value: str | None) -> str | None:
    if not value:
        return None
    key = value.strip().upper()
    if hasattr(SensorStateClass, key):
        return getattr(SensorStateClass, key)
    return value


def _register_to_dict(definition: RegisterDefinition) -> dict[str, Any]:
    return {
        "key": definition.key,
        "name": definition.name,
        "address": definition.address,
        "register_type": definition.register_type,
        "data_type": definition.data_type,
        "scale": definition.scale,
        "offset": definition.offset,
        "precision": definition.precision,
        "unit": _unit_to_str(definition.unit),
        "device_class": _class_to_str(definition.device_class),
        "state_class": _class_to_str(definition.state_class),
    }


def _climate_to_dict(definition: ClimateDefinition) -> dict[str, Any]:
    return {
        "key": definition.key,
        "name": definition.name,
        "current_temp_register": definition.current_temp_register,
        "target_temp_register": definition.target_temp_register,
        "scale": definition.scale,
        "precision": definition.precision,
        "min_temp": definition.min_temp,
        "max_temp": definition.max_temp,
        "temp_step": definition.temp_step,
    }


def _coil_to_dict(definition: CoilDefinition) -> dict[str, Any]:
    payload = {
        "key": definition.key,
        "name": definition.name,
        "address": definition.address,
    }
    if definition.reversed:
        payload["reversed"] = True
    return payload


def _cover_to_dict(definition: CoverDefinition) -> dict[str, Any]:
    payload = {
        "key": definition.key,
        "name": definition.name,
        "address": definition.address,
    }
    if definition.reversed:
        payload["reversed"] = True
    return payload


def _unit_to_str(unit: str | None) -> str | None:
    if not unit:
        return None
    if unit in (UnitOfTemperature.CELSIUS, "°C", "C"):
        return "C"
    if unit == PERCENTAGE:
        return "%"
    return unit


def _class_to_str(value: str | None) -> str | None:
    return value
