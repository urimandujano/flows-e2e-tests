import os
from pathlib import Path

import structlog
from dynaconf import Validator

from .custom import CensoredDynaconf

logger = structlog.get_logger(__name__)

ENV_SWITCHER = "E2E_TESTS_FLOWS_ENV"
PROJECT_DIR = Path(__file__).resolve().parent
VALID_TEST_ENVS = [
    "production",
    "integration",
    "test",
    "sandbox",
    "preview",
    "staging",
]


logger.debug(f"Tests will load base settings from {__package__}")
dotenv_found = (Path.cwd() / ".env").exists()
if dotenv_found:
    logger.debug(f"Tests will load custom settings from .env")

TARGET_ENV = os.environ.get(ENV_SWITCHER, "production")

assert (
    TARGET_ENV in VALID_TEST_ENVS
), f"Invalid value for {ENV_SWITCHER}: {TARGET_ENV}, must be one of {VALID_TEST_ENVS}"
os.environ[ENV_SWITCHER] = TARGET_ENV
os.environ["GLOBUS_SDK_ENVIRONMENT"] = TARGET_ENV
logger.debug(f'Target test environment is "{TARGET_ENV}"')

settings = CensoredDynaconf(
    environments=True,
    default_env="defaults",
    env_switcher=ENV_SWITCHER,
    envvar_prefix="E2E_TESTS",
    settings_files=[
        PROJECT_DIR / "settings.toml",
        PROJECT_DIR / ".secrets.toml",
    ],
    load_dotenv=dotenv_found,
    dotenv_path=Path.cwd(),
    validators=[
        Validator(
            "GLOBUS_AUTH_CLIENT_SECRET",
            "GLOBUS_AUTH_CLIENT_ID",
            must_exist=True,
        )
    ],
)
