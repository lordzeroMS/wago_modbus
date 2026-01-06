from __future__ import annotations

from .const import DATA_TYPE_INT16


def decode_register_value(raw: int, data_type: str) -> int:
    if data_type == DATA_TYPE_INT16 and raw >= 0x8000:
        return raw - 0x10000
    return raw


def encode_register_value(value: float, scale: float, offset: float) -> int:
    scaled = (value - offset) / scale
    return int(round(scaled))
