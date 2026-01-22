"""API client for Tuya IoT Power Stations."""
import logging
from typing import Any

from tuya_connector import TuyaOpenAPI

_LOGGER = logging.getLogger(__name__)


class TwoEPowerStationAPI:
    """Class to interact with Tuya IoT Power Station via Tuya Cloud API."""

    def __init__(
        self,
        access_id: str,
        access_secret: str,
        device_id: str,
        endpoint: str = "https://openapi.tuyaeu.com",
    ) -> None:
        """Initialize API client.

        Args:
            access_id: Tuya Cloud Access ID
            access_secret: Tuya Cloud Access Secret
            device_id: Device ID in Tuya Cloud
            endpoint: Tuya Cloud API endpoint (default EU)
        """
        self.device_id = device_id
        self.access_id = access_id
        self.access_secret = access_secret
        self.endpoint = endpoint

        # Use official tuya-connector-python SDK
        self.api = TuyaOpenAPI(endpoint, access_id, access_secret)
        self.api.connect()
        _LOGGER.debug("Tuya API initialized - Endpoint: %s", endpoint)

    def close(self) -> None:
        """Close connection."""
        # Tuya SDK does not require explicit closing

    def get_device_status(self) -> dict[str, Any]:
        """Get device status.

        Returns:
            Dictionary with status of all data points
        """
        response = self.api.get(f"/v1.0/devices/{self.device_id}/status")
        if not response.get("success"):
            error_msg = response.get("msg", "Unknown error")
            if "device is offline" in error_msg.lower() or response.get("code") == 2001:
                _LOGGER.warning("Device offline: %s", error_msg)
            else:
                _LOGGER.error("Error getting status: %s", response)
            return {}

        # Convert status list to dictionary
        return {item["code"]: item["value"] for item in response.get("result", [])}

    def get_device_info(self) -> dict[str, Any]:
        """Get device info.

        Returns:
            Dictionary with device information

        Raises:
            PermissionError: If no access to device (code 1106)
            ConnectionError: If other connection error
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
        """Send command to device.

        Args:
            code: Command code (data point)
            value: Command value

        Returns:
            True if command successful
        """
        commands = {"commands": [{"code": code, "value": value}]}
        response = self.api.post(f"/v1.0/devices/{self.device_id}/commands", commands)

        success = response.get("success", False)
        if not success:
            error_msg = response.get("msg", "Unknown error")
            if "device is offline" in error_msg.lower() or response.get("code") == 2001:
                _LOGGER.warning("Could not send command %s (device offline): %s", code, error_msg)
            else:
                _LOGGER.error("Error sending command %s: %s", code, response)

        return success


    def get_all_devices(self) -> list[dict[str, Any]]:
        """Get list of all devices available for this project.

        Returns:
            List of dictionaries with device information
        """
        # Endpoint to get device list by project
        # See https://developer.tuya.com/en/docs/iot/list-devices?id=K9j6y60m66v1f
        response = self.api.get("/v1.0/devices")
        if not response.get("success"):
            _LOGGER.error("Error getting device list: %s", response)
            return []

        return response.get("result", {}).get("list", [])


    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Tuya Cloud.

        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            self.get_device_info()
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
