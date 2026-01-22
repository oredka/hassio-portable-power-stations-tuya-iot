"""Tuya IoT Smart Portable Power Stations for Home Assistant."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import TwoEPowerStationAPI
from .const import DOMAIN, PLATFORMS
from .coordinator import TwoEPowerStationCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Tuya IoT Power Stations component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tuya IoT Power Stations from a config entry."""
    _LOGGER.info("Setting up integration %s", DOMAIN)

    # Create API client with Tuya credentials
    api = await hass.async_add_executor_job(
        TwoEPowerStationAPI,
        entry.data["access_id"],
        entry.data["access_secret"],
        entry.data["device_id"],
        entry.data.get("endpoint", "https://openapi.tuyaeu.com"),
    )

    # Test connection
    connection_ok, error_msg = await hass.async_add_executor_job(api.test_connection)
    if not connection_ok:
        api.close()
        raise ConfigEntryNotReady(
            f"Failed to connect to Tuya Cloud for device {entry.data['device_id']}: {error_msg}"
        )

    # Get update interval from options or use default
    update_interval = entry.options.get("scan_interval", 30)

    # Create coordinator for data updates
    coordinator = TwoEPowerStationCoordinator(hass, api, update_interval)

    # Get initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Load platforms (sensor, switch, etc.)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register options update listener
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # Check for new devices in background
    hass.async_create_task(check_for_new_devices(hass, entry))

    return True


async def check_for_new_devices(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Check for new devices in the same Tuya project."""
    # Wait a bit after startup
    await asyncio.sleep(10)

    try:
        coordinator = hass.data[DOMAIN][entry.entry_id]
        api = coordinator.api

        # Get all devices from project
        all_devices = await hass.async_add_executor_job(api.get_all_devices)
        if not all_devices:
            return

        # Get IDs of already configured devices
        configured_device_ids = {
            e.data.get("device_id") 
            for e in hass.config_entries.async_entries(DOMAIN)
        }

        new_devices = [
            d for d in all_devices 
            if d.get("id") not in configured_device_ids
        ]

        if new_devices:
            _LOGGER.info("Found new Tuya devices: %s", [d.get("id") for d in new_devices])
            for device in new_devices:
                device_id = device.get("id")
                device_name = device.get("name", device_id)
                
                # Create persistent notification for discovered device
                hass.components.persistent_notification.async_create(
                    title="New Tuya IoT Device Detected",
                    message=(
                        f"Found new device '{device_name}' (ID: {device_id}). "
                        "You can add it by going to Settings -> Devices & Services -> Add Integration -> Tuya IoT Smart Portable Power Stations for Home Assistant."
                    ),
                    notification_id=f"tuya_new_device_{device_id}"
                )
    except Exception as err:
        _LOGGER.error("Error checking for new devices: %s", err)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading integration %s", DOMAIN)

    # Unload all platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Close API connection
        coordinator = hass.data[DOMAIN][entry.entry_id]
        coordinator.api.close()

        # Remove from hass.data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
