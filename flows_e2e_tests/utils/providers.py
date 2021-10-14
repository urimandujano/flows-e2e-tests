import structlog
from globus_automate_client import ActionClient

from flows_e2e_tests.config import get_settings

logger = structlog.getLogger(__name__)


def action_provider_url_for_environment(s: str) -> str:
    """
    Given a Url extension, construct the AP Url
    """
    settings = get_settings()

    if settings.current_env == "production":
        url = f"https://actions.automate.globus.org/{s}"
    else:
        url = f"https://{settings.current_env}.actions.automate.globus.org/{s}"
    logger.info(f"Using URL {url} for Action Provider {s}")
    return url


def action_provider_scope(ap_url: str) -> str:
    return ActionClient.new_client(ap_url, None).action_scope
