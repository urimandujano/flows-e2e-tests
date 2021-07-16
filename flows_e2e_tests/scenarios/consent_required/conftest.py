import typing as t

import pytest

from flows_e2e_tests.utils import (
    FlowResponse,
    RunResponse,
    action_provider_url_for_environment,
    flows_client,
)

flow = {
    "StartAt": "HelloState",
    "States": {
        "HelloState": {
            "Type": "Action",
            "ActionUrl": action_provider_url_for_environment(
                "https://actions.automate.globus.org/hello_world"
            ),
            "Parameters": {
                "required_dependent_scope": "urn:globus:auth:scope:groups.api.globus.org:all"
            },
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


@pytest.fixture(scope="module")
def flow_for_tests(request):
    deploy_resp = flows_client.deploy_flow(
        title=f"Integration Test Flow for {request.module.__name__}",
        flow_definition=flow,
        **metadata,
    )
    assert deploy_resp.http_status == 201
    yield FlowResponse(**deploy_resp.data)

    delete_resp = flows_client.delete_flow(deploy_resp.data["id"])
    assert delete_resp.http_status == 200


@pytest.fixture(scope="module")
def run_for_tests(request, flow_for_tests: FlowResponse):
    run_resp = flows_client.run_flow(
        flow_id=flow_for_tests.id,
        flow_scope=flow_for_tests.globus_auth_scope,
        flow_input=flow_input,
        label=f"Integration Test Run for {request.module.__name__}",
    )
    assert run_resp.http_status == 201
    yield RunResponse(**run_resp.data)
