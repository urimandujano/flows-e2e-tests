import typing as t

import pytest
from globus_sdk.exc import GlobusAPIError

from flows_e2e_tests.utils import (
    FlowResponse,
    RunResponse,
    authorizer_for_scope,
    get_flows_client,
    scopes,
)

from .conftest import flow_input


def test_runs_persist_after_flow_delete(
    flow_with_runs: t.Tuple[FlowResponse, t.List[RunResponse]],
):
    flow, runs = flow_with_runs
    authz = authorizer_for_scope(scopes.FLOWS_RUN_STATUS)
    response = get_flows_client().enumerate_actions(
        filters={"filter_flow_id": flow.id}, authorizer=authz
    )

    run_ids = [r.run_id for r in runs]
    for r_resp in response.data["runs"]:
        r = RunResponse(**r_resp)
        assert r.run_id in run_ids
        assert r.flow_deleted_at is not None


def test_run_operations_work_after_delete(
    flow_with_runs: t.Tuple[FlowResponse, t.List[RunResponse]]
):
    flow, runs = flow_with_runs

    flows_client = get_flows_client()
    response = flows_client.flow_action_status(
        flow.id, flow.globus_auth_scope, runs[0].run_id
    )
    assert response.http_status == 200, response.data

    response = flows_client.flow_action_log(
        flow.id, flow.globus_auth_scope, runs[0].run_id
    )
    assert response.http_status == 200, response.data

    response = flows_client.flow_action_resume(
        flow.id, flow.globus_auth_scope, runs[0].run_id
    )
    assert response.http_status == 200, response.data

    response = flows_client.flow_action_cancel(
        flow.id, flow.globus_auth_scope, runs[0].run_id
    )
    assert response.http_status == 202, response.data

    response = flows_client.flow_action_release(
        flow.id, flow.globus_auth_scope, runs[0].run_id
    )
    assert response.http_status == 200, response.data


def test_flow_cannot_be_retrieved_after_delete(
    flow_with_runs: t.Tuple[FlowResponse, t.List[RunResponse]]
):
    flow, _ = flow_with_runs
    with pytest.raises(GlobusAPIError) as err:
        get_flows_client().get_flow(flow.id)
    assert err.value.http_status == 404


def test_flow_cannot_be_run_after_delete(
    flow_with_runs: t.Tuple[FlowResponse, t.List[RunResponse]]
):
    flow, _ = flow_with_runs
    with pytest.raises(GlobusAPIError) as err:
        get_flows_client().run_flow(
            flow.id, flow_scope=flow.globus_auth_scope, flow_input=flow_input
        )
    assert err.value.http_status == 404


def test_flow_cannot_be_removed_after_delete(
    flow_with_runs: t.Tuple[FlowResponse, t.List[RunResponse]]
):
    flow, _ = flow_with_runs
    with pytest.raises(GlobusAPIError) as err:
        get_flows_client().delete_flow(flow.id)
    assert err.value.http_status == 404


def test_flow_is_not_listed_after_delete(
    flow_with_runs: t.Tuple[FlowResponse, t.List[RunResponse]]
):
    flow, _ = flow_with_runs
    response = get_flows_client().list_flows()
    for f in response.data["flows"]:
        f = FlowResponse(**f)
        assert f.id != flow.id


def test_flow_cannot_be_updated_after_delete(
    flow_with_runs: t.Tuple[FlowResponse, t.List[RunResponse]]
):
    flow, _ = flow_with_runs
    with pytest.raises(GlobusAPIError) as err:
        get_flows_client().update_flow(flow.id, title="Updated Flow Title")
    assert err.value.http_status == 404
