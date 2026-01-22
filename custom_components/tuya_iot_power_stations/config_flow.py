"""Config flow для інтеграції Tuya IoT Power Stations."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .api import TwoEPowerStationAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Можливі Tuya endpoints по регіонах
TUYA_ENDPOINTS = {
    "Європа": "https://openapi.tuyaeu.com",
    "США": "https://openapi.tuyaus.com",
    "Китай": "https://openapi.tuyacn.com",
    "Індія": "https://openapi.tuyain.com",
}

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("access_id"): str,
    vol.Required("access_secret"): str,
    vol.Required("device_id"): str,
    vol.Required("endpoint", default="Європа"): vol.In(list(TUYA_ENDPOINTS.keys())),
})


def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Перевірити введені дані.

    Args:
        hass: Home Assistant instance
        data: Дані від користувача

    Returns:
        Словник з інформацією про підключення

    Raises:
        Exception: Якщо не вдалося підключитися
    """
    # Отримуємо URL endpoint з назви регіону
    endpoint_url = TUYA_ENDPOINTS[data["endpoint"]]

    api = TwoEPowerStationAPI(
        access_id=data["access_id"],
        access_secret=data["access_secret"],
        device_id=data["device_id"],
        endpoint=endpoint_url,
    )

    # Перевіряємо з'єднання
    success, error_msg = api.test_connection()
    if not success:
        raise Exception(error_msg or "Failed to connect to Tuya Cloud")

    # Отримуємо інформацію про пристрій
    device_info = api.get_device_info()

    return {
        "title": device_info.get("name", f"Power Station ({data['device_id'][:8]})"),
        "device_info": device_info,
        "endpoint": endpoint_url,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow для Tuya IoT Power Stations."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Обробка користувацького введення."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Перевіряємо введені дані в executor (Tuya SDK не async)
                info = await self.hass.async_add_executor_job(
                    validate_input, self.hass, user_input
                )

                # Перевіряємо, чи не налаштований вже цей пристрій
                await self.async_set_unique_id(user_input["device_id"])
                self._abort_if_unique_id_configured()

                # Зберігаємо endpoint URL замість назви регіону
                user_input["endpoint"] = info["endpoint"]

                # Створюємо entry
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )
            except PermissionError as err:
                _LOGGER.error("Permission error: %s", err)
                errors["base"] = "permission_denied"
            except Exception as err:
                _LOGGER.error("Setup error: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "setup_info": "1. Зареєструйтесь на https://iot.tuya.com\n2. Створіть Cloud Project\n3. Підключіть API: Industry Solutions -> Smart Home\n4. Додайте пристрій до проєкту\n5. Скопіюйте Access ID, Access Secret та Device ID"
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Отримати options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Обробка налаштувань."""

    def __init__(self, config_entry):
        """Ініціалізація options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Управління налаштуваннями."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "scan_interval",
                    default=self.config_entry.options.get("scan_interval", 30),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
            }),
        )
