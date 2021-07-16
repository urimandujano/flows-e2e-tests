from flows_e2e_tests.utils import FlowResponse, flows_client


def test_deployed_flow_can_be_retrieved(flow_for_tests: FlowResponse):
    get_resp = flows_client.get_flow(flow_for_tests.id)
    assert get_resp.http_status == 200

    for key in [
        "id",
        "definition",
        "globus_auth_username",
        "input_schema",
    ]:
        assert get_resp.data[key] == getattr(flow_for_tests, key), get_resp.data


def test_get_flow_conforms_to_schema(flow_for_tests: FlowResponse):
    get_resp = flows_client.get_flow(flow_for_tests.id)
    assert get_resp.http_status == 200
    FlowResponse(**get_resp.data)
