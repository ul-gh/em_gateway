#!/usr/bin/env python3
"""EM Gateway.

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
"""

import argparse
import asyncio
import logging
import threading

from em_gateway import gateway_config
from em_gateway.sdm630_emulator import SDM630Emulator

parser = argparse.ArgumentParser(prog=__package__, description=__doc__)
parser.add_argument("--init", action="store_true", help="Initialize configuration file and exit")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose (debug) output")
cmdline = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(message)s", level=logging.DEBUG if cmdline.verbose else logging.INFO)


# App configuration read from file: "~/bms_gateway/bms_config.toml"
# Default configuration: See source tree file "bms_config_default.toml"
conf = gateway_config.init_or_read_from_config_file(init=cmdline.init)

t_main: threading.Thread | None = None
stop_flag = threading.Event()

# meter_emu = SDM630Emulator(conf.emulator)
emu: SDM630Emulator


# async def main_task() -> None:
#     async with AsyncExitStack() as stack:
#         bmses_in = [BMS_In(bms_conf) for bms_conf in conf.bmses_in]
#         for bms in bmses_in:
#             await stack.enter_async_context(bms)
#         bmses_out = [BMS_Out(bms_conf) for bms_conf in conf.bmses_out]
#         for bms in bmses_out:
#             await stack.enter_async_context(bms)
#         if conf.mqtt.ACTIVATED:
#             mqtt_out = MQTTBroadcaster(conf.mqtt)
#             await stack.enter_async_context(mqtt_out)
#         while not thread_stop.isSet():
#             # Read all input BMSes
#             getters = (bms.get_state() for bms in bmses_in)
#             states_in = await asyncio.gather(*getters)
#             # Calculate total and average values, error flags and corrections
#             state_out = combiner.calculate_result_state(states_in)
#             logger.debug(state_out)
#             # Set calculated state on all virtual output BMSes.
#             # Individual current scaling values are applied from config file.
#             setters = (bms.set_state(state_out) for bms in bmses_out)
#             await asyncio.gather(*setters)
#             if conf.mqtt.ACTIVATED:
#                 await mqtt_out.set_state(state_out)


async def main_task() -> None:
    """Initialize application and launch all async tasks."""
    global emu  # noqa: PLW0603
    emu = SDM630Emulator()
    await emu.start_server()
    while not stop_flag.is_set():  # noqa: ASYNC110
        await asyncio.sleep(0.1)


def main() -> None:
    """Run main task."""
    try:
        logger.info("EM-Gateway running. Press (twice) <CTRL> + C to exit.")
        asyncio.run(main_task())
    except KeyboardInterrupt:
        stop_flag.set()


def run_bg() -> None:
    """Run main task in background thread (for debugging in ipython etc)."""
    global t_main  # noqa: PLW0603
    stop_flag.clear()
    t_main = threading.Thread(target=main)
    t_main.start()


def stop_bg() -> None:
    """Stop main task."""
    stop_flag.set()
    if t_main is not None:
        t_main.join()


if __name__ == "__main__":
    main()
