from __future__ import annotations

import asyncio
from typing import Any

import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv, selector

from .const import (
    CONF_HOST,
    CONF_ADDRESS_OFFSET,
    CONF_ENTITY_MAP,
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
    DOMAIN,
    LOGGER,
)
from .entity_map import default_entity_map_json, entity_map_to_json, parse_entity_map

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
        vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): vol.Coerce(int),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=""): cv.string,
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=5)
        ),
        vol.Required(CONF_ADDRESS_OFFSET, default=DEFAULT_ADDRESS_OFFSET): vol.Coerce(
            int
        ),
        vol.Required(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
        vol.Required(
            CONF_MAX_REGISTERS_PER_REQUEST,
            default=DEFAULT_MAX_REGISTERS_PER_REQUEST,
        ): vol.All(vol.Coerce(int), vol.Range(min=1, max=125)),
        vol.Required(
            CONF_MAX_COILS_PER_REQUEST, default=DEFAULT_MAX_COILS_PER_REQUEST
        ): vol.All(vol.Coerce(int), vol.Range(min=1, max=2000)),
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
        vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): vol.Coerce(int),
        vol.Required(
            CONF_ENTITY_MAP, default=default_entity_map_json()
        ): selector.TextSelector(
            selector.TextSelectorConfig(multiline=True, rows=20)
        ),
    }
)


async def _async_can_connect(host: str, port: int) -> bool:
    try:
        async with async_timeout.timeout(5):
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
    except (OSError, asyncio.TimeoutError) as err:
        LOGGER.debug("Modbus TCP connection check failed: %s", err)
        return False
    return True


class WagoModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WAGO Modbus."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})

            if not await _async_can_connect(
                user_input[CONF_HOST], user_input[CONF_PORT]
            ):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST], data=user_input
                )

        data_schema = self.add_suggested_values_to_schema(DATA_SCHEMA, user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return WagoModbusOptionsFlowHandler(config_entry)


class WagoModbusOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            raw_map = user_input.get(CONF_ENTITY_MAP)
            try:
                parsed_map = parse_entity_map(raw_map)
            except ValueError:
                errors[CONF_ENTITY_MAP] = "invalid_entity_map"
            else:
                user_input[CONF_ENTITY_MAP] = entity_map_to_json(parsed_map)

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        defaults = {
            CONF_HOST: self._config_entry.options.get(
                CONF_HOST, self._config_entry.data.get(CONF_HOST)
            ),
            CONF_SCAN_INTERVAL: self._config_entry.options.get(
                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
            ),
            CONF_ADDRESS_OFFSET: self._config_entry.options.get(
                CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET
            ),
            CONF_TIMEOUT: self._config_entry.options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
            CONF_MAX_REGISTERS_PER_REQUEST: self._config_entry.options.get(
                CONF_MAX_REGISTERS_PER_REQUEST, DEFAULT_MAX_REGISTERS_PER_REQUEST
            ),
            CONF_MAX_COILS_PER_REQUEST: self._config_entry.options.get(
                CONF_MAX_COILS_PER_REQUEST, DEFAULT_MAX_COILS_PER_REQUEST
            ),
            CONF_PORT: self._config_entry.options.get(
                CONF_PORT, self._config_entry.data.get(CONF_PORT, DEFAULT_PORT)
            ),
            CONF_UNIT_ID: self._config_entry.options.get(
                CONF_UNIT_ID, self._config_entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)
            ),
            CONF_ENTITY_MAP: self._config_entry.options.get(
                CONF_ENTITY_MAP, default_entity_map_json()
            ),
        }

        data_schema = self.add_suggested_values_to_schema(OPTIONS_SCHEMA, defaults)
        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors if user_input is not None else None,
        )
