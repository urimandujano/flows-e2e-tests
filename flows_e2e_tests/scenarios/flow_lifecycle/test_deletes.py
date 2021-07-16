import pytest
from globus_sdk import GlobusAPIError

from flows_e2e_tests.utils import FlowResponse, flows_client


def test_flow_delete_succeeds(flow_for_one_test: FlowResponse):
    del_resp = flows_client.delete_flow(flow_for_one_test.id)

    assert del_resp.http_status == 200
    with pytest.raises(GlobusAPIError) as err:
        flows_client.get_flow(flow_for_one_test.id)
    assert err.value.http_status == 404
