from wago_modbus.blocks import build_blocks
from wago_modbus.models import ModbusBlock


def test_build_blocks_empty() -> None:
    assert build_blocks([], max_block_size=10) == []


def test_build_blocks_contiguous() -> None:
    blocks = build_blocks([1, 2, 3, 4], max_block_size=10)
    assert blocks == [ModbusBlock(start=1, count=4)]


def test_build_blocks_gaps_split_by_size() -> None:
    blocks = build_blocks([1, 2, 3, 10, 11], max_block_size=4)
    assert blocks == [
        ModbusBlock(start=1, count=4),
        ModbusBlock(start=5, count=4),
        ModbusBlock(start=9, count=3),
    ]
