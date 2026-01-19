"""Інтеграція 2E Power Stations для Home Assistant через Tuya IoT."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import TwoEPowerStationAPI
from .const import DOMAIN, PLATFORMS
from .coordinator import TwoEPowerStationCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the 2E Power Stations component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Налаштування 2E Power Stations з config entry."""
    _LOGGER.info("Налаштування інтеграції %s", DOMAIN)

    # Створюємо API клієнт з Tuya credentials
    api = await hass.async_add_executor_job(
        TwoEPowerStationAPI,
        entry.data["access_id"],
        entry.data["access_secret"],
        entry.data["device_id"],
        entry.data.get("endpoint", "https://openapi.tuyaeu.com"),
    )

    # Перевіряємо з'єднання
    connection_ok, error_msg = await hass.async_add_executor_job(api.test_connection)
    if not connection_ok:
        api.close()
        raise ConfigEntryNotReady(
            f"Не вдалося з'єднатися з Tuya Cloud для пристрою {entry.data['device_id']}: {error_msg}"
        )

    # Отримуємо інтервал оновлення з options або використовуємо за замовчуванням
    update_interval = entry.options.get("scan_interval", 30)

    # Створюємо координатор для оновлення даних
    coordinator = TwoEPowerStationCoordinator(hass, api, update_interval)

    # Отримуємо початкові дані
    await coordinator.async_config_entry_first_refresh()

    # Зберігаємо координатор в hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Завантажуємо платформи (sensor, switch)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Реєструємо оновлення options
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Вивантаження config entry."""
    _LOGGER.info("Вивантаження інтеграції %s", DOMAIN)

    # Вивантажуємо всі платформи
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Закриваємо API з'єднання
        coordinator = hass.data[DOMAIN][entry.entry_id]
        coordinator.api.close()

        # Видаляємо дані з hass.data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Обробка оновлення options."""
    await hass.config_entries.async_reload(entry.entry_id)
