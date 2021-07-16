from flows_e2e_tests.utils import FlowResponse, flows_client


def test_deployed_flow_can_get_updated_by_creator(flow_for_tests: FlowResponse):
    updated_def = flow_for_tests.definition
    updated_def["Comment"] = "This comment was updated"

    updates = {
        "flow_definition": updated_def,
        "title": "This title was updated",
        "subtitle": "This subtitle was updated",
        "description": "This description was updated",
    }
    update_resp = flows_client.update_flow(flow_for_tests.id, **updates)
    assert update_resp.http_status == 200
    for key, value in updates.items():
        # The SDK kwarg is flow_definition but the API's return value is
        # definition, standardize the key so that we only look for definition.
        if key == "flow_definition":
            key = key.strip("flow_")
        assert update_resp.data[key] == value
