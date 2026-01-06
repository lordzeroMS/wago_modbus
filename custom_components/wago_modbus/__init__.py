from __future__ import annotations

from typing import TYPE_CHECKING

from .const import DATA_COORDINATOR, DATA_HUB, DOMAIN, PLATFORMS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from .coordinator import (
        WagoModbusCoordinator,
        async_build_hub,
        build_entry_blocks,
        entry_scan_interval,
    )

    hub = await async_build_hub(hass, entry)
    input_blocks, holding_blocks, coil_blocks = build_entry_blocks(entry)

    coordinator = WagoModbusCoordinator(
        hass,
        hub,
        input_blocks,
        holding_blocks,
        coil_blocks,
        entry_scan_interval(entry),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_HUB: hub,
        DATA_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
