import structlog
from globus_automate_client import create_flows_client
from globus_automate_client.flows_client import MANAGE_FLOWS_SCOPE
from globus_sdk import GlobusAPIError
from globus_sdk.authorizers import RefreshTokenAuthorizer

from flows_e2e_tests.config import settings

from .auth import authorizer_for_scope

logger = structlog.get_logger(__name__)


def authorizer_retriever(*args, flow_scope: str, **kwargs) -> RefreshTokenAuthorizer:
    return authorizer_for_scope(flow_scope)


try:
    flows_client = create_flows_client(
        base_url=None,
        authorizer=authorizer_retriever(flow_scope=MANAGE_FLOWS_SCOPE),
        authorizer_callback=authorizer_retriever,
        http_timeout=10,
    )
except GlobusAPIError as err:
    logger.exception("Unable to create a FlowsClient", settings=settings.censored())
    raise SystemExit from err
else:
    logger.debug(f"Initialized Flows Client at {flows_client.base_url}")
