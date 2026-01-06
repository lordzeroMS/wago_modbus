# WAGO Modbus Home Assistant Integration

Custom Home Assistant integration for a WAGO Modbus TCP controller with a fixed register map. The integration batches reads to avoid overwhelming the controller (one request per register type by default).

## Features
- Batched Modbus reads for input registers, holding registers, and coils.
- Sensor entities for temperature, humidity, and shutter status.
- Climate entities for heating setpoints.
- Switch entities for lights.
- Cover entities for roller shutters.
- Config flow UI with options for scan interval, address offset, and request sizing.

## Installation
1. Copy `custom_components/wago_modbus` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via **Settings > Devices & Services > Add Integration**.

## Configuration
Initial setup in the UI only asks for connection details:
- Host
- Port (default 502)
- Unit ID (default 1)

Options (via the integration options menu):
- Host
- Scan interval (seconds)
- Address offset (use `-1` if your device uses 1-based addresses)
- Timeout
- Max registers per request (default 125)
- Max coils per request (default 2000)
- Port and Unit ID overrides

## Notes
- The register map is currently hardcoded from `modbus.yaml`. Adjust definitions in `custom_components/wago_modbus/const.py` if addresses or names change.
- Entity names are ASCII-only by default; you can rename entities in Home Assistant for localized names.
