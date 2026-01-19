"""Датчики для 2E Power Stations через Tuya IoT."""
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfFrequency,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Налаштування датчиків з config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Base sensors - always add
    entities = [
        PowerStationBatterySensor(coordinator, entry),
    ]

    # Power sensors - add if available in data
    if "total_input_power" in coordinator.data:
        entities.append(PowerStationInputPowerSensor(coordinator, entry))
    if "total_output_power" in coordinator.data:
        entities.append(PowerStationOutputPowerSensor(coordinator, entry))
    if "ac_output_power" in coordinator.data:
        entities.append(PowerStationACPowerSensor(coordinator, entry))
    if "dc_output_power" in coordinator.data:
        entities.append(PowerStationDCPowerSensor(coordinator, entry))

    # USB power sensors
    if "usb1_output_power" in coordinator.data:
        entities.append(PowerStationUSBPowerSensor(coordinator, entry, 1))
    if "usb2_output_power" in coordinator.data:
        entities.append(PowerStationUSBPowerSensor(coordinator, entry, 2))
    if "usb3_output_power" in coordinator.data:
        entities.append(PowerStationUSBPowerSensor(coordinator, entry, 3))
    if "usb4_output_power" in coordinator.data:
        entities.append(PowerStationUSBPowerSensor(coordinator, entry, 4))
    if "usb_c1_output_power" in coordinator.data:
        entities.append(PowerStationUSBCPowerSensor(coordinator, entry, 1))
    if "usb_c2_output_power" in coordinator.data:
        entities.append(PowerStationUSBCPowerSensor(coordinator, entry, 2))

    # Other sensors
    if "temp_current" in coordinator.data:
        entities.append(PowerStationTemperatureSensor(coordinator, entry))
    if "ac_voltage_freq" in coordinator.data:
        entities.append(PowerStationFrequencySensor(coordinator, entry))
    if "error_code" in coordinator.data:
        entities.append(PowerStationErrorSensor(coordinator, entry))
    if "input_type" in coordinator.data:
        entities.append(PowerStationInputTypeSensor(coordinator, entry))

    async_add_entities(entities)


class PowerStationSensorBase(CoordinatorEntity, SensorEntity):
    """Базовий клас для датчиків 2E Power Station."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Ініціалізація датчика."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "2E Power Station",
            "manufacturer": "2E",
            "model": "Power Station",
        }


class PowerStationBatterySensor(PowerStationSensorBase):
    """Датчик рівня батареї."""

    _attr_name = "Battery Level"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_battery"

    @property
    def native_value(self) -> int | None:
        """Поточне значення датчика."""
        return self.coordinator.data.get("battery_percentage", 0)


class PowerStationInputPowerSensor(PowerStationSensorBase):
    """Датчик вхідної потужності."""

    _attr_name = "Input Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:transmission-tower-import"

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_input_power"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        power = self.coordinator.data.get("total_input_power", 0)
        return float(power) / 10.0 if power > 1000 else float(power)


class PowerStationOutputPowerSensor(PowerStationSensorBase):
    """Датчик вихідної потужності."""

    _attr_name = "Output Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:transmission-tower-export"

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_output_power"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        power = self.coordinator.data.get("total_output_power", 0)
        return float(power) / 10.0 if power > 1000 else float(power)


class PowerStationACPowerSensor(PowerStationSensorBase):
    """Датчик потужності AC виходу."""

    _attr_name = "AC Output Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:power-plug-outline"

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_ac_power"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        power = self.coordinator.data.get("ac_output_power", 0)
        return float(power) / 10.0 if power > 1000 else float(power)


class PowerStationDCPowerSensor(PowerStationSensorBase):
    """Датчик потужності DC виходу."""

    _attr_name = "DC Output Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:power-plug-outline"

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_dc_power"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        power = self.coordinator.data.get("dc_output_power", 0)
        return float(power) / 10.0 if power > 1000 else float(power)


class PowerStationUSBPowerSensor(PowerStationSensorBase):
    """Датчик потужності USB порту."""

    def __init__(self, coordinator, entry: ConfigEntry, port_num: int) -> None:
        """Ініціалізація датчика."""
        super().__init__(coordinator, entry)
        self._port_num = port_num
        self._attr_name = f"USB{port_num} Output Power"
        self._attr_icon = "mdi:usb-port"

    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_usb{self._port_num}_power"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        power = self.coordinator.data.get(f"usb{self._port_num}_output_power", 0)
        return float(power) / 10.0 if power > 1000 else float(power)


class PowerStationUSBCPowerSensor(PowerStationSensorBase):
    """Датчик потужності USB-C порту."""

    def __init__(self, coordinator, entry: ConfigEntry, port_num: int) -> None:
        """Ініціалізація датчика."""
        super().__init__(coordinator, entry)
        self._port_num = port_num
        self._attr_name = f"USB-C{port_num} Output Power"
        self._attr_icon = "mdi:usb-port"

    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_usbc{self._port_num}_power"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        power = self.coordinator.data.get(f"usb_c{self._port_num}_output_power", 0)
        return float(power) / 10.0 if power > 1000 else float(power)


class PowerStationTemperatureSensor(PowerStationSensorBase):
    """Датчик температури."""

    _attr_name = "Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_temperature"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        temp = self.coordinator.data.get("temp_current", 0)
        return float(temp)


class PowerStationFrequencySensor(PowerStationSensorBase):
    """Датчик частоти AC напруги."""

    _attr_name = "AC Frequency"
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:sine-wave"

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_frequency"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        freq = self.coordinator.data.get("ac_voltage_freq", 0)
        return float(freq)


class PowerStationErrorSensor(PowerStationSensorBase):
    """Датчик коду помилки."""

    _attr_name = "Error Code"
    _attr_icon = "mdi:alert-circle-outline"

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_error_code"

    @property
    def native_value(self) -> str | None:
        """Поточне значення датчика."""
        error = self.coordinator.data.get("error_code", 0)
        return str(error) if error else "No errors"


class PowerStationInputTypeSensor(PowerStationSensorBase):
    """Датчик типу вхідного живлення."""

    _attr_name = "Input Type"
    _attr_icon = "mdi:power-plug"

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_input_type"

    @property
    def native_value(self) -> str | None:
        """Поточне значення датчика."""
        input_type = self.coordinator.data.get("input_type", "unknown")
        return str(input_type)
