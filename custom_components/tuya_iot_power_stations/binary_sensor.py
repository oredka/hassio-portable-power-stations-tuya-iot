"""Binary sensors for Tuya IoT Power Stations (2E Syayvo)."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
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
    """Set up binary sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    if "switch_usb" in coordinator.data:
        entities.append(PowerStationUSBStatusSensor(coordinator, entry))

    if entities:
        async_add_entities(entities)


class PowerStationBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for Tuya IoT Power Station binary sensors."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "2E Syayvo",
            "manufacturer": "2E",
            "model": "Power Station",
        }


class PowerStationUSBStatusSensor(PowerStationBinarySensorBase):
    """USB Output Status binary sensor."""

    _attr_name = "USB Output Status"
    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_icon = "mdi:usb-port"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_usb_status"

    @property
    def is_on(self) -> bool:
        """Return true if USB output is active."""
        return self.coordinator.data.get("switch_usb", False)
