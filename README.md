# EM Gateway
## This is a work-in-progress repository: DO NOT USE!

Energy Meter Gateway for Battery Inverter Feed-In Power Control.

Live control of grid-side instantaneous influx and outgoing power for
Deye low-voltage battery and hybrid inverters running in grid-parallel
zero-export mode.

This enables dynamic feed-in tariffs, direct energy trading, local load-shaping
or scheduled application of an arbitrary load/supply power profile using a
supervisory plant controller or energy management system (EMS).

In grid-side control mode, this application acts as a Modbus-to-Modbus gateway
for data from an attached SDM630 energy meter, superimposing an arbitrary power
offset (positive or negative) to the values reported from the meter.

This mode 100% keeps the original dynamics and tuning settings from the
zero-export power closed-loop controller implemented in the Deye inverter.

In inverter-direct control mode, the energy meter for zero-export control is
emulated using read-out values of current active power from the inverter itself,
allowing for direct control of inverter active output power.

The grid-side or inverter-side instantaneous power setpoint can be set and
continuously updated using the configured MQTT topic.
MQTT topic default: cmd/deye_powercontrol/set_power

The Python code uses asyncio, async-enabled pymodbus and aiomqtt packages
for cooperative multitasking.

The gateway application is configured via text file in user home folder:
    ~/.em_gateway/app_config.toml

This file must be edited to suit application details.

2025-08-27 Ulrich Lukas