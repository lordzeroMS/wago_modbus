from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModbusBlock:
    start: int
    count: int


@dataclass
class ModbusData:
    input_registers: dict[int, int]
    holding_registers: dict[int, int]
    coils: dict[int, bool]

    def get_register(self, register_type: str, address: int) -> int | None:
        if register_type == "input":
            return self.input_registers.get(address)
        if register_type == "holding":
            return self.holding_registers.get(address)
        return None

    def get_coil(self, address: int) -> bool | None:
        return self.coils.get(address)
