"""Config flow for Oura Bedtime integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    OuraApiAuthenticationError,
    OuraApiClient,
    OuraApiCommunicationError,
)
from .const import CONF_ACCESS_TOKEN, DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)


class OuraBedtimeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oura Bedtime."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = OuraApiClient(
                token=user_input[CONF_ACCESS_TOKEN], session=session
            )

            try:
                await client.async_validate_token()
            except OuraApiAuthenticationError:
                errors["base"] = "auth"
            except OuraApiCommunicationError:
                errors["base"] = "connection"
            except Exception:
                LOGGER.exception("Unexpected error during config flow")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title="Oura Bedtime",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
