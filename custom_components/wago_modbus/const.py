from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Final

try:
    from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
    from homeassistant.const import PERCENTAGE, Platform, UnitOfTemperature
except ImportError:  # pragma: no cover - only for test environments without HA
    class SensorDeviceClass:
        TEMPERATURE = "temperature"
        HUMIDITY = "humidity"

    class SensorStateClass:
        MEASUREMENT = "measurement"
        TOTAL_INCREASING = "total_increasing"

    class Platform:
        SENSOR = "sensor"
        CLIMATE = "climate"
        SWITCH = "switch"

    PERCENTAGE = "%"

    class UnitOfTemperature:
        CELSIUS = "C"

DOMAIN: Final = "wago_modbus"
LOGGER = logging.getLogger(__name__)

PLATFORMS: Final = [Platform.SENSOR, Platform.CLIMATE, Platform.SWITCH]

DATA_COORDINATOR: Final = "coordinator"
DATA_HUB: Final = "hub"

CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_UNIT_ID: Final = "unit_id"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_ADDRESS_OFFSET: Final = "address_offset"
CONF_TIMEOUT: Final = "timeout"
CONF_MAX_REGISTERS_PER_REQUEST: Final = "max_registers_per_request"
CONF_MAX_COILS_PER_REQUEST: Final = "max_coils_per_request"

DEFAULT_PORT: Final = 502
DEFAULT_UNIT_ID: Final = 1
DEFAULT_SCAN_INTERVAL: Final = 10
DEFAULT_ADDRESS_OFFSET: Final = 0
DEFAULT_TIMEOUT: Final = 5
DEFAULT_MAX_REGISTERS_PER_REQUEST: Final = 125
DEFAULT_MAX_COILS_PER_REQUEST: Final = 2000

REGISTER_INPUT: Final = "input"
REGISTER_HOLDING: Final = "holding"

DATA_TYPE_INT16: Final = "int16"
DATA_TYPE_UINT16: Final = "uint16"


@dataclass(frozen=True)
class RegisterDefinition:
    key: str
    name: str
    address: int
    register_type: str
    data_type: str
    scale: float = 1.0
    offset: float = 0.0
    precision: int | None = None
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None


@dataclass(frozen=True)
class ClimateDefinition:
    key: str
    name: str
    current_temp_register: int
    target_temp_register: int
    scale: float
    precision: int
    min_temp: float
    max_temp: float
    temp_step: float


@dataclass(frozen=True)
class CoilDefinition:
    key: str
    name: str
    address: int


SENSOR_DEFINITIONS: Final = (
    RegisterDefinition(
        key="wohn_temp",
        name="Wohnzimmer Temperatur",
        address=32023,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="wohn_humidity",
        name="Wohnzimmer Luftfeuchtigkeit",
        address=32022,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="gaeste_temp",
        name="Gaestezimmer Temperatur",
        address=32011,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="gaeste_humidity",
        name="Gaestezimmer Luftfeuchtigkeit",
        address=32010,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="bad_unten_temp",
        name="Bad unten Temperatur",
        address=32005,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="bad_unten_humidity",
        name="Bad unten Luftfeuchtigkeit",
        address=32004,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="bad_oben_temp",
        name="Bad oben Temperatur",
        address=32002,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="bad_oben_humidity",
        name="Bad oben Luftfeuchtigkeit",
        address=32001,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="hwk_oben_temp",
        name="Hauswirtschaftsraum oben Temperatur",
        address=32014,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="hwk_oben_humidity",
        name="Hauswirtschaftsraum oben Luftfeuchtigkeit",
        address=32013,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="lilly_temp",
        name="Lilly Temperatur",
        address=32020,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="lilly_humidity",
        name="Lilly Luftfeuchtigkeit",
        address=32019,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="leroy_temp",
        name="Leroy Temperatur",
        address=32017,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="leroy_humidity",
        name="Leroy Luftfeuchtigkeit",
        address=32016,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="eltern_temp",
        name="Eltern Temperatur",
        address=32008,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="eltern_humidity",
        name="Eltern Luftfeuchtigkeit",
        address=32007,
        register_type=REGISTER_INPUT,
        data_type=DATA_TYPE_INT16,
        scale=0.01,
        precision=2,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_esszimmer_status",
        name="Rolladen Esszimmer Status",
        address=32027,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_gaestezimmer_west_status",
        name="Rolladen Gaestezimmer West Status",
        address=32031,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_gaestezimmer_sued_status",
        name="Rolladen Gaestezimmer Sued Status",
        address=32030,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_wohnzimmer_ost_status",
        name="Rolladen Wohnzimmer Ost Status",
        address=32037,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_wohnzimmer_sued_status",
        name="Rolladen Wohnzimmer Sued Status",
        address=32038,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_schlafzimmer_links_status",
        name="Rolladen Schlafzimmer Links Status",
        address=32035,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_schlafzimmer_rechts_status",
        name="Rolladen Schlafzimmer Rechts Status",
        address=32036,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_lilly_status",
        name="Rolladen Lilly Status",
        address=32034,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_leroy_status",
        name="Rolladen Leroy Status",
        address=32033,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RegisterDefinition(
        key="rolladen_kueche_status",
        name="Rolladen Kueche Status",
        address=32032,
        register_type=REGISTER_HOLDING,
        data_type=DATA_TYPE_UINT16,
        precision=0,
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

CLIMATE_DEFINITIONS: Final = (
    ClimateDefinition(
        key="wohn_climate",
        name="Wohnzimmer Heizung",
        current_temp_register=32023,
        target_temp_register=32024,
        scale=0.01,
        precision=1,
        min_temp=15.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
    ClimateDefinition(
        key="gaeste_climate",
        name="Gaestezimmer Heizung",
        current_temp_register=32011,
        target_temp_register=32012,
        scale=0.01,
        precision=1,
        min_temp=15.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
    ClimateDefinition(
        key="bad_unten_climate",
        name="Bad unten Heizung",
        current_temp_register=32005,
        target_temp_register=32006,
        scale=0.01,
        precision=1,
        min_temp=15.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
    ClimateDefinition(
        key="bad_oben_climate",
        name="Bad oben Heizung",
        current_temp_register=32002,
        target_temp_register=32003,
        scale=0.01,
        precision=1,
        min_temp=15.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
    ClimateDefinition(
        key="hwk_oben_climate",
        name="Hauswirtschaftsraum oben Heizung",
        current_temp_register=32014,
        target_temp_register=32015,
        scale=0.01,
        precision=1,
        min_temp=15.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
    ClimateDefinition(
        key="lilly_climate",
        name="Lilly Heizung",
        current_temp_register=32020,
        target_temp_register=32021,
        scale=0.01,
        precision=1,
        min_temp=15.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
    ClimateDefinition(
        key="leroy_climate",
        name="Leroy Heizung",
        current_temp_register=32017,
        target_temp_register=32018,
        scale=0.01,
        precision=1,
        min_temp=15.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
    ClimateDefinition(
        key="eltern_climate",
        name="Eltern Heizung",
        current_temp_register=32008,
        target_temp_register=32009,
        scale=0.01,
        precision=1,
        min_temp=15.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
)

COIL_DEFINITIONS: Final = (
    CoilDefinition(key="licht_aussen_kueche", name="Licht Aussen Kueche", address=33184),
    CoilDefinition(key="licht_aussen_wohnzimmer", name="Licht Aussen Wohnzimmer", address=33185),
    CoilDefinition(key="licht_buero_dg", name="Licht Buero DG", address=33192),
    CoilDefinition(key="licht_esszimmer_decke", name="Licht Esszimmer Decke", address=33186),
    CoilDefinition(key="licht_gaeste", name="Licht Gaestezimmer", address=33187),
    CoilDefinition(key="licht_garage", name="Licht Garage", address=33188),
    CoilDefinition(key="licht_hwr_unten", name="Licht HWR unten", address=33189),
    CoilDefinition(key="licht_hwr_oben", name="Licht HWR oben", address=33193),
    CoilDefinition(key="licht_kueche", name="Licht Kueche", address=33190),
    CoilDefinition(key="licht_leroy_1", name="Licht Leroy 1", address=33195),
    CoilDefinition(key="licht_leroy_2", name="Licht Leroy 2", address=33194),
    CoilDefinition(key="licht_lilly_1", name="Licht Lilly 1", address=33197),
    CoilDefinition(key="licht_lilly_2", name="Licht Lilly 2", address=33196),
    CoilDefinition(key="licht_eltern_1", name="Licht Eltern 1", address=33199),
    CoilDefinition(key="licht_eltern_2", name="Licht Eltern 2", address=33198),
    CoilDefinition(key="licht_wohnzimmer_decke", name="Licht Wohnzimmer Decke", address=33191),
)
