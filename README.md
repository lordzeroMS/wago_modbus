# WAGO Modbus Home Assistant Integration

Custom Home Assistant integration for a WAGO Modbus TCP controller with a fixed register map. The integration batches reads to avoid overwhelming the controller (one unified register read plus one coil read by default).

## Features
- Batched Modbus reads with one FC4 register block set plus one coil block set.
- Sensor entities for temperature, humidity, and shutter status.
- Climate entities for heating setpoints.
- Switch entities for lights.
- Cover entities for roller shutters.
- Config flow UI with options for scan interval, address offset, and request sizing.

## Polling Behavior
- Register-backed entities (sensors, climates, covers) are polled via `read_input_registers` (FC4) using merged address blocks.
- Switch entities are polled via `read_coils` (FC1).
- With the sample map and default limits, this results in 2 read requests per scan cycle:
  - 1 register request
  - 1 coil request
- Additional diagnostic sensors are exposed:
  - `Modbus Requests Total` (count since integration start)
  - `Modbus Requests Error` (failed request count since integration start)

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
- Entity map (JSON or YAML)

## Notes
- The default register map is defined in `custom_components/wago_modbus/const.py`.
- You can override the register map via the entity map in the options flow (JSON or YAML).
- Full map format example: `entity_map.sample.json`
- Minimal format example (covers/switches only): `entity_map.simple.sample.yaml`
- Entity names are ASCII-only by default; you can rename entities in Home Assistant for localized names.
- Ensure your controller exposes the configured register addresses through FC4 (`read_input_registers`).
- Climate and cover writes still use `write_register` for target/control registers.

## Minimal Entity Map Format
You can paste this directly in the UI options field to define only switches/covers:

```yaml
entities:
  - name: "Terrace Blind"
    type: cover
    modbus_address: 32027
    reversed: false
  - name: "Kitchen Blind"
    type: cover
    address: 32032
    reversed: true
  - name: "Garden Light"
    type: switch
    address: 33184
    reversed: false
```

Supported fields per entry:
- `name` (required)
- `type` (required): `cover`, `switch` (or `coil`)
- `address` or `modbus_address` (required)
- `reversed` (optional): `true` / `false`
- `key` (optional): auto-generated from `name` if omitted
