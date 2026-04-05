"""Constants for the Oura Bedtime integration."""

from datetime import timedelta
from logging import getLogger

LOGGER = getLogger(__package__)

DOMAIN = "oura_bedtime"
SCAN_INTERVAL = timedelta(hours=4)
BEDTIME_LOOKBACK_DAYS = 10
API_BASE_URL = "https://api.ouraring.com/v2"
CONF_ACCESS_TOKEN = "access_token"
