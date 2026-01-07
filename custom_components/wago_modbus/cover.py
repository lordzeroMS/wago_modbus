from __future__ import annotations

from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_COORDINATOR,
    DATA_ENTITY_MAP,
    DATA_HUB,
    DOMAIN,
    REGISTER_HOLDING,
)
from .coordinator import WagoModbusCoordinator, WagoModbusHub
from .helpers import build_device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WagoModbusCoordinator = entry_data[DATA_COORDINATOR]
    hub: WagoModbusHub = entry_data[DATA_HUB]
    entity_map = entry_data[DATA_ENTITY_MAP]
    device_info = build_device_info(entry.entry_id)

    async_add_entities(
        WagoModbusCover(coordinator, hub, entry.entry_id, device_info, definition)
        for definition in entity_map.covers
    )


class WagoModbusCover(CoordinatorEntity[WagoModbusCoordinator], CoverEntity):
    _attr_has_entity_name = True
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
    )

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
    def current_cover_position(self) -> int | None:
        status = self._read_status()
        if status is None:
            return None
        return max(0, min(100, 100 - status))

    @property
    def is_closed(self) -> bool | None:
        status = self._read_status()
        if status is None:
            return None
        if status <= 5:
            return False
        if status >= 95:
            return True
        return None

    async def async_open_cover(self, **kwargs) -> None:
        await self._hub.async_write_register(self._definition.address, 0)
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs) -> None:
        await self._hub.async_write_register(self._definition.address, 100)
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs) -> None:
        position = kwargs.get("position")
        if position is None:
            return
        target = max(0, min(100, 100 - int(position)))
        await self._hub.async_write_register(self._definition.address, target)
        await self.coordinator.async_request_refresh()

    def _read_status(self) -> int | None:
        if not self.coordinator.data:
            return None
        status = self.coordinator.data.get_register(
            REGISTER_HOLDING, self._definition.address
        )
        if status is None:
            return None
        return int(status)
