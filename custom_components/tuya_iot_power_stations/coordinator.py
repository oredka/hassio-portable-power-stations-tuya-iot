"""DataUpdateCoordinator for Tuya IoT Power Stations."""
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TwoEPowerStationAPI
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class TwoEPowerStationCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to update data from Tuya IoT Power Station."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: TwoEPowerStationAPI,
        update_interval: int = UPDATE_INTERVAL,
    ) -> None:
        """Initialize coordinator.

        Args:
            hass: Home Assistant instance
            api: API client to interact with power station
            update_interval: Update interval in seconds
        """
        self.api = api

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch updated data from power station.

        Returns:
            Dictionary with all device data (all Tuya data points)

        Raises:
            UpdateFailed: If update fails
        """
        try:
            # Tuya SDK is not async, so we run in executor
            status = await self.hass.async_add_executor_job(
                self.api.get_device_status
            )

            if not status:
                # API returns {} if device is offline or there is an error
                # This is already logged in api.py
                raise UpdateFailed("Received empty status from device")

            # Log received data points for debugging
            _LOGGER.debug("Received status from Tuya: %s", status)

            # Return the entire status - it contains all data points from Tuya
            # Each sensor/switch will take its own data point
            return status

        except UpdateFailed:
            raise
        except Exception as err:
            if "device is offline" in str(err).lower():
                _LOGGER.warning("Device offline during update: %s", err)
            else:
                _LOGGER.error("Error updating data: %s", err)
            raise UpdateFailed(f"Error updating data: {err}") from err
