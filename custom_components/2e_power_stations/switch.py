"""Перемикачі для 2E Power Stations через Tuya IoT."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Можливі коди Tuya data points для перемикачів
# Реальні коди залежать від конкретної моделі пристрою
SWITCH_CODES = {
    "main": ["switch", "switch_1", "main_switch"],
    "ac": ["switch_ac", "ac_switch", "switch_2"],
    "dc": ["switch_dc", "dc_switch", "switch_usb", "switch_3"],
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Налаштування перемикачів з config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Додаємо тільки ті перемикачі, які знайдені в даних пристрою
    entities = []

    for switch_type, codes in SWITCH_CODES.items():
        # Перевіряємо чи є хоч один з кодів у даних
        for code in codes:
            if code in coordinator.data:
                if switch_type == "main":
                    entities.append(PowerStationOutputSwitch(coordinator, entry, code))
                elif switch_type == "ac":
                    entities.append(PowerStationACOutputSwitch(coordinator, entry, code))
                elif switch_type == "dc":
                    entities.append(PowerStationDCOutputSwitch(coordinator, entry, code))
                break  # Знайшли код, додали entity, виходимо з циклу

    if entities:
        async_add_entities(entities)
    else:
        _LOGGER.warning("Не знайдено жодного перемикача в даних пристрою")


class PowerStationSwitchBase(CoordinatorEntity, SwitchEntity):
    """Базовий клас для перемикачів 2E Power Station."""

    def __init__(self, coordinator, entry: ConfigEntry, switch_code: str) -> None:
        """Ініціалізація перемикача."""
        super().__init__(coordinator)
        self._entry = entry
        self._switch_code = switch_code
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "2E Power Station",
            "manufacturer": "2E",
            "model": "Power Station",
        }

    @property
    def is_on(self) -> bool:
        """Чи увімкнений перемикач."""
        return self.coordinator.data.get(self._switch_code, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Увімкнути перемикач."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_switch, self._switch_code, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Вимкнути перемикач."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_switch, self._switch_code, False
        )
        await self.coordinator.async_request_refresh()


class PowerStationOutputSwitch(PowerStationSwitchBase):
    """Перемикач основного виходу."""

    _attr_name = "Основний вихід"

    @property
    def unique_id(self) -> str:
        """Унікальний ID перемикача."""
        return f"{self._entry.entry_id}_main_output"


class PowerStationACOutputSwitch(PowerStationSwitchBase):
    """Перемикач AC виходу."""

    _attr_name = "AC вихід"

    @property
    def unique_id(self) -> str:
        """Унікальний ID перемикача."""
        return f"{self._entry.entry_id}_ac_output"


class PowerStationDCOutputSwitch(PowerStationSwitchBase):
    """Перемикач DC виходу."""

    _attr_name = "DC вихід"

    @property
    def unique_id(self) -> str:
        """Унікальний ID перемикача."""
        return f"{self._entry.entry_id}_dc_output"
