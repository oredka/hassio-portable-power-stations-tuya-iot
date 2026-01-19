"""Select entities for 2E Power Stations via Tuya IoT."""
import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# LED mode options based on Tuya DP enum values
LED_MODE_OPTIONS = {
    "lamp_off": "Off",
    "lamp_10": "10%",
    "lamp_30": "30%",
    "lamp_50": "50%",
    "lamp_100": "100%",
    "lamp_breath": "Breathing",
    "lamp_sos": "SOS",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    if "led_mode" in coordinator.data:
        entities.append(PowerStationLEDModeSelect(coordinator, entry))

    if entities:
        async_add_entities(entities)


class PowerStationSelectBase(CoordinatorEntity, SelectEntity):
    """Base class for 2E Power Station select entities."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize select entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "2E Power Station",
            "manufacturer": "2E",
            "model": "Power Station",
        }


class PowerStationLEDModeSelect(PowerStationSelectBase):
    """LED Mode selector."""

    _attr_name = "LED Mode"
    _attr_icon = "mdi:lightbulb-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize LED mode select."""
        super().__init__(coordinator, entry)
        # Set available options from the enum mapping
        self._attr_options = list(LED_MODE_OPTIONS.values())

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_led_mode_select"

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        current_value = self.coordinator.data.get("led_mode")
        if current_value in LED_MODE_OPTIONS:
            return LED_MODE_OPTIONS[current_value]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the key for the selected value
        tuya_value = None
        for key, value in LED_MODE_OPTIONS.items():
            if value == option:
                tuya_value = key
                break

        if tuya_value:
            await self.hass.async_add_executor_job(
                self.coordinator.api.send_command, "led_mode", tuya_value
            )
            await self.coordinator.async_request_refresh()
