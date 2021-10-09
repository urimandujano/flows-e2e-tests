import typing as t

import structlog
from globus_sdk import ConfidentialAppAuthClient
from globus_sdk.auth.token_response import OAuthTokenResponse
from globus_sdk.authorizers import RefreshTokenAuthorizer

from flows_e2e_tests.config import get_settings

logger = structlog.get_logger(__name__)


def get_auth_client() -> ConfidentialAppAuthClient:
    settings = get_settings()
    auth_client = ConfidentialAppAuthClient(
        settings.globus_auth_client_id, settings.globus_auth_client_secret
    )
    logger.debug(f"Initialized Auth Client at {auth_client.base_url}")
    return auth_client


def authorizers_by_scope(scopes: t.List[str]) -> t.Dict[str, RefreshTokenAuthorizer]:
    authzs: t.Dict[str, RefreshTokenAuthorizer] = {}
    auth_client = get_auth_client()
    response: OAuthTokenResponse = auth_client.oauth2_client_credentials_tokens(
        " ".join(scopes)
    )
    for s in scopes:
        base_scope = _get_base_scope(s)
        tokens = response.by_scopes[base_scope]
        auth = RefreshTokenAuthorizer(
            auth_client=auth_client,
            refresh_token=tokens["refresh_token"],
            access_token=tokens["access_token"],
            expires_at=tokens["expires_at_seconds"],
        )
        authzs[s] = authzs[base_scope] = auth
    return authzs


def _get_base_scope(scope: str):
    if "[" in scope:
        return scope.split("[")[0]
    return scope


def authorizer_for_scope(scope: str) -> RefreshTokenAuthorizer:
    return authorizers_by_scope([scope]).get(scope)


def get_token_for_scope(scope: str) -> str:
    return authorizer_for_scope(scope).access_token
