from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Iterable

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CLIMATE_DEFINITIONS,
    COIL_DEFINITIONS,
    CONF_ADDRESS_OFFSET,
    CONF_HOST,
    CONF_MAX_COILS_PER_REQUEST,
    CONF_MAX_REGISTERS_PER_REQUEST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_UNIT_ID,
    DEFAULT_ADDRESS_OFFSET,
    DEFAULT_MAX_COILS_PER_REQUEST,
    DEFAULT_MAX_REGISTERS_PER_REQUEST,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT_ID,
    LOGGER,
    REGISTER_HOLDING,
    REGISTER_INPUT,
    SENSOR_DEFINITIONS,
)
from .blocks import build_blocks
from .modbus_client import ModbusClientError, WagoModbusClient
from .models import ModbusBlock, ModbusData


class WagoModbusHub:
    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        unit_id: int,
        timeout: int,
        address_offset: int,
    ) -> None:
        self._hass = hass
        self._client = WagoModbusClient(host, port, unit_id, timeout, address_offset)
        self._lock = asyncio.Lock()

    def update_config(
        self, host: str, port: int, unit_id: int, timeout: int, address_offset: int
    ) -> None:
        self._client.update_config(host, port, unit_id, timeout, address_offset)

    async def async_read_blocks(
        self,
        input_blocks: Iterable[ModbusBlock],
        holding_blocks: Iterable[ModbusBlock],
        coil_blocks: Iterable[ModbusBlock],
    ) -> ModbusData:
        async with self._lock:
            return await self._hass.async_add_executor_job(
                self._client.read_blocks, input_blocks, holding_blocks, coil_blocks
            )

    async def async_write_coil(self, address: int, value: bool) -> None:
        async with self._lock:
            await self._hass.async_add_executor_job(
                self._client.write_coil, address, value
            )

    async def async_write_register(self, address: int, value: int) -> None:
        async with self._lock:
            await self._hass.async_add_executor_job(
                self._client.write_register, address, value
            )


def build_input_addresses() -> list[int]:
    return [
        definition.address
        for definition in SENSOR_DEFINITIONS
        if definition.register_type == REGISTER_INPUT
    ]


def build_holding_addresses() -> list[int]:
    addresses = [
        definition.address
        for definition in SENSOR_DEFINITIONS
        if definition.register_type == REGISTER_HOLDING
    ]
    for climate in CLIMATE_DEFINITIONS:
        addresses.append(climate.current_temp_register)
        addresses.append(climate.target_temp_register)
    return addresses


def build_coil_addresses() -> list[int]:
    return [definition.address for definition in COIL_DEFINITIONS]


def entry_option(entry, key, default):
    return entry.options.get(key, entry.data.get(key, default))


def build_entry_blocks(entry) -> tuple[list[ModbusBlock], list[ModbusBlock], list[ModbusBlock]]:
    max_registers = entry_option(
        entry, CONF_MAX_REGISTERS_PER_REQUEST, DEFAULT_MAX_REGISTERS_PER_REQUEST
    )
    max_coils = entry_option(
        entry, CONF_MAX_COILS_PER_REQUEST, DEFAULT_MAX_COILS_PER_REQUEST
    )
    input_blocks = build_blocks(build_input_addresses(), max_registers)
    holding_blocks = build_blocks(build_holding_addresses(), max_registers)
    coil_blocks = build_blocks(build_coil_addresses(), max_coils)
    return input_blocks, holding_blocks, coil_blocks


class WagoModbusCoordinator(DataUpdateCoordinator[ModbusData]):
    def __init__(
        self,
        hass: HomeAssistant,
        hub: WagoModbusHub,
        input_blocks: list[ModbusBlock],
        holding_blocks: list[ModbusBlock],
        coil_blocks: list[ModbusBlock],
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name="WAGO Modbus",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._hub = hub
        self._input_blocks = input_blocks
        self._holding_blocks = holding_blocks
        self._coil_blocks = coil_blocks

    async def _async_update_data(self) -> ModbusData:
        try:
            return await self._hub.async_read_blocks(
                self._input_blocks, self._holding_blocks, self._coil_blocks
            )
        except ModbusClientError as err:
            raise UpdateFailed(str(err)) from err

    def update_blocks(self, input_blocks, holding_blocks, coil_blocks) -> None:
        self._input_blocks = input_blocks
        self._holding_blocks = holding_blocks
        self._coil_blocks = coil_blocks


async def async_build_hub(hass: HomeAssistant, entry) -> WagoModbusHub:
    host = entry_option(entry, CONF_HOST, entry.data[CONF_HOST])
    port = entry_option(entry, CONF_PORT, DEFAULT_PORT)
    unit_id = entry_option(entry, CONF_UNIT_ID, DEFAULT_UNIT_ID)
    timeout = entry_option(entry, CONF_TIMEOUT, DEFAULT_TIMEOUT)
    address_offset = entry_option(entry, CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET)
    return WagoModbusHub(hass, host, port, unit_id, timeout, address_offset)


def entry_scan_interval(entry) -> int:
    return entry_option(entry, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
