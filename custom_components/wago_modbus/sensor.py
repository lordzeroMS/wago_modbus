from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DATA_ENTITY_MAP, DOMAIN
from .coordinator import WagoModbusCoordinator
from .helpers import build_device_info
from .values import decode_register_value


@dataclass(frozen=True, kw_only=True)
class WagoSensorDescription(SensorEntityDescription):
    address: int
    register_type: str
    data_type: str
    scale: float
    offset: float
    precision: int | None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: WagoModbusCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    entity_map = hass.data[DOMAIN][entry.entry_id][DATA_ENTITY_MAP]
    device_info = build_device_info(entry.entry_id)
    sensor_types = tuple(
        WagoSensorDescription(
            key=definition.key,
            name=definition.name,
            native_unit_of_measurement=definition.unit,
            device_class=definition.device_class,
            state_class=definition.state_class,
            address=definition.address,
            register_type=definition.register_type,
            data_type=definition.data_type,
            scale=definition.scale,
            offset=definition.offset,
            precision=definition.precision,
        )
        for definition in entity_map.sensors
    )

    async_add_entities(
        WagoModbusSensor(coordinator, entry.entry_id, device_info, description)
        for description in sensor_types
    )


class WagoModbusSensor(CoordinatorEntity[WagoModbusCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WagoModbusCoordinator,
        entry_id: str,
        device_info,
        description: WagoSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> Any:
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get_register(
            self.entity_description.register_type, self.entity_description.address
        )
        if raw is None:
            return None
        value = decode_register_value(raw, self.entity_description.data_type)
        value = value * self.entity_description.scale + self.entity_description.offset
        if self.entity_description.precision is not None:
            return round(value, self.entity_description.precision)
        return value
