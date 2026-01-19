"""API клієнт для 2E Power Stations через Tuya IoT."""
import logging
from typing import Any

from tuya_iot import TuyaOpenAPI, TuyaDeviceManager, AuthType

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

        # Ініціалізація Tuya API
        self.api = TuyaOpenAPI(endpoint, access_id, access_secret, AuthType.CUSTOM)
        self.api.connect()

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
        """
        response = self.api.get(f"/v1.0/devices/{self.device_id}")
        if response.get("success"):
            return response.get("result", {})
        else:
            _LOGGER.error("Помилка отримання інформації про пристрій: %s", response)
            return {}

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

    def test_connection(self) -> bool:
        """Перевірити з'єднання з Tuya Cloud.

        Returns:
            True якщо з'єднання успішне
        """
        try:
            info = self.get_device_info()
            return bool(info)
        except Exception as err:
            _LOGGER.error("Помилка перевірки з'єднання: %s", err)
            return False
