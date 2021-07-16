import structlog
from globus_automate_client import create_flows_client
from globus_automate_client.flows_client import MANAGE_FLOWS_SCOPE
from globus_sdk.authorizers import RefreshTokenAuthorizer

from .auth import authorizer_for_scope

logger = structlog.get_logger(__name__)


def authorizer_retriever(*args, flow_scope: str, **kwargs) -> RefreshTokenAuthorizer:
    return authorizer_for_scope(flow_scope)


flows_client = create_flows_client(
    base_url=None,
    authorizer=authorizer_retriever(flow_scope=MANAGE_FLOWS_SCOPE),
    authorizer_callback=authorizer_retriever,
)
logger.debug(f"Initialized Flows Client at {flows_client.base_url}")
