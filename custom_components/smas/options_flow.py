from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

# Field key for the "new password" input.
# The label text should clearly inform the user what this field does.
NEW_PASSWORD_KEY = "new_password_leave_empty_to_keep_current"


class SmasOptionsFlow(config_entries.OptionsFlow):
    """Options flow for SMAS integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Store the config entry for later use."""
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the options step."""
        errors: dict[str, str] = {}

        # Current stored values
        current_email = self._entry.data.get("email", "")
        # We do NOT show the current password
        current_password = self._entry.data.get("password", "")
        current_subscription_id = self._entry.data.get("subscriptionId", 0)

        if user_input is not None:
            new_email = user_input["email"]
            new_subscription_id = user_input["subscriptionId"]

            # New password is optional: if empty, keep the existing one
            new_password_input = user_input.get(NEW_PASSWORD_KEY, "")
            if new_password_input:
                password_to_store = new_password_input
            else:
                password_to_store = current_password

            new_data = {
                **self._entry.data,
                "email": new_email,
                "password": password_to_store,
                "subscriptionId": new_subscription_id,
            }

            # Update the config entry with the new values
            self.hass.config_entries.async_update_entry(
                self._entry,
                data=new_data,
            )

            # Reload the integration so changes take effect
            await self.hass.config_entries.async_reload(self._entry.entry_id)

            # No extra options stored separately for now
            return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required("email", default=current_email): str,
                # New password field: empty means "do not change"
                vol.Optional(NEW_PASSWORD_KEY, default=""): str,
                vol.Required(
                    "subscriptionId", default=current_subscription_id
                ): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
