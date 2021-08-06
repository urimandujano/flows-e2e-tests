import os
from pathlib import Path

import structlog
from dynaconf import Validator

from .custom import CensoredDynaconf

logger = structlog.get_logger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent
EXECUTION_DIR = Path.cwd()
logger.debug(f"Reading base settings at {PROJECT_DIR}")
logger.debug(f"Searching for overrides at {EXECUTION_DIR}/.env")

ENV_SWITCHER = "FLOWS_TEST_ENVIRONMENT"
ENV_VALUE = os.getenv(ENV_SWITCHER, "production")
if ENV_SWITCHER != "GLOBUS_SDK_ENVIRONMENT":
    os.environ["GLOBUS_SDK_ENVIRONMENT"] = ENV_VALUE
logger.debug(f"Using {ENV_SWITCHER}={ENV_VALUE} to determine settings")


settings = CensoredDynaconf(
    default_env="production",
    envvar_prefix="TEST",
    settings_files=[
        PROJECT_DIR / "settings.toml",
        PROJECT_DIR / ".secrets.toml",
    ],
    dotenv_path=EXECUTION_DIR,
    load_dotenv=True,
    env_switcher=ENV_SWITCHER,
    ignore_unknown_envvars=True,
    environments=True,
    validators=[
        Validator("GLOBUS_AUTH_CLIENT_ID", "GLOBUS_AUTH_CLIENT_SECRET", must_exist=True)
    ],
)
