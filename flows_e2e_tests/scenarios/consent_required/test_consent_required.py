import time

import pytest

from flows_e2e_tests.config import settings
from flows_e2e_tests.utils import FlowResponse, RunResponse, flows_client


@pytest.mark.slow
def test_run_with_consent_required_can_resume_to_completion(
    flow_for_tests: FlowResponse, run_for_tests: RunResponse
):
    # Wait for the Run to become inactive
    for _ in range(settings.max_wait_time):
        run_status_resp = flows_client.flow_action_status(
            flow_id=flow_for_tests.id,
            flow_scope=flow_for_tests.globus_auth_scope,
            flow_action_id=run_for_tests.run_id,
        )
        if (
            run_status_resp.data["status"] == "INACTIVE"
            and run_status_resp.data["details"]["code"] == "ConsentRequired"
        ):
            consent_scope = run_status_resp["details"]["required_scope"]
            break
        time.sleep(1)
    else:
        # We only execute this if the Action never reaches its INACTIVE state by
        # the time max_wait_time has elapsed
        assert False, "Action never reached INACTIVE state due to ConsentRequired"

    # Attempt to resume the Run with updated consents
    resume_resp = flows_client.flow_action_resume(
        flow_id=flow_for_tests.id,
        flow_scope=consent_scope,
        flow_action_id=run_for_tests.run_id,
    )
    assert resume_resp.http_status == 200
    assert resume_resp.data["status"] == "ACTIVE"

    # Wait for the Run to complete
    for _ in range(settings.max_wait_time):
        run_status_resp = flows_client.flow_action_status(
            flow_id=flow_for_tests.id,
            flow_scope=flow_for_tests.globus_auth_scope,
            flow_action_id=run_for_tests.run_id,
        )
        if run_status_resp.data["status"] == "SUCCEEDED":
            break
        time.sleep(1)
    else:
        # We only execute this if the Action never reaches its INACTIVE state by
        # the time max_wait_time has elapsed
        assert False, "Action never reached ACTIVE state after resuming"

    assertions = (
        run_status_resp.data["status"] == "SUCCEEDED"
        and run_status_resp.data["completion_time"] is not None
        and run_status_resp.data["details"]["code"] == "FlowSucceeded"
    )
    assert assertions, run_status_resp.data
