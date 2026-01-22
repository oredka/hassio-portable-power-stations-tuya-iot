"""Config flow for Tuya IoT Power Stations integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .api import TwoEPowerStationAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Possible Tuya endpoints by region
TUYA_ENDPOINTS = {
    "Europe": "https://openapi.tuyaeu.com",
    "America": "https://openapi.tuyaus.com",
    "China": "https://openapi.tuyacn.com",
    "India": "https://openapi.tuyain.com",
}

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("access_id"): str,
    vol.Required("access_secret"): str,
    vol.Required("device_id"): str,
    vol.Required("endpoint", default="Europe"): vol.In(list(TUYA_ENDPOINTS.keys())),
})


def validate_input(hass: HomeAssistant, data: dict[str, Any], device_id: str | None = None) -> dict[str, Any]:
    """Validate user input.

    Args:
        hass: Home Assistant instance
        data: Data from user
        device_id: Device ID to validate (if not passed, taken from data)

    Returns:
        Dictionary with connection information

    Raises:
        Exception: If connection fails
    """
    # Get endpoint URL from region name
    endpoint_url = TUYA_ENDPOINTS.get(data["endpoint"], data["endpoint"])
    target_device_id = device_id or data["device_id"]

    api = TwoEPowerStationAPI(
        access_id=data["access_id"],
        access_secret=data["access_secret"],
        device_id=target_device_id,
        endpoint=endpoint_url,
    )

    # Test connection
    success, error_msg = api.test_connection()
    if not success:
        raise Exception(error_msg or f"Failed to connect to Tuya Cloud for device {target_device_id}")

    # Get device info
    device_info = api.get_device_info()

    return {
        "title": device_info.get("name", f"Power Station ({target_device_id[:8]})"),
        "device_info": device_info,
        "endpoint": endpoint_url,
        "device_id": target_device_id,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Tuya IoT Power Stations."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user input."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Split device IDs by comma and clean up
                device_ids = [
                    d.strip() for d in user_input["device_id"].replace(";", ",").split(",") if d.strip()
                ]
                
                if not device_ids:
                    errors["device_id"] = "invalid_device_id"
                    raise Exception("No device IDs provided")

                # Process the first device to validate credentials and endpoint
                first_device_id = device_ids[0]
                info = await self.hass.async_add_executor_job(
                    validate_input, self.hass, user_input, first_device_id
                )

                # Store endpoint URL instead of region name for all entries
                user_input["endpoint"] = info["endpoint"]

                # If multiple devices, start flows for the rest
                if len(device_ids) > 1:
                    for extra_id in device_ids[1:]:
                        # Check if already configured
                        await self.async_set_unique_id(extra_id, raise_on_progress=False)
                        try:
                            self._abort_if_unique_id_configured()
                            
                            # Validate extra device
                            await self.hass.async_add_executor_job(
                                validate_input, self.hass, user_input, extra_id
                            )
                            
                            # Start a new flow for this device
                            await self.hass.config_entries.flow.async_init(
                                DOMAIN,
                                context={"source": config_entries.SOURCE_USER},
                                data={
                                    "access_id": user_input["access_id"],
                                    "access_secret": user_input["access_secret"],
                                    "device_id": extra_id,
                                    "endpoint": user_input["endpoint"],
                                }
                            )
                        except Exception as e:
                            _LOGGER.warning("Could not add extra device %s: %s", extra_id, e)

                # Set unique ID for the first device
                await self.async_set_unique_id(first_device_id)
                self._abort_if_unique_id_configured()

                # Create entry for the first (or only) device
                user_input["device_id"] = first_device_id
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )
            except PermissionError as err:
                _LOGGER.error("Permission error: %s", err)
                errors["base"] = "permission_denied"
            except Exception as err:
                _LOGGER.error("Setup error: %s", err)
                if not errors:
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "setup_info": "1. Register at https://iot.tuya.com\n2. Create Cloud Project\n3. Link API: Industry Solutions -> Smart Home\n4. Add device to project\n5. Copy Access ID, Access Secret and Device ID (multiple allowed via comma)"
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
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
