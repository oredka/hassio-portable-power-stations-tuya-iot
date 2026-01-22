"""Select entities for Tuya IoT Power Stations."""
import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# LED mode options based on Tuya Standard Instruction Set
LED_MODE_OPTIONS = {
    "lamp_off": "Off",
    "lamp_100": "High Light",
    "lamp_flash": "Strobe",
    "lamp_50": "Half Bright",
    "lamp_30": "Low",
    "lamp_sos": "SOS",
}

# Timer options for AC/DC/LED auto-off - based on Tuya device specifications
AC_OFF_TIME_OPTIONS = {
    "2hour": "2 Hours",
    "4hour": "4 Hours",
    "8hour": "8 Hours",
    "12hour": "12 Hours",
    "do_not_close": "Never",
}

DC_OFF_TIME_OPTIONS = {
    "2hour": "2 Hours",
    "4hour": "4 Hours",
    "8hour": "8 Hours",
    "12hour": "12 Hours",
    "do_not_close": "Never",
}

LED_OFF_TIME_OPTIONS = {
    "2hour": "2 Hours",
    "4hour": "4 Hours",
    "8hour": "8 Hours",
    "12hour": "12 Hours",
    "do_not_close": "Never",
}

STANDBY_TIME_OPTIONS = {
    "3min": "3 Minutes",
    "5min": "5 Minutes",
    "15min": "15 Minutes",
    "60min": "60 Minutes",
    "do_not_close": "Never",
}

DISPLAY_OFF_TIME_OPTIONS = {
    "2min": "2 Minutes",
    "5min": "5 Minutes",
    "10min": "10 Minutes",
    "20min": "20 Minutes",
    "do_not_close": "Never",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # LED Mode
    if "led_mode" in coordinator.data:
        entities.append(PowerStationLEDModeSelect(coordinator, entry))

    # Timer settings - Send & report type, should be writable
    # Currently getting error 2008, need to verify correct enum values from Tuya platform
    if "ac_off_time_set" in coordinator.data:
        entities.append(PowerStationACOffTimeSelect(coordinator, entry))
    if "dc_off_time_set" in coordinator.data:
        entities.append(PowerStationDCOffTimeSelect(coordinator, entry))
    if "led_off_time_set" in coordinator.data:
        entities.append(PowerStationLEDOffTimeSelect(coordinator, entry))
    if "device_standby_time_set" in coordinator.data:
        entities.append(PowerStationStandbyTimeSelect(coordinator, entry))
    if "display_off_time_set" in coordinator.data:
        entities.append(PowerStationDisplayOffTimeSelect(coordinator, entry))

    if entities:
        async_add_entities(entities)


class PowerStationSelectBase(CoordinatorEntity, SelectEntity):
    """Base class for Tuya IoT Power Station select entities."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize select entity."""
        super().__init__(coordinator)
        self._entry = entry
        
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
            self.entity_id = f"select.{device_name.lower().replace(' ', '_')}_{self._attr_name.split(' ', 1)[1].lower().replace(' ', '_')}"


class PowerStationLEDModeSelect(PowerStationSelectBase):
    """LED Mode selector."""

    _attr_name = "LED Mode"
    _attr_icon = "mdi:lightbulb-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize LED mode select."""
        super().__init__(coordinator, entry)
        self._attr_options = list(LED_MODE_OPTIONS.values())
        self._dp_code = "led_mode"
        self._options_map = LED_MODE_OPTIONS

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_led_mode_select"

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        current_value = self.coordinator.data.get(self._dp_code)
        if current_value in self._options_map:
            return self._options_map[current_value]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        tuya_value = None
        for key, value in self._options_map.items():
            if value == option:
                tuya_value = key
                break

        if tuya_value:
            success = await self.hass.async_add_executor_job(
                self.coordinator.api.send_command, self._dp_code, tuya_value
            )
            if not success:
                _LOGGER.error("Failed to set LED Mode to %s", option)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Could not find Tuya value for option: %s", option)


class PowerStationACOffTimeSelect(PowerStationSelectBase):
    """AC Auto-Off Time selector."""

    _attr_name = "AC Auto-Off Time"
    _attr_icon = "mdi:timer-off-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize selector."""
        super().__init__(coordinator, entry)
        self._attr_options = list(AC_OFF_TIME_OPTIONS.values())
        self._dp_code = "ac_off_time_set"
        self._options_map = AC_OFF_TIME_OPTIONS

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_ac_off_time"

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        current_value = self.coordinator.data.get(self._dp_code)
        if current_value in self._options_map:
            return self._options_map[current_value]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        tuya_value = None
        for key, value in self._options_map.items():
            if value == option:
                tuya_value = key
                break

        if tuya_value:
            await self.hass.async_add_executor_job(
                self.coordinator.api.send_command, self._dp_code, tuya_value
            )
            await self.coordinator.async_request_refresh()


class PowerStationDCOffTimeSelect(PowerStationSelectBase):
    """DC Auto-Off Time selector."""

    _attr_name = "DC Auto-Off Time"
    _attr_icon = "mdi:timer-off-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize selector."""
        super().__init__(coordinator, entry)
        self._attr_options = list(DC_OFF_TIME_OPTIONS.values())
        self._dp_code = "dc_off_time_set"
        self._options_map = DC_OFF_TIME_OPTIONS

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_dc_off_time"

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        current_value = self.coordinator.data.get(self._dp_code)
        if current_value in self._options_map:
            return self._options_map[current_value]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        tuya_value = None
        for key, value in self._options_map.items():
            if value == option:
                tuya_value = key
                break

        if tuya_value:
            await self.hass.async_add_executor_job(
                self.coordinator.api.send_command, self._dp_code, tuya_value
            )
            await self.coordinator.async_request_refresh()


class PowerStationLEDOffTimeSelect(PowerStationSelectBase):
    """LED Auto-Off Time selector."""

    _attr_name = "LED Auto-Off Time"
    _attr_icon = "mdi:timer-off-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize selector."""
        super().__init__(coordinator, entry)
        self._attr_options = list(LED_OFF_TIME_OPTIONS.values())
        self._dp_code = "led_off_time_set"
        self._options_map = LED_OFF_TIME_OPTIONS

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_led_off_time"

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        current_value = self.coordinator.data.get(self._dp_code)
        if current_value in self._options_map:
            return self._options_map[current_value]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        tuya_value = None
        for key, value in self._options_map.items():
            if value == option:
                tuya_value = key
                break

        if tuya_value:
            await self.hass.async_add_executor_job(
                self.coordinator.api.send_command, self._dp_code, tuya_value
            )
            await self.coordinator.async_request_refresh()


class PowerStationStandbyTimeSelect(PowerStationSelectBase):
    """Device Standby Time selector."""

    _attr_name = "Standby Time"
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize selector."""
        super().__init__(coordinator, entry)
        self._attr_options = list(STANDBY_TIME_OPTIONS.values())
        self._dp_code = "device_standby_time_set"
        self._options_map = STANDBY_TIME_OPTIONS

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_standby_time"

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        current_value = self.coordinator.data.get(self._dp_code)
        if current_value in self._options_map:
            return self._options_map[current_value]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        tuya_value = None
        for key, value in self._options_map.items():
            if value == option:
                tuya_value = key
                break

        if tuya_value:
            await self.hass.async_add_executor_job(
                self.coordinator.api.send_command, self._dp_code, tuya_value
            )
            await self.coordinator.async_request_refresh()


class PowerStationDisplayOffTimeSelect(PowerStationSelectBase):
    """Display Auto-Off Time selector."""

    _attr_name = "Display Auto-Off Time"
    _attr_icon = "mdi:monitor-off"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize selector."""
        super().__init__(coordinator, entry)
        self._attr_options = list(DISPLAY_OFF_TIME_OPTIONS.values())
        self._dp_code = "display_off_time_set"
        self._options_map = DISPLAY_OFF_TIME_OPTIONS

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_display_off_time"

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        current_value = self.coordinator.data.get(self._dp_code)
        if current_value in self._options_map:
            return self._options_map[current_value]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        tuya_value = None
        for key, value in self._options_map.items():
            if value == option:
                tuya_value = key
                break

        if tuya_value:
            await self.hass.async_add_executor_job(
                self.coordinator.api.send_command, self._dp_code, tuya_value
            )
            await self.coordinator.async_request_refresh()
