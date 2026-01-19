"""DataUpdateCoordinator для 2E Power Stations через Tuya IoT."""
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TwoEPowerStationAPI
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class TwoEPowerStationCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Координатор для оновлення даних з 2E Power Station через Tuya."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: TwoEPowerStationAPI,
        update_interval: int = UPDATE_INTERVAL,
    ) -> None:
        """Ініціалізація координатора.

        Args:
            hass: Home Assistant instance
            api: API клієнт для взаємодії з power station
            update_interval: Інтервал оновлення в секундах
        """
        self.api = api

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Отримати оновлені дані з power station.

        Returns:
            Словник з усіма даними про пристрій (всі Tuya data points)

        Raises:
            UpdateFailed: Якщо оновлення не вдалося
        """
        try:
            # Tuya SDK не async, тому виконуємо в executor
            status = await self.hass.async_add_executor_job(
                self.api.get_device_status
            )

            if not status:
                raise UpdateFailed("Отримано порожній статус від пристрою")

            # Логуємо отримані data points для налагодження
            _LOGGER.debug("Отримано статус з Tuya: %s", status)

            # Повертаємо весь статус - він містить всі data points з Tuya
            # Кожен сенсор/перемикач буде брати свій data point
            return status

        except Exception as err:
            _LOGGER.error("Помилка оновлення даних: %s", err)
            raise UpdateFailed(f"Помилка оновлення даних: {err}") from err
