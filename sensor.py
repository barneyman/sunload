from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.template.sensor import SensorTemplate
from homeassistant.helpers.template import Template

import logging
_LOGGER = logging.getLogger(__name__)

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "sunload"

# when called from a async_load_platform (say from async_setup) the passed config does not get this far, so i use discovery
async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType
) -> None:

    _LOGGER.info("async_setup_platform! sunload {} {}".format(config,discovery_info))

    """Set up the sensor platform."""

    # config isn't passed from async_setup() [or i'm doing something wrong!]
    # so grab a cached copy from dad
    config=hass.data[DOMAIN]

    _LOGGER.info("hass.config.as_dict {}".format(config))


    rewiredSensors=[]

    # first - turn the sun.sun attributes we care about into sensors
    _LOGGER.info("Adding azimuth sensor")
    sensorConfig={"name":Template("sunload_azimuth"),"unit_of_measurement":"°", "state_class": "measurement","state":Template("{{ state_attr('sun.sun', 'azimuth') }}")}
    rewiredSensors.append(SensorTemplate(hass,sensorConfig,"sunload.internal.azimuth" ))

    _LOGGER.info("Adding elevation sensor")
    sensorConfig={"name":Template("sunload_elevation"),"unit_of_measurement":"°", "state_class": "measurement","state":Template("{{ state_attr('sun.sun', 'elevation') }}")}
    rewiredSensors.append(SensorTemplate(hass,sensorConfig, "sunload.internal.elevation" ))

    add_entities(rewiredSensors)

    # walk thru the config
    newSensors=[]

    if "instances" in config:

        for instance in config["instances"]:
            newSensors.append(sunloadInstance(hass,instance))

        add_entities(newSensors)

    else:
        _LOGGER.error("No instances configured for {}".format(DOMAIN))


class sunloadInstance(SensorEntity):

    def __init__(self, hass, config) -> None:
        
        _LOGGER.info("sunloadInstance init {}".format(config))

        self._name=config["name"]
        self._state=None

    def update(self):
        _LOGGER.info("update! {}".format(self._name))
        pass

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state