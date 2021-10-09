import typing as t

import pytest

from flows_e2e_tests.utils import FlowResponse, RunResponse, get_flows_client

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


@pytest.fixture(scope="module")
def flow_with_runs(request):
    flows_client = get_flows_client()
    deploy_resp = flows_client.deploy_flow(
        title=f"Integration Test Flow for {request.module.__name__}",
        flow_definition=flow_definition,
        **metadata,
    )
    assert deploy_resp.http_status == 201
    flow = FlowResponse(**deploy_resp.data)

    runs: t.List[RunResponse] = []
    for _ in range(1):
        run_resp = flows_client.run_flow(
            flow_id=flow.id,
            flow_scope=flow.globus_auth_scope,
            flow_input=flow_input,
            label=f"Integration Test Run for {request.module.__name__}",
        )
        assert run_resp.http_status == 201
        run = RunResponse(**run_resp.data)
        runs.append(run)

    delete_resp = flows_client.delete_flow(flow.id)
    assert delete_resp.http_status == 200
    yield flow, runs
