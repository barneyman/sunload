from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE
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
    discovery_info: DiscoveryInfoType,
) -> None:

    _LOGGER.info("async_setup_platform! sunload %s %s", config, discovery_info)

    # """Set up the sensor platform."""

    # config isn't passed from async_setup() [or i'm doing something wrong!]
    # so grab a cached copy from dad
    config = hass.data[DOMAIN]

    _LOGGER.info("hass.config.as_dict %s", (config))

    rewiredSensors = []

    # first - turn the sun.sun attributes we care about into sensors
    _LOGGER.info("Adding azimuth sensor")
    sensorConfig = {
        "name": Template("sunload_azimuth"),
        "unit_of_measurement": "°",
        "state_class": "measurement",
        "state": Template("{{ state_attr('sun.sun', 'azimuth') }}"),
    }
    rewiredSensors.append(
        SensorTemplate(hass, sensorConfig, "sunload.internal.azimuth")
    )

    _LOGGER.info("Adding elevation sensor")
    sensorConfig = {
        "name": Template("sunload_elevation"),
        "unit_of_measurement": "°",
        "state_class": "measurement",
        "state": Template("{{ state_attr('sun.sun', 'elevation') }}"),
    }
    rewiredSensors.append(
        SensorTemplate(hass, sensorConfig, "sunload.internal.elevation")
    )

    add_entities(rewiredSensors)

    # walk thru the config
    newSensors = []

    tempSensor = config["tempsensor"]
    threshold = config["threshold"]

    if "instances" in config:

        for instance in config["instances"]:
            newinstance = sunloadInstance(hass, instance, tempSensor, threshold)
            _LOGGER.info("adding instance %s", (newinstance.name))
            newSensors.append(newinstance)

        add_entities(newSensors)

    else:
        _LOGGER.error("No instances configured for %s", (DOMAIN))


class sunloadInstance(SensorEntity):
    def __init__(self, hass, config, tempsensor, threshold) -> None:

        _LOGGER.info("sunloadInstance init %s", (config))

        self._name = "{}_{}".format(DOMAIN, config["name"])
        self._attr_native_value = None
        self._hass = hass

        self._inAzimuth = None
        self._inElevation = None

        self._tempsensor = tempsensor
        self._threshold = threshold

        # get the deets
        # azimuth
        azimuth = config["azimuth"]
        self._azimuth_min = azimuth["min"]
        self._azimuth_max = azimuth["max"]

        self._elevation_min = self._elevation_max = None

        if "elevation" in config:
            if "min" in config["elevation"]:
                self._elevation_min = config["elevation"]["min"]

            if "max" in config["elevation"]:
                self._elevation_max = config["elevation"]["max"]

        # and update
        self.update()

    def update(self):
        _LOGGER.debug("update! %s", (self._name))

        # get el and az
        az = self._hass.states.get("sensor.sunload_azimuth")
        el = self._hass.states.get("sensor.sunload_elevation")

        if (
            az is None
            or el is None
            or az.state == STATE_UNKNOWN
            or el.state == STATE_UNKNOWN
        ):
            return

        az = float(az.state)
        el = float(el.state)

        _LOGGER.info("%s az %f el %f", self._name, az, el)

        wrapFix = 0
        self._inAzimuth = False

        # have to spot crossing thr 0/360 line
        if self._azimuth_max > self._azimuth_min:
            # has the potential to cross the border, so just rotate the world, consistently
            wrapFix = 360 - self._azimuth_max

            _LOGGER.info(
                "%s wrapping az %f min %f with %f",
                self._name,
                az,
                self._azimuth_min,
                wrapFix,
            )

            if (az + wrapFix) % 360 < self._azimuth_min + wrapFix:
                self._inAzimuth = True

        elif az < self._azimuth_min and az > self._azimuth_max:
            self._inAzimuth = True

        # elevation
        self._inElevation = True

        if self._elevation_min is not None:
            if el < self._elevation_min:
                self._inElevation = False

        if self._elevation_max is not None:
            if el > self._elevation_max:
                self._inElevation = False

        # ok - now check the temp
        ctemp = self._hass.states.get(self._tempsensor)

        if ctemp is not None and ctemp.state not in [STATE_UNKNOWN, STATE_UNAVAILABLE]:

            self._attr_native_value = False
            if (
                self._inElevation
                and self._inAzimuth
                and float(ctemp.state) > self._threshold
            ):
                self._attr_native_value = True

            _LOGGER.info("%s state is %s", self._name, self._attr_native_value)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def extra_state_attributes(self):  # -> Mapping[str, Any] | None:

        return {"inazimuth": self._inAzimuth, "inelevation": self._inElevation}
