# sunload
Sunload sensor for Home Assistant

## Description
This is a platform that will create a number of sensors that can help to make
blueprints easier to use.

## Why a platform?
It was the longest day, Dec 21, 2021, and the sun was pouring through the loungeroom 
window - "About time I wrote that automation to close the blinds on a 30degC day"

I originally tried to do this entirely as a blueprint but quickly realised automations 
are not really great at `choose`, the automations can be made significantly simpler if
logic is deferred to sensors.

This can be achieved in `configuration.yaml` - see appendix at the bottom - but I threw 
this platform together.

## Sensors
### Names
Creates a number of sensors from `sun.sun` attributes
- `sensor.sunload_elevation`
- `sensor.sunload.azimuth`

tip: you can add these sensors to a Sensor Card in the UI so you're not guessing where the 
sun is right now 

Every `instance` gets a sensor of the form `"sensor.sunload_{}".format(INSTANCE_NAME)`

### Values
Each of these instance sensors has the following attributes

- `inazimuth`, `bool` - the sun is between the azimuth limits for this instance
- `inelevation` , `bool` - the sun is between the elevation limits for this instance
- `state`, `bool` - `inazimuth and inelevation`

## Installation
This code needs to run **on** your HA installation, if you're uncomfortable with that, 
have a look at the appendix below which has a simpler implementation

***
this code is freshly minted so it's gonna have bugs!
***

Shell to the `config/custom_components` directory on your HA install, then clone this
repo
```
git clone https://github.com/barneyman/sunload.git
```

Restart your HA, then change `configuration/yaml`, then restart HA once again - HA **will** complain about the addon being 
untested by their team.

Deleting the config entries will stop this code executng. When not used, the `sunload` 
directory can be removed

### Example Config
```
sunload:
  instances:
    - name: northside
      azimuth:
        min: 70
        max: 350
      elevation:
        min: 5
    - name: southside
      azimuth:
        min: 330
        max: 270
      elevation:
        min: 5
```        
### Example Automation using above
```
- alias: reduce northside sunload
  trigger:
    # when sun is on the north face
    platform: state
    entity_id:
      - sensor.sunload_northside
    to: True

  condition: 
  # if i'm home and the forecast > 30 degs
     - condition: and
       conditions:
        - condition: numeric_state 
          # this is a template sensor i created from {{ states.weather.beachhouse.attributes["temperature"] |float() }}
          entity_id: sensor.forecast_temp
          above: 30
        - condition: state
          entity_id:
            - device_tracker.galaxy_note10
          state: 'home'

  action:
    - service: cover.close_cover
      entity_id: cover.north_blinds      
  

- alias: open northside sunload
  trigger:
    # when sun is off north face
    platform: state
    entity_id:
      - sensor.sunload_northside
    to: False
  condition:
  # if i'm home
    - condition: state
      entity_id:
        - device_tracker.galaxy_note10
      state: 'home'

  action:
    - service: cover.open_cover
      entity_id: cover.north_blinds      



````



## Appendix - Configuration ONLY Alternative

### Attributes exposed as Sensors
```
template:
  - sensor:
      - name: "Sun Azimuth"
        unit_of_measurement: "°"
        state_class: "measurement"
        state: >
          {{ state_attr('sun.sun', 'azimuth') }}

      - name: "Sun Elevation"
        unit_of_measurement: "°"
        state_class: "measurement"
        state: >
          {{ state_attr('sun.sun', 'elevation') }}

```
### BinarySensors doing the logic (Examples)
```
  - binary_sensor:
      - name: Sun Azimuth Test
        state: >
          {{  states.sensor.sun_azimuth.state | int() < 70 and states.sensor.sun_azimuth.state |int() > 5 }}

      - name: Sun Elevation Test
        state: >
          {{ states.sensor.sun_elevation.state | int() > 5 and states.sensor.sun_elevation.state | int() < 60 }}
      - name: Sun Azimuth And Elevation Test
        state: >
          {{ states.sensor.sun_elevation_test.state and sensor.sun_azimuth_test.state < 60 }}
```
