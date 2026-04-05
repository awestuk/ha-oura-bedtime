"""Data update coordinator for Oura Bedtime."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .api import OuraApiAuthenticationError, OuraApiClient, OuraApiError
from .const import BEDTIME_LOOKBACK_DAYS, LOGGER, SCAN_INTERVAL


class OuraBedtimeCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching and processing Oura sleep data."""

    def __init__(self, hass: HomeAssistant, client: OuraApiClient) -> None:
        super().__init__(
            hass,
            LOGGER,
            name="Oura Bedtime",
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Fetch sleep data and compute average bedtime."""
        now = dt_util.now()
        end_date = now.date().isoformat()
        start_date = (now.date() - timedelta(days=BEDTIME_LOOKBACK_DAYS)).isoformat()

        try:
            records = await self.client.async_get_sleep(start_date, end_date)
        except OuraApiAuthenticationError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except OuraApiError as err:
            raise UpdateFailed(str(err)) from err

        average_bedtime = calculate_average_bedtime(records)
        return {
            "average_bedtime": average_bedtime,
            "sample_count": len(records),
        }


def calculate_average_bedtime(records: list[dict]) -> str:
    """Calculate the average bedtime from sleep records.

    Handles bedtimes that span midnight by mapping times to a continuous
    range centred on midnight: hours >= 18 become negative minutes
    (e.g. 23:00 = -60), hours < 18 stay positive (e.g. 01:00 = 60).
    """
    if not records:
        return "N/A"

    minutes_list: list[float] = []
    for record in records:
        bedtime_start = record.get("bedtime_start")
        if not bedtime_start:
            continue

        dt = datetime.fromisoformat(bedtime_start)
        total_minutes = dt.hour * 60 + dt.minute
        # Map evening times to negative values so averaging across midnight works
        if dt.hour >= 18:
            total_minutes -= 1440

        minutes_list.append(total_minutes)

    if not minutes_list:
        return "N/A"

    avg_minutes = sum(minutes_list) / len(minutes_list)
    # Convert back to positive clock time
    if avg_minutes < 0:
        avg_minutes += 1440

    hours = int(avg_minutes) // 60
    mins = int(round(avg_minutes)) % 60
    return f"{hours:02d}:{mins:02d}"
