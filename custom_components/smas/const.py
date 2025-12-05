from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

DOMAIN = "smas"
VERSION = 1
LOGIN_URL = "https://portal.ucloud.cgi.com/uPortal2/smasleiria/login"
LIST_SUBSCRIPTIONS = "https://portal.ucloud.cgi.com/uPortal2/smasleiria/Subscription/listSubscriptions"

CONF_SUBSCRIPTION_ID = "subscription_id"

# Optional: re-use HA constants for clarity
CONF_EMAIL = CONF_USERNAME  # we treat "username" as email