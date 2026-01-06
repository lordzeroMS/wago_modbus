from __future__ import annotations

from typing import Iterable

from .models import ModbusBlock


def build_blocks(addresses: Iterable[int], max_block_size: int) -> list[ModbusBlock]:
    addresses = sorted(set(addresses))
    if not addresses:
        return []

    start = addresses[0]
    end = addresses[-1]
    blocks: list[ModbusBlock] = []
    current = start

    while current <= end:
        count = min(max_block_size, end - current + 1)
        blocks.append(ModbusBlock(start=current, count=count))
        current += count

    return blocks
