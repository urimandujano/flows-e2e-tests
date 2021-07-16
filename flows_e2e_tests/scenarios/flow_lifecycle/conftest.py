import typing as t

import pytest

from flows_e2e_tests.utils import FlowResponse, flows_client

flow_definition = {
    "StartAt": "PassState",
    "States": {
        "PassState": {
            "Type": "Pass",
            "ResultPath": "$.FlowResult",
            "End": True,
        }
    },
}

flow_input: t.Dict[str, t.Any] = {}

metadata = {
    "input_schema": {"additionalProperties": False},
    # "flow_administrators": [],
    # "flow_starters": [],
    # "flow_viewers": [],
    "keywords": [],
}


@pytest.fixture(scope="function")
def flow_for_one_test(request):
    deploy_resp = flows_client.deploy_flow(
        title=f"Integration Test Flow for {request.module.__name__}",
        flow_definition=flow_definition,
        **metadata,
    )
    assert deploy_resp.http_status == 201
    yield FlowResponse(**deploy_resp.data)


@pytest.fixture(scope="module")
def flow_for_tests(request):
    deploy_resp = flows_client.deploy_flow(
        title=f"Integration Test Flow for {request.module.__name__}",
        flow_definition=flow_definition,
        **metadata,
    )
    assert deploy_resp.http_status == 201
    yield (flow := FlowResponse(**deploy_resp.data))

    delete_resp = flows_client.delete_flow(flow.id)
    assert delete_resp.http_status == 200
