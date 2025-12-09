"""EM Gateway configuration.

Do not edit the configuration values herein, they will be
overwritten from config file, see file names below!

2025-06-02 Ulrich Lukas
"""

import logging
import shutil
import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from dataclass_binder import Binder

from em_gateway import __version__

logger = logging.getLogger(__name__)

CONFIG_FILE_NAME: str = "config.toml"
DEFAULT_CONFIG_FILE_NAME: str = "config_default.toml"


@dataclass
class MQTTConfig:
    """Settings for MQTT control and telemetry."""

    # Setting this to false disables transmitting of MQTT telegrams
    ACTIVATED: bool = True
    TOPIC_POWER_CONTROL: str = "cmd/em_gateway/set_power"
    TOPIC_MEASUREMENTS: str = "tele/em_gateway/measurements"
    BROKER: str = "localhost"
    PORT: int = 1883
    # MQTT minimum broadcast (transmit) time interval in seconds.
    # If the inverter stops requesting energy meter data,
    # MQTT broadcast is also stopped.
    INTERVAL: float = 10.0


@dataclass
class SDM630EmuConfig:
    """Settings for emulated SDM630 energy meter."""

    # Serial port connected to Modbus-"Meter" port of the inverter
    # modbus_port: str = "/dev/ttyUSB1"
    modbus_port: str = "COM1"
    baudrate: int = 9600
    version: str = __version__


@dataclass
class SDM630ClientConfig:
    """Settings for SDM630 energy meter Modbus client."""

    # Serial port connected to grid-sided SDM630 energy meter using Modbus-RTU
    modbus_port: str = "/dev/ttyUSB3"


@dataclass
class SHMReceiverConfig:
    """Settings for Sunny Home Manager (SHM) receiver."""

    # Interface name of the UDP receiver input
    udp_interface: str = "eth0"
    # UDP source address of the Sunny Home Manager or compatible device
    udp_addr: str = ""
    # UDP port of the Sunny Home Manager or compatible device
    udp_port: int = 8888


@dataclass
class InverterConfig:
    """Settings for Deye inverter."""

    # Serial port connected to main Modbus control port of the inverter
    # modbus_port: str = "/dev/ttyUSB2"
    modbus_port: str = "/tmp/ttyV1"

    # Poll interval in seconds for reading inverter state
    poll_interval: float = 1.0


@dataclass
class AppConfig:
    """All application settings."""

    version: str = __version__
    # Can be "grid-side", "inverter-direct" or "off" (default) for no operation.
    CONTROL_MODE: str = "inverter-direct"
    mqtt: type[MQTTConfig] = MQTTConfig
    emulator: type[SDM630EmuConfig] = SDM630EmuConfig
    inverter: type[InverterConfig] = InverterConfig


def init_or_read_from_config_file(*, init: bool = False) -> AppConfig:
    """Init app config on request or if not existing. Otherwise read from config file."""
    return AppConfig()
    conf_file = Path.home().joinpath(f".{__package__}").joinpath(CONFIG_FILE_NAME)
    default_conf_file = files(__package__).joinpath(DEFAULT_CONFIG_FILE_NAME)
    if init or not conf_file.is_file():
        conf_file.parent.mkdir(exist_ok=True)
        shutil.copy(default_conf_file, conf_file)
        logger.log(
            logging.INFO if init else logging.ERROR,
            "Configuration initialized using file: %s\n"
            "==> Please edit this file NOW to configure "
            "and run the application again!",
            conf_file,
        )
        sys.exit(0 if init else 1)
    try:
        conf = Binder(AppConfig).parse_toml(conf_file)
        if conf.CONTROL_MODE not in ("grid-side", "inverter-direct"):
            logger.error("Application not configured! Edit config file first: %s", conf_file)
            sys.exit(1)
    except Exception as e:
        logger.exception("Error reading configuration file %s", conf_file)
        sys.exit(1)
    return conf
