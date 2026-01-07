from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_COORDINATOR,
    DATA_ENTITY_MAP,
    DATA_HUB,
    DATA_TYPE_INT16,
    DOMAIN,
    REGISTER_HOLDING,
)
from .coordinator import WagoModbusCoordinator, WagoModbusHub
from .helpers import build_device_info
from .values import decode_register_value, encode_register_value


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WagoModbusCoordinator = entry_data[DATA_COORDINATOR]
    hub: WagoModbusHub = entry_data[DATA_HUB]
    entity_map = entry_data[DATA_ENTITY_MAP]
    device_info = build_device_info(entry.entry_id)

    async_add_entities(
        WagoModbusClimate(coordinator, hub, entry.entry_id, device_info, definition)
        for definition in entity_map.climates
    )


class WagoModbusClimate(CoordinatorEntity[WagoModbusCoordinator], ClimateEntity):
    _attr_has_entity_name = True
    _attr_hvac_mode = HVACMode.HEAT
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: WagoModbusCoordinator,
        hub: WagoModbusHub,
        entry_id: str,
        device_info,
        definition,
    ) -> None:
        super().__init__(coordinator)
        self._hub = hub
        self._definition = definition
        self._attr_unique_id = f"{entry_id}_{definition.key}"
        self._attr_name = definition.name
        self._attr_device_info = device_info
        self._attr_min_temp = definition.min_temp
        self._attr_max_temp = definition.max_temp
        self._attr_target_temperature_step = definition.temp_step

    @property
    def current_temperature(self) -> float | None:
        return self._read_scaled(self._definition.current_temp_register)

    @property
    def target_temperature(self) -> float | None:
        return self._read_scaled(self._definition.target_temp_register)

    def _read_scaled(self, address: int) -> float | None:
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get_register(REGISTER_HOLDING, address)
        if raw is None:
            return None
        value = decode_register_value(raw, DATA_TYPE_INT16)
        value = value * self._definition.scale
        return round(value, self._definition.precision)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        raw_value = encode_register_value(
            temperature, self._definition.scale, offset=0.0
        )
        await self._hub.async_write_register(
            self._definition.target_temp_register, raw_value
        )
        await self.coordinator.async_request_refresh()
