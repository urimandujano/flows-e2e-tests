from flows_e2e_tests.utils import FlowResponse, auth_client, flows_client

from .conftest import flow_input


def test_deployed_flow_can_be_run_by_creator(flow_for_tests: FlowResponse):
    run_resp = flows_client.run_flow(
        flow_for_tests.id,
        flow_scope=flow_for_tests.globus_auth_scope,
        flow_input=flow_input,
    )
    assert run_resp.http_status == 201
    assert (
        run_resp.data["created_by"]
        == f"urn:globus:auth:identity:{auth_client.client_id}"
    )
