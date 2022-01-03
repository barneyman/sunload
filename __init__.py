# inspired by https://github.com/home-assistant/example-custom-config/tree/master/custom_components/example_load_platform

import voluptuous as vol
import logging
_LOGGER = logging.getLogger(__name__)

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "sunload"

import json
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv

offSchema=vol.Schema({
    vol.Required("at"): cv.time
})

# TODO enable checking
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("tempsensor"): cv.string,
                vol.Required("threshold"): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),

                vol.Required("instances"): vol.All(
                    cv.ensure_list,
                    [
                        {
                            vol.Required("name"): cv.string,  
                            vol.Required("azimuth"): vol.Schema({
                                vol.Required("min"): vol.All(vol.Coerce(float), vol.Range(min=0, max=359)),
                                vol.Required("max"): vol.All(vol.Coerce(float), vol.Range(min=0, max=359))
                            }),
                            vol.Optional("elevation"): vol.Schema({
                                vol.Optional("min"): vol.All(vol.Coerce(float), vol.Range(min=0, max=90)),
                                vol.Optional("max"): vol.All(vol.Coerce(float), vol.Range(min=0, max=90))
                            }),

                        }
                    ]
                )
            }
        )
    }, extra=vol.ALLOW_EXTRA
)

suninstances=[]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""

    _LOGGER.info("{} async_setup {}".format(DOMAIN, config))

    if DOMAIN in config:
        
        myConfig=config.get(DOMAIN)

        hass.data[DOMAIN]=myConfig

        _LOGGER.info("{} config {}".format(DOMAIN, myConfig))

        # see hass.helpers.discovery.async_load_platform for the create task
        hass.async_create_task(hass.helpers.discovery.async_load_platform('sensor', DOMAIN, None, config))

    else:
        _LOGGER.error("No config for {}".format(DOMAIN))

    return True
