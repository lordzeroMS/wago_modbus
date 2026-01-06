# AGENTS

Project: WAGO Modbus Home Assistant integration.

- Core code lives in `custom_components/wago_modbus`.
- Register and coil maps are defined in `custom_components/wago_modbus/const.py`.
- Modbus I/O is handled in `custom_components/wago_modbus/modbus_client.py`; batching logic lives in `custom_components/wago_modbus/coordinator.py`.
- UI configuration is in `custom_components/wago_modbus/config_flow.py`.
- Keep new files ASCII-only unless a non-ASCII character is required.
- No automated tests are set up yet.
