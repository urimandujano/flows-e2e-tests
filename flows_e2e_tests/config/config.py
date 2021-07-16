import os
from pathlib import Path

import structlog
from dynaconf import Dynaconf, Validator

logger = structlog.get_logger(__name__)

CURR_DIR = Path(__file__).resolve().parent
logger.debug(f"Reading settings from {CURR_DIR}")

ENV_SWITCHER = "FLOWS_TEST_ENVIRONMENT"
ENV_VALUE = os.getenv(ENV_SWITCHER, "production")
if ENV_SWITCHER != "GLOBUS_SDK_ENVIRONMENT":
    os.environ["GLOBUS_SDK_ENVIRONMENT"] = ENV_VALUE
logger.debug(f"Using {ENV_SWITCHER}={ENV_VALUE} to determine settings")

settings = Dynaconf(
    default_env="production",
    envvar_prefix="TEST",
    settings_files=[CURR_DIR / "settings.toml", CURR_DIR / ".secrets.toml"],
    env_switcher=ENV_SWITCHER,
    environments=True,
    validators=[
        Validator("GLOBUS_AUTH_CLIENT_ID", "GLOBUS_AUTH_CLIENT_SECRET", must_exist=True)
    ],
)
