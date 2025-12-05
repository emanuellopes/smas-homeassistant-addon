import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_SUBSCRIPTION_ID

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the SMAS integration from a config entry."""

    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    subscription_id = entry.data[CONF_SUBSCRIPTION_ID]

    _LOGGER.info("Setting up SMAS integration for email %s and subscription %d", email, subscription_id)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_EMAIL: email,
        CONF_PASSWORD: password,
        CONF_SUBSCRIPTION_ID: subscription_id,
    }

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the SMAS integration when the entry is removed."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
