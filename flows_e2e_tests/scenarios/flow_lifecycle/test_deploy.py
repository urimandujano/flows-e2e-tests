from flows_e2e_tests.utils import FlowResponse, get_auth_client

from .conftest import metadata


def test_deployed_flow_has_correct_rbac(flow_for_tests: FlowResponse):
    assert flow_for_tests.user_role == "flow_owner"
    assert (
        flow_for_tests.flow_owner
        == f"urn:globus:auth:identity:{get_auth_client().client_id}"
    )


def test_deployed_flow_has_correct_metadata(flow_for_tests: FlowResponse):
    for key, value in metadata.items():
        assert getattr(flow_for_tests, key) == value
