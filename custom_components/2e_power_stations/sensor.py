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
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Можливі коди Tuya data points для різних параметрів
# Ці коди можуть відрізнятися залежно від конкретної моделі
BATTERY_CODES = ["battery_percentage", "va_battery", "battery", "battery_value"]
POWER_CODES = ["cur_power", "power", "output_power"]
VOLTAGE_CODES = ["cur_voltage", "voltage"]
CURRENT_CODES = ["cur_current", "current"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Налаштування датчиків з config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        PowerStationBatterySensor(coordinator, entry),
        PowerStationPowerSensor(coordinator, entry),
        PowerStationVoltageSensor(coordinator, entry),
        PowerStationCurrentSensor(coordinator, entry),
    ]

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

    def _get_value_from_codes(self, codes: list[str], default: Any = None) -> Any:
        """Отримати значення з першого знайденого коду."""
        for code in codes:
            value = self.coordinator.data.get(code)
            if value is not None:
                return value
        return default


class PowerStationBatterySensor(PowerStationSensorBase):
    """Датчик рівня батареї."""

    _attr_name = "Рівень батареї"
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
        return self._get_value_from_codes(BATTERY_CODES, 0)


class PowerStationPowerSensor(PowerStationSensorBase):
    """Датчик поточної потужності."""

    _attr_name = "Поточна потужність"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_power"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        power = self._get_value_from_codes(POWER_CODES, 0)
        # Tuya часто повертає потужність в деці-ватах або мілі-ватах
        if power > 10000:
            return power / 10.0
        return float(power)


class PowerStationVoltageSensor(PowerStationSensorBase):
    """Датчик напруги."""

    _attr_name = "Напруга"
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_voltage"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        voltage = self._get_value_from_codes(VOLTAGE_CODES, 0)
        # Tuya часто повертає напругу в деці-вольтах
        if voltage > 1000:
            return voltage / 10.0
        return float(voltage)


class PowerStationCurrentSensor(PowerStationSensorBase):
    """Датчик струму."""

    _attr_name = "Струм"
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Унікальний ID датчика."""
        return f"{self._entry.entry_id}_current"

    @property
    def native_value(self) -> float | None:
        """Поточне значення датчика."""
        current = self._get_value_from_codes(CURRENT_CODES, 0)
        # Tuya часто повертає струм в мілі-амперах
        if current > 100:
            return current / 1000.0
        return float(current)
