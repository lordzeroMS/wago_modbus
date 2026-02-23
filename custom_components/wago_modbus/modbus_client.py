from __future__ import annotations

import inspect
from typing import Iterable

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import LOGGER
from .models import ModbusBlock, ModbusData


class ModbusClientError(RuntimeError):
    """Raised when Modbus communication fails."""


class WagoModbusClient:
    def __init__(
        self,
        host: str,
        port: int,
        unit_id: int,
        timeout: int,
        address_offset: int,
    ) -> None:
        self._host = host
        self._port = port
        self._unit_id = unit_id
        self._timeout = timeout
        self._address_offset = address_offset
        self._request_count = 0
        self._request_error_count = 0

    @property
    def request_count(self) -> int:
        return self._request_count

    @property
    def request_error_count(self) -> int:
        return self._request_error_count

    def _mark_request(self) -> None:
        self._request_count += 1

    def _mark_request_error(self) -> None:
        self._request_error_count += 1

    def update_config(
        self, host: str, port: int, unit_id: int, timeout: int, address_offset: int
    ) -> None:
        self._host = host
        self._port = port
        self._unit_id = unit_id
        self._timeout = timeout
        self._address_offset = address_offset

    def read_blocks(
        self,
        input_blocks: Iterable[ModbusBlock],
        holding_blocks: Iterable[ModbusBlock],
        coil_blocks: Iterable[ModbusBlock],
    ) -> ModbusData:
        client = ModbusTcpClient(self._host, port=self._port, timeout=self._timeout)
        if not client.connect():
            self._mark_request()
            self._mark_request_error()
            raise ModbusClientError("Unable to connect to Modbus TCP host")

        input_registers: dict[int, int] = {}
        holding_registers: dict[int, int] = {}
        coils: dict[int, bool] = {}

        try:
            for block in input_blocks:
                registers = self._read_register_block(
                    client, block, register_type="input"
                )
                input_registers.update(registers)
                # FC4 is used as the unified polling source. Mirror values so
                # entities that look up holding registers still resolve.
                holding_registers.update(registers)

            for block in holding_blocks:
                registers = self._read_register_block(
                    client, block, register_type="holding"
                )
                holding_registers.update(registers)

            for block in coil_blocks:
                block_values = self._read_coil_block(client, block)
                coils.update(block_values)
        finally:
            client.close()

        return ModbusData(
            input_registers=input_registers,
            holding_registers=holding_registers,
            coils=coils,
        )

    def write_coil(self, address: int, value: bool) -> None:
        client = ModbusTcpClient(self._host, port=self._port, timeout=self._timeout)
        if not client.connect():
            self._mark_request()
            self._mark_request_error()
            raise ModbusClientError("Unable to connect to Modbus TCP host")
        try:
            result = self._call_with_unit(
                client.write_coil, address + self._address_offset, value
            )
            if result.isError():
                self._mark_request_error()
                raise ModbusClientError("Modbus coil write failed")
        except ModbusException as err:
            LOGGER.debug("Modbus write_coil error: %s", err)
            raise ModbusClientError("Modbus coil write raised an exception") from err
        finally:
            client.close()

    def write_register(self, address: int, value: int) -> None:
        client = ModbusTcpClient(self._host, port=self._port, timeout=self._timeout)
        if not client.connect():
            self._mark_request()
            self._mark_request_error()
            raise ModbusClientError("Unable to connect to Modbus TCP host")
        try:
            result = self._call_with_unit(
                client.write_register, address + self._address_offset, value
            )
            if result.isError():
                self._mark_request_error()
                raise ModbusClientError("Modbus register write failed")
        except ModbusException as err:
            LOGGER.debug("Modbus write_register error: %s", err)
            raise ModbusClientError("Modbus register write raised an exception") from err
        finally:
            client.close()

    def _read_register_block(
        self, client: ModbusTcpClient, block: ModbusBlock, register_type: str
    ) -> dict[int, int]:
        start_address = block.start + self._address_offset
        try:
            if register_type == "input":
                result = self._call_with_unit(
                    client.read_input_registers,
                    start_address,
                    count=block.count,
                )
            else:
                result = self._call_with_unit(
                    client.read_holding_registers,
                    start_address,
                    count=block.count,
                )
        except ModbusException as err:
            LOGGER.debug("Modbus read error (%s): %s", register_type, err)
            raise ModbusClientError("Modbus register read raised an exception") from err

        if result.isError() or not hasattr(result, "registers"):
            self._mark_request_error()
            raise ModbusClientError("Modbus register read returned error")

        registers: dict[int, int] = {}
        for idx, value in enumerate(result.registers):
            registers[block.start + idx] = value
        return registers

    def _read_coil_block(
        self, client: ModbusTcpClient, block: ModbusBlock
    ) -> dict[int, bool]:
        start_address = block.start + self._address_offset
        try:
            result = self._call_with_unit(
                client.read_coils, start_address, count=block.count
            )
        except ModbusException as err:
            LOGGER.debug("Modbus coil read error: %s", err)
            raise ModbusClientError("Modbus coil read raised an exception") from err

        if result.isError() or not hasattr(result, "bits"):
            self._mark_request_error()
            raise ModbusClientError("Modbus coil read returned error")

        coils: dict[int, bool] = {}
        for idx, value in enumerate(result.bits[: block.count]):
            coils[block.start + idx] = bool(value)
        return coils

    def _call_with_unit(self, func, *args, **kwargs):
        self._mark_request()
        try:
            params = inspect.signature(func).parameters
        except (TypeError, ValueError):
            params = {}
        try:
            if "slave" in params:
                return func(*args, slave=self._unit_id, **kwargs)
            if "unit" in params:
                return func(*args, unit=self._unit_id, **kwargs)
            return func(*args, **kwargs)
        except Exception:
            self._mark_request_error()
            raise
