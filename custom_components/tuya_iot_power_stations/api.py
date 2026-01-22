"""API клієнт для Tuya IoT Power Stations."""
import logging
from typing import Any

from tuya_connector import TuyaOpenAPI

_LOGGER = logging.getLogger(__name__)


class TwoEPowerStationAPI:
    """Клас для взаємодії з Tuya IoT Power Station через Tuya Cloud API."""

    def __init__(
        self,
        access_id: str,
        access_secret: str,
        device_id: str,
        endpoint: str = "https://openapi.tuyaeu.com",
    ) -> None:
        """Ініціалізація API клієнта.

        Args:
            access_id: Tuya Cloud Access ID
            access_secret: Tuya Cloud Access Secret
            device_id: ID пристрою в Tuya Cloud
            endpoint: Tuya Cloud API endpoint (за замовчуванням EU)
        """
        self.device_id = device_id
        self.access_id = access_id
        self.access_secret = access_secret
        self.endpoint = endpoint

        # Використовуємо офіційний tuya-connector-python SDK
        self.api = TuyaOpenAPI(endpoint, access_id, access_secret)
        self.api.connect()
        _LOGGER.debug("Tuya API initialized - Endpoint: %s", endpoint)

    def close(self) -> None:
        """Закрити з'єднання."""
        # Tuya SDK не потребує явного закриття

    def get_device_status(self) -> dict[str, Any]:
        """Отримати статус пристрою.

        Returns:
            Словник зі статусом всіх data points
        """
        response = self.api.get(f"/v1.0/devices/{self.device_id}/status")
        if not response.get("success"):
            error_msg = response.get("msg", "Unknown error")
            if "device is offline" in error_msg.lower() or response.get("code") == 2001:
                _LOGGER.warning("Пристрій офлайн: %s", error_msg)
            else:
                _LOGGER.error("Помилка отримання статусу: %s", response)
            return {}

        # Конвертуємо список status в словник
        return {item["code"]: item["value"] for item in response.get("result", [])}

    def get_device_info(self) -> dict[str, Any]:
        """Отримати інформацію про пристрій.

        Returns:
            Словник з інформацією про пристрій

        Raises:
            PermissionError: Якщо немає доступу до пристрою (код 1106)
            ConnectionError: Якщо інша помилка підключення
        """
        response = self.api.get(f"/v1.0/devices/{self.device_id}")
        _LOGGER.debug("Device info response: %s", response)

        if response.get("success"):
            return response.get("result", {})

        error_code = response.get("code")
        error_msg = response.get("msg", "Unknown error")

        if error_code == 1106:
            _LOGGER.error(
                "Permission denied (1106) for device %s. "
                "Please ensure the device is linked to your Cloud Project via App Account authorization.",
                self.device_id
            )
            raise PermissionError(
                f"Permission denied for device {self.device_id}. "
                "Device must be authorized in Tuya IoT Platform via App Account."
            )

        _LOGGER.error("Error getting device info: %s", response)
        raise ConnectionError(f"Failed to get device info: {error_msg} (code: {error_code})")

    def send_command(self, code: str, value: Any) -> bool:
        """Відправити команду пристрою.

        Args:
            code: Код команди (data point)
            value: Значення команди

        Returns:
            True якщо команда успішна
        """
        commands = {"commands": [{"code": code, "value": value}]}
        response = self.api.post(f"/v1.0/devices/{self.device_id}/commands", commands)

        success = response.get("success", False)
        if not success:
            error_msg = response.get("msg", "Unknown error")
            if "device is offline" in error_msg.lower() or response.get("code") == 2001:
                _LOGGER.warning("Не вдалося відправити команду %s (пристрій офлайн): %s", code, error_msg)
            else:
                _LOGGER.error("Помилка відправки команди %s: %s", code, response)

        return success


    def test_connection(self) -> tuple[bool, str]:
        """Перевірити з'єднання з Tuya Cloud.

        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            info = self.get_device_info()
            return (True, "")
        except PermissionError as err:
            error_msg = (
                "Permission denied. Please authorize your device:\n"
                "1. Go to Tuya IoT Platform\n"
                "2. Cloud → Development → Link Tuya App Account\n"
                "3. Add your device using Smart Life app credentials\n"
                "4. Ensure device is visible in 'Devices' tab"
            )
            _LOGGER.error("Permission error: %s", err)
            return (False, error_msg)
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return (False, str(err))
