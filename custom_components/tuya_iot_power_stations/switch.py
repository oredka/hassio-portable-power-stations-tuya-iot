"""Switches for Tuya IoT Power Stations."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up switches from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # Output switches
    if "switch_ac" in coordinator.data:
        entities.append(PowerStationACOutputSwitch(coordinator, entry))
    if "switch_dc" in coordinator.data:
        entities.append(PowerStationDCOutputSwitch(coordinator, entry))
    if "switch_usb" in coordinator.data:
        entities.append(PowerStationUSBOutputSwitch(coordinator, entry))

    # Feature switches
    if "switch_buzzer" in coordinator.data:
        entities.append(PowerStationBuzzerSwitch(coordinator, entry))

    if entities:
        async_add_entities(entities)
    else:
        _LOGGER.warning("No switches found in device data")


class PowerStationSwitchBase(CoordinatorEntity, SwitchEntity):
    """Base class for Tuya IoT Power Station switches."""

    def __init__(self, coordinator, entry: ConfigEntry, switch_code: str) -> None:
        """Initialize switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._switch_code = switch_code
        
        # Get device name from entry title
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
            self.entity_id = f"switch.{device_name.lower().replace(' ', '_')}_{self._attr_name.split(' ', 1)[1].lower().replace(' ', '_')}"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.data.get(self._switch_code, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.send_command, self._switch_code, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.send_command, self._switch_code, False
        )
        await self.coordinator.async_request_refresh()


class PowerStationACOutputSwitch(PowerStationSwitchBase):
    """AC output switch."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize switch."""
        super().__init__(coordinator, entry, "switch_ac")
        self._attr_name = "AC Enabled"
        self._attr_icon = "mdi:power-socket-eu"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_ac_output"


class PowerStationDCOutputSwitch(PowerStationSwitchBase):
    """DC output switch."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize switch."""
        super().__init__(coordinator, entry, "switch_dc")
        self._attr_name = "DC (12V) Enabled"
        self._attr_icon = "mdi:power-plug-outline"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_dc_output"


class PowerStationUSBOutputSwitch(PowerStationSwitchBase):
    """USB output switch."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize switch."""
        super().__init__(coordinator, entry, "switch_usb")
        self._attr_name = "USB Enabled"
        self._attr_icon = "mdi:usb-port"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_usb_output"


class PowerStationBuzzerSwitch(PowerStationSwitchBase):
    """Buzzer switch."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize switch."""
        super().__init__(coordinator, entry, "switch_buzzer")
        self._attr_name = "Beeper"
        self._attr_icon = "mdi:volume-high"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_buzzer"
