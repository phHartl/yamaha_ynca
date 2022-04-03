"""Constants for the Yamaha (YNCA) integration."""

import logging
import ynca

DOMAIN = "yamaha_ynca"
LOGGER = logging.getLogger(__package__)

# Keep the value "serial_port" for backward compatibility
CONF_SERIAL_URL = "serial_port"

MANUFACTURER_NAME = "Yamaha"

ZONE_SUBUNIT_IDS = [
    ynca.Subunit.MAIN,
    ynca.Subunit.ZONE2,
    ynca.Subunit.ZONE3,
    ynca.Subunit.ZONE4,
]
