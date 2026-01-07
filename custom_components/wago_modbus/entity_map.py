from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

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

    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as err:
            raise ValueError("Invalid JSON for entity map") from err
    elif isinstance(raw, dict):
        data = raw
    else:
        raise ValueError("Entity map must be a JSON string or object")

    sensors = tuple(_parse_register(item) for item in data.get("sensors", []))
    climates = tuple(_parse_climate(item) for item in data.get("climates", []))
    switches = tuple(_parse_coil(item) for item in data.get("switches", []))
    covers = tuple(_parse_cover(item) for item in data.get("covers", []))

    return EntityMap(
        sensors=sensors,
        climates=climates,
        switches=switches,
        covers=covers,
    )


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
    )


def _parse_cover(item: dict[str, Any]) -> CoverDefinition:
    return CoverDefinition(
        key=_require_str(item, "key"),
        name=_require_str(item, "name"),
        address=_require_int(item, "address"),
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
    return {"key": definition.key, "name": definition.name, "address": definition.address}


def _cover_to_dict(definition: CoverDefinition) -> dict[str, Any]:
    return {"key": definition.key, "name": definition.name, "address": definition.address}


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
