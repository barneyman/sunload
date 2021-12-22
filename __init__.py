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
CONFIG_SCHEMA_ = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("instances"): vol.All(
                    cv.ensure_list,
                    [
                        {
                            vol.Required("name"): cv.string,  
                            # vol.Required("presence_binary"): cv.string,  
                            # vol.Required("lux_sensor"): cv.string,
                            # vol.Required("off_scene"): cv.string,
                            # "softOff":offSchema,
                            # "hardOff":offSchema,
                            # "reset":offSchema,

                            # vol.Optional("jitter", default=30):vol.All(
                            #         vol.Coerce(float), vol.Range(min=0, max=50)
                            #     ),
                            # "absent": vol.Schema({
                            #     vol.Optional("unlit_scene"): cv.string,
                            #     vol.Optional("lit_scene"): cv.string,
                            #     vol.Required("minLux"): vol.All(
                            #         vol.Coerce(float), vol.Range(min=0, max=100)
                            #     ),
                            # }),
                            # "present": vol.Schema({
                            #     vol.Optional("unlit_scene"): cv.string,
                            #     vol.Optional("lit_scene"): cv.string,
                            #     vol.Required("minLux"): vol.All(
                            #         vol.Coerce(float), vol.Range(min=0, max=100)
                            #     ),
                            # }),
                        }
                    ]
                )
            }
        )
    }, extra=vol.ALLOW_EXTRA
)

suninstances=[]



# def setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     """Your controller/hub specific code."""

#     # Data that you want to share with your platforms
#     # hass.data[DOMAIN] = {
#     #     'temperature': 23
#     # }

#     _LOGGER.debug("{} setup {}".format(DOMAIN, config))

#     if DOMAIN in config:
        
#         myConfig=config.get(DOMAIN)

#         _LOGGER.info("{} config {}".format(DOMAIN, myConfig))

#         hass.helpers.discovery.load_platform('sensor', DOMAIN, None, myConfig)
#     else:
#         _LOGGER.error("No config for {}".format(DOMAIN))

#     return True

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""

    # Data that you want to share with your platforms
    # hass.data[DOMAIN] = {
    #     'temperature': 23
    # }

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