from wago_modbus.values import decode_register_value, encode_register_value


def test_decode_register_value_int16_negative() -> None:
    assert decode_register_value(0xFF9C, "int16") == -100


def test_decode_register_value_uint16_passthrough() -> None:
    assert decode_register_value(500, "uint16") == 500


def test_encode_register_value_scale_offset() -> None:
    assert encode_register_value(21.5, scale=0.01, offset=0.0) == 2150
    assert encode_register_value(10.0, scale=0.1, offset=2.0) == 80
