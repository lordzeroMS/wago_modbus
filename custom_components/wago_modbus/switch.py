from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COIL_DEFINITIONS, DATA_COORDINATOR, DATA_HUB, DOMAIN
from .coordinator import WagoModbusCoordinator, WagoModbusHub
from .helpers import build_device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WagoModbusCoordinator = entry_data[DATA_COORDINATOR]
    hub: WagoModbusHub = entry_data[DATA_HUB]
    device_info = build_device_info(entry.entry_id)

    async_add_entities(
        WagoModbusSwitch(coordinator, hub, entry.entry_id, device_info, definition)
        for definition in COIL_DEFINITIONS
    )


class WagoModbusSwitch(CoordinatorEntity[WagoModbusCoordinator], SwitchEntity):
    _attr_has_entity_name = True

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

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get_coil(self._definition.address)

    async def async_turn_on(self, **kwargs) -> None:
        await self._hub.async_write_coil(self._definition.address, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._hub.async_write_coil(self._definition.address, False)
        await self.coordinator.async_request_refresh()
