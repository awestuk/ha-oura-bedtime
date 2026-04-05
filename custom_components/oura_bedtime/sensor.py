"""Sensor platform for Oura Bedtime."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OuraBedtimeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Oura Bedtime sensor from a config entry."""
    coordinator: OuraBedtimeCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OuraAverageBedtimeSensor(coordinator, entry)])


class OuraAverageBedtimeSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing the average bedtime over the last 10 days."""

    _attr_icon = "mdi:bed-clock"
    _attr_has_entity_name = True
    _attr_name = "Average Bedtime"

    def __init__(
        self,
        coordinator: OuraBedtimeCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_average_bedtime"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Oura Ring",
            manufacturer="Oura",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> str | None:
        """Return the average bedtime."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("average_bedtime")

    @property
    def extra_state_attributes(self) -> dict[str, str | int] | None:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return None
        bedtime = self.coordinator.data.get("average_bedtime", "N/A")
        return {
            "sample_count": self.coordinator.data.get("sample_count", 0),
            "status": _bedtime_status(bedtime),
        }


def _bedtime_status(bedtime: str) -> str:
    """Return good/warning/late based on average bedtime.

    - Before 23:15 -> good
    - 23:15 to 23:44 -> warning
    - 23:45 or later (including after midnight) -> late
    """
    if bedtime == "N/A":
        return "unknown"
    try:
        h, m = (int(x) for x in bedtime.split(":"))
    except ValueError:
        return "unknown"
    mins = h * 60 + m
    # After-midnight times (00:00–05:59) count as late
    if mins < 360:
        return "late"
    if mins >= 1425:  # 23:45
        return "late"
    if mins >= 1395:  # 23:15
        return "warning"
    return "good"
