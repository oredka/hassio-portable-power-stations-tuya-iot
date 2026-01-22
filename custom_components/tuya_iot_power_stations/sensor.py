"""Sensors for Tuya IoT Power Stations."""
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
    """Set up sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Base sensors - always add
    entities = [
        PowerStationBatteryLevelSensor(coordinator, entry),
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

    # Battery power sensor (positive = discharge, negative = charge)
    # This sensor is used for Energy Dashboard
    if "total_input_power" in coordinator.data or "total_output_power" in coordinator.data:
        entities.append(PowerStationBatteryPowerSensor(coordinator, entry))

    # Energy sensors
    if "charge_energy" in coordinator.data:
        entities.append(PowerStationChargeEnergySensor(coordinator, entry))
    if "discharge_energy" in coordinator.data:
        entities.append(PowerStationDischargeEnergySensor(coordinator, entry))

    # Add Power-to-Energy integration sensors (helpers) if real energy sensors are missing
    # Note: This usually requires user to add them in HA UI, 
    # but we can provide the base power sensors with correct attributes.

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
    """Base class for Tuya IoT Power Station sensors."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._entry = entry
        
        # Get device name from entry title or coordinator data if available
        device_name = entry.title
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "Tuya",
            "model": "Portable Power Station",
        }
        
        # Set entity name to include device name for better identification
        if hasattr(self, "_attr_name") and self._attr_name:
            self._attr_name = f"{device_name} {self._attr_name}"
            # Ensure entity_id is generated from the name including device name
            self.entity_id = f"sensor.{device_name.lower().replace(' ', '_')}_{self._attr_name.split(' ', 1)[1].lower().replace(' ', '_')}"


class PowerStationBatteryLevelSensor(PowerStationSensorBase):
    """Battery level sensor."""

    _attr_name = "Battery Level"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_battery"

    @property
    def native_value(self) -> int | None:
        """Current value of sensor."""
        return self.coordinator.data.get("battery_percentage", 0)


class PowerStationInputPowerSensor(PowerStationSensorBase):
    """Input power sensor."""

    _attr_name = "Total In Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:transmission-tower-import"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_input_power"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor."""
        power = self.coordinator.data.get("total_input_power", 0)
        return float(power)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {"last_reset": "1970-01-01T00:00:00+00:00"}


class PowerStationOutputPowerSensor(PowerStationSensorBase):
    """Output power sensor."""

    _attr_name = "Total Out Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:transmission-tower-export"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_output_power"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor."""
        power = self.coordinator.data.get("total_output_power", 0)
        return float(power)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {"last_reset": "1970-01-01T00:00:00+00:00"}


class PowerStationACPowerSensor(PowerStationSensorBase):
    """AC output power sensor."""

    _attr_name = "AC Out Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:power-plug-outline"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_ac_power"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor."""
        power = self.coordinator.data.get("ac_output_power", 0)
        return float(power)


class PowerStationDCPowerSensor(PowerStationSensorBase):
    """DC output power sensor."""

    _attr_name = "DC Out Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:power-plug-outline"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_dc_power"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor."""
        power = self.coordinator.data.get("dc_output_power", 0)
        return float(power)


class PowerStationUSBPowerSensor(PowerStationSensorBase):
    """USB port power sensor."""

    def __init__(self, coordinator, entry: ConfigEntry, port_num: int) -> None:
        """Initialize sensor."""
        self._attr_name = f"USB{port_num} Out Power"
        super().__init__(coordinator, entry)
        self._port_num = port_num
        self._attr_icon = "mdi:usb-port"

    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_usb{self._port_num}_power"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor."""
        power = self.coordinator.data.get(f"usb{self._port_num}_output_power", 0)
        return float(power)


class PowerStationUSBCPowerSensor(PowerStationSensorBase):
    """USB-C port power sensor."""

    def __init__(self, coordinator, entry: ConfigEntry, port_num: int) -> None:
        """Initialize sensor."""
        self._attr_name = f"USB-C{port_num} Out Power"
        super().__init__(coordinator, entry)
        self._port_num = port_num
        self._attr_icon = "mdi:usb-port"

    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_usbc{self._port_num}_power"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor."""
        power = self.coordinator.data.get(f"usb_c{self._port_num}_output_power", 0)
        return float(power)


class PowerStationTemperatureSensor(PowerStationSensorBase):
    """Temperature sensor."""

    _attr_name = "Battery Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_temperature"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor."""
        temp = self.coordinator.data.get("temp_current", 0)
        return float(temp)


class PowerStationFrequencySensor(PowerStationSensorBase):
    """AC voltage and frequency sensor."""

    _attr_name = "AC Voltage/Frequency"
    _attr_icon = "mdi:sine-wave"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_ac_voltage_freq"

    @property
    def native_value(self) -> str | None:
        """Current value of sensor."""
        freq = self.coordinator.data.get("ac_voltage_freq", "Unknown")
        return str(freq)


class PowerStationErrorSensor(PowerStationSensorBase):
    """Error code sensor."""

    _attr_name = "Error Code"
    _attr_icon = "mdi:alert-circle-outline"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_error_code"

    @property
    def native_value(self) -> str | None:
        """Current value of sensor."""
        error = self.coordinator.data.get("error_code", 0)
        return str(error) if error else "No errors"


class PowerStationInputTypeSensor(PowerStationSensorBase):
    """Input power type sensor."""

    _attr_name = "Input Type"
    _attr_icon = "mdi:power-plug"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_input_type"

    @property
    def native_value(self) -> str | None:
        """Current value of sensor."""
        input_type = self.coordinator.data.get("input_type", "unknown")
        return str(input_type)


class PowerStationChargeEnergySensor(PowerStationSensorBase):
    """Battery charge energy sensor (for Energy Dashboard)."""

    _attr_name = "Battery Charge Energy"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:battery-charging"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_charge_energy"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor in kWh."""
        energy = self.coordinator.data.get("charge_energy", 0)
        # Convert Wh to kWh if needed
        return float(energy) / 1000.0 if energy > 100 else float(energy)


class PowerStationDischargeEnergySensor(PowerStationSensorBase):
    """Battery discharge energy sensor (for Energy Dashboard)."""

    _attr_name = "Battery Discharge Energy"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:battery-minus"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_discharge_energy"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor in kWh."""
        energy = self.coordinator.data.get("discharge_energy", 0)
        # Convert Wh to kWh if needed
        return float(energy) / 1000.0 if energy > 100 else float(energy)


class PowerStationBatteryPowerSensor(PowerStationSensorBase):
    """Battery power sensor (for Energy Dashboard).

    Positive value = battery discharge (output)
    Negative value = battery charge (input)
    """

    _attr_name = "Battery Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:battery-arrow-down-outline"

    @property
    def unique_id(self) -> str:
        """Unique ID for sensor."""
        return f"{self._entry.entry_id}_battery_power"

    @property
    def native_value(self) -> float | None:
        """Current value of sensor in Watts.

        Positive = discharge, negative = charge
        """
        output_power = self.coordinator.data.get("total_output_power", 0)
        input_power = self.coordinator.data.get("total_input_power", 0)

        # Discharge (positive) - charge (negative)
        return float(output_power) - float(input_power)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {"last_reset": "1970-01-01T00:00:00+00:00"}


# Timer sensors (read-only) - cannot be changed via Tuya API
class PowerStationACOffTimeSensor(PowerStationSensorBase):
    """AC Auto-Off Timer sensor (read-only)."""

    _attr_name = "AC Auto-Off Time"
    _attr_icon = "mdi:timer-off-outline"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_ac_off_time"
