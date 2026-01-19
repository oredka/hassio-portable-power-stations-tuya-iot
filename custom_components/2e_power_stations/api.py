"""API клієнт для 2E Power Stations через Tuya IoT."""
import hashlib
import hmac
import json
import logging
import time
from typing import Any

import requests

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
        self.token = None
        self.token_expire = 0

        _LOGGER.debug("Initialized Tuya API client - Endpoint: %s", endpoint)

    def _get_token(self) -> str:
        """Отримати access token з кешуванням."""
        current_time = int(time.time() * 1000)

        # Якщо токен ще валідний, використовуємо його
        if self.token and current_time < self.token_expire:
            return self.token

        # Отримуємо новий токен
        timestamp = str(current_time)

        # Для Easy IoT API без токена: client_id + t
        string_to_sign = f"{self.access_id}{timestamp}"

        signature = hmac.new(
            self.access_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().lower()

        headers = {
            "client_id": self.access_id,
            "sign": signature,
            "t": timestamp,
            "sign_method": "HMAC-SHA256",
        }

        _LOGGER.debug("Getting token - string_to_sign=%s, signature=%s", string_to_sign, signature[:16] + "...")
        _LOGGER.debug("Headers: %s", {**headers, "sign": signature[:16] + "..."})

        url = f"{self.endpoint}/v1.0/token?grant_type=1"
        response = requests.get(url, headers=headers)
        result = response.json()

        _LOGGER.debug("Token response: %s", result)

        if not result.get("success"):
            _LOGGER.error("Failed to get token: %s", result)
            _LOGGER.error("Make sure Access ID and Access Secret are correct from Tuya IoT Platform")
            raise Exception(f"Failed to get token: {result}")

        self.token = result["result"]["access_token"]
        # Токен валідний 2 години, оновлюємо за 5 хвилин до закінчення
        self.token_expire = current_time + (result["result"]["expire_time"] - 300) * 1000

        _LOGGER.debug("Token obtained successfully, expires in %s seconds", result["result"]["expire_time"])
        return self.token

    def _make_request(self, method: str, path: str, body: dict = None) -> dict:
        """Виконати API запит з правильним підписом."""
        token = self._get_token()
        timestamp = str(int(time.time() * 1000))

        # Формуємо рядок для підпису
        body_str = json.dumps(body) if body else ""
        string_to_sign = f"{self.access_id}{token}{timestamp}{method.upper()}\n\n{body_str}\n{path}"

        signature = hmac.new(
            self.access_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().lower()

        headers = {
            "client_id": self.access_id,
            "access_token": token,
            "sign": signature,
            "t": timestamp,
            "sign_method": "HMAC-SHA256",
            "Content-Type": "application/json",
        }

        url = f"{self.endpoint}{path}"

        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=body)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return response.json()

    async def close(self) -> None:
        """Закрити з'єднання."""
        # Tuya SDK не потребує явного закриття
        pass

    def get_device_status(self) -> dict[str, Any]:
        """Отримати статус пристрою.

        Returns:
            Словник зі статусом всіх data points
        """
        response = self._make_request("GET", f"/v1.0/devices/{self.device_id}/status")
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
        _LOGGER.debug("Requesting device info for device_id: %s", self.device_id)
        response = self._make_request("GET", f"/v1.0/devices/{self.device_id}")
        _LOGGER.debug("Device info response: %s", response)

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
        response = self._make_request(
            "POST",
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
