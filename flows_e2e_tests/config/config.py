import os
from pathlib import Path

import structlog
from dynaconf import Validator

from .custom import CensoredDynaconf

PROJECT_DIR = Path(__file__).resolve().parent
ENV_SWITCHER = "E2E_TESTS_FLOWS_ENV"
TARGET_ENV = os.environ.get(ENV_SWITCHER, "production")
assert TARGET_ENV in [
    "production",
    "integration",
    "test",
    "sandbox",
    "preview",
    "staging",
], f"Invalid value for {ENV_SWITCHER}: {TARGET_ENV}"

logger = structlog.get_logger(__name__)

logger.debug(f"Using base config at {__package__}")
if (Path.cwd() / ".env").exists():
    logger.debug(f"Using settings in .env file")

settings = CensoredDynaconf(
    environments=True,
    default_env="defaults",
    env=TARGET_ENV,
    envvar_prefix="E2E_TESTS",
    settings_files=[
        PROJECT_DIR / "settings.toml",
        PROJECT_DIR / ".secrets.toml",
    ],
    load_dotenv=True,
    validators=[
        Validator(
            "GLOBUS_AUTH_CLIENT_SECRET",
            "GLOBUS_AUTH_CLIENT_ID",
            must_exist=True,
        )
    ],
)

os.environ["GLOBUS_SDK_ENVIRONMENT"] = TARGET_ENV
logger.debug(f'Target test environment is "{settings.current_env}"')
