"""Config flow for SMAS integration."""

from __future__ import annotations

from typing import Any

import asyncio
import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
import homeassistant.helpers.config_validation as cv

from .const import VERSION, DOMAIN, CONF_PASSWORD, CONF_EMAIL, CONF_SUBSCRIPTION_ID

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,           # email
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_SUBSCRIPTION_ID): cv.positive_int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate user input and perform a login against the SMAS API.

    Replace the TODO section with your real client login call.
    """

    session = aiohttp_client.async_get_clientsession(hass)

    # TODO: Replace this with your real login logic.
    # Example using your client:
    #
    # from .client import SmasClient
    # client = SmasClient(hass, data[CONF_EMAIL], data[CONF_PASSWORD])
    # await client.async_login()
    #
    # Here we just simulate success.

    # You can use `session` for a quick sanity network check if you want:
    # async with session.get("https://www.google.com", timeout=5):
    #     pass

    # Return something useful if needed; here we just echo email/subscription
    return {
        CONF_EMAIL: data[CONF_EMAIL],
        CONF_SUBSCRIPTION_ID: data[CONF_SUBSCRIPTION_ID],
    }

class SmasConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMAS."""

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except (aiohttp.ClientError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "invalid_auth"
            else:
                # Optional: you can set a unique_id based on email/subscription
                await self.async_set_unique_id(
                    f"{user_input[CONF_EMAIL]}_{user_input[CONF_SUBSCRIPTION_ID]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"{user_input[CONF_EMAIL]} ({user_input[CONF_SUBSCRIPTION_ID]})",
                    data={
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_SUBSCRIPTION_ID: user_input[CONF_SUBSCRIPTION_ID],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    # ---------- RECONFIGURE FLOW (manual, from the UI menu) ----------

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle manual reconfiguration of the integration."""
        reconfigure_entry = self._get_reconfigure_entry()
        entry_data = reconfigure_entry.data

        errors: dict[str, str] = {}

        # Label used for the password field in the reconfigure form
        password_field_key = "password (leave empty to keep current)"

        if user_input is None:
            # First time: show form with current email/subscriptionId and empty password
            data_schema = vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=entry_data.get(CONF_EMAIL, "")): cv.string,
                    vol.Optional(password_field_key, default=""): cv.string,
                    vol.Required(
                        CONF_SUBSCRIPTION_ID,
                        default=entry_data.get(CONF_SUBSCRIPTION_ID, 0),
                    ): cv.positive_int,
                }
            )

            return self.async_show_form(
                step_id="reconfigure",
                data_schema=data_schema,
                errors=errors,
            )

        # User submitted the form
        new_email: str = user_input[CONF_EMAIL]
        new_subscription_id: int = user_input[CONF_SUBSCRIPTION_ID]
        new_password_input: str = user_input.get(password_field_key, "")

        # If password field is empty, keep the old one
        if new_password_input:
            password_to_store = new_password_input
        else:
            password_to_store = entry_data[CONF_PASSWORD]

        # Build new data for entry
        new_data = {
            **entry_data,
            CONF_EMAIL: new_email,
            CONF_PASSWORD: password_to_store,
            CONF_SUBSCRIPTION_ID: new_subscription_id,
        }

        # Optional: validate the new data with a login
        try:
            await validate_input(
                self.hass,
                {
                    CONF_EMAIL: new_email,
                    CONF_PASSWORD: password_to_store,
                    CONF_SUBSCRIPTION_ID: new_subscription_id,
                },
            )
        except (aiohttp.ClientError, asyncio.TimeoutError):
            errors["base"] = "cannot_connect"
        except Exception:
            errors["base"] = "invalid_auth"
        else:
            # If validation is OK, update entry and reload integration
            return self.async_update_reload_and_abort(
                reconfigure_entry,
                data_updates=new_data,
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
