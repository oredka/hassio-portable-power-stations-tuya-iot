"""API клієнт для 2E Power Stations через Tuya IoT."""
import logging
from typing import Any

from tuya_connector import TuyaOpenAPI

_LOGGER = logging.getLogger(__name__)


class TwoEPowerStationAPI:
    """Клас для взаємодії з 2E Power Station через Tuya Cloud API."""

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

        _LOGGER.debug("Initializing Tuya Connector API - Endpoint: %s", endpoint)
        # Використовуємо офіційний tuya-connector-python SDK
        self.api = TuyaOpenAPI(endpoint, access_id, access_secret)
        self.api.connect()
        _LOGGER.debug("Tuya API initialized and connected")

    async def close(self) -> None:
        """Закрити з'єднання."""
        # Tuya SDK не потребує явного закриття
        pass

    def get_device_status(self) -> dict[str, Any]:
        """Отримати статус пристрою.

        Returns:
            Словник зі статусом всіх data points
        """
        response = self.api.get(f"/v1.0/devices/{self.device_id}/status")
        if response.get("success"):
            # Конвертуємо список status в словник
            status_dict = {}
            for item in response.get("result", []):
                status_dict[item["code"]] = item["value"]
            return status_dict
        else:
            _LOGGER.error("Помилка отримання статусу: %s", response)
            return {}

    def get_device_info(self) -> dict[str, Any]:
        """Отримати інформацію про пристрій.

        Returns:
            Словник з інформацією про пристрій

        Raises:
            PermissionError: Якщо немає доступу до пристрою (код 1106)
            ConnectionError: Якщо інша помилка підключення
        """
        _LOGGER.debug("Requesting device info for device_id: %s", self.device_id)
        response = self.api.get(f"/v1.0/devices/{self.device_id}")
        _LOGGER.debug("Device info response: %s", response)

        if response.get("success"):
            return response.get("result", {})
        else:
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
        response = self.api.post(
            f"/v1.0/devices/{self.device_id}/commands",
            commands
        )

        success = response.get("success", False)
        if not success:
            _LOGGER.error("Помилка відправки команди %s: %s", code, response)

        return success

    def get_battery_level(self) -> int:
        """Отримати рівень батареї у відсотках."""
        status = self.get_device_status()
        # Звичайні коди для рівня батареї в Tuya
        return status.get("battery_percentage", status.get("va_battery", 0))

    def get_power_output(self) -> float:
        """Отримати поточну вихідну потужність у ватах."""
        status = self.get_device_status()
        # Можливі коди для потужності
        return status.get("cur_power", status.get("power", 0))

    def get_voltage(self) -> float:
        """Отримати напругу у вольтах."""
        status = self.get_device_status()
        voltage = status.get("cur_voltage", status.get("voltage", 0))
        # Часто Tuya повертає напругу в деці-вольтах
        return voltage / 10.0 if voltage > 100 else voltage

    def get_current(self) -> float:
        """Отримати струм в амперах."""
        status = self.get_device_status()
        current = status.get("cur_current", status.get("current", 0))
        # Часто Tuya повертає струм в мілі-амперах
        return current / 1000.0 if current > 100 else current

    def set_switch(self, switch_code: str, state: bool) -> bool:
        """Увімкнути/вимкнути вихід.

        Args:
            switch_code: Код перемикача (наприклад "switch_1", "switch_usb")
            state: True для увімкнення, False для вимкнення

        Returns:
            True якщо команда успішна
        """
        return self.send_command(switch_code, state)

    def is_switch_on(self, switch_code: str) -> bool:
        """Перевірити чи увімкнений перемикач."""
        status = self.get_device_status()
        return status.get(switch_code, False)

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
