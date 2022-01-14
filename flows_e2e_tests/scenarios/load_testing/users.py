import typing as t
from uuid import UUID

from locust import HttpUser, task

from flows_e2e_tests.utils import action_provider_url_for_environment
from flows_e2e_tests.utils.auth import get_token_for_scope


class FlowsHttpUser(HttpUser):
    host: str
    flow_def: t.Dict[str, t.Any]
    flow_schema: t.Dict[str, t.Any]
    flow_id: str
    access_token: str


class ActionHttpUser(HttpUser):
    host: str
    access_token: str


class HelloWorldUser(ActionHttpUser):
    """
    Run the Hello World AP continuously with health checks.
    """

    action_provider = "hello_world"
    payload: t.Dict[str, t.Any] = {}

    # These get set during test setup
    host: str = ""
    access_token: str = ""

    @task(20)
    def run_action(self):
        self.client.post(
            f"/run",
            json={"request_id": str(UUID(int=0)), "body": self.payload},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

    @task(1)
    def sporadic_health_check(self):
        self.client.get("/")


class PassFlowUser(FlowsHttpUser):
    """
    Run a Flow with a single Pass state with health checks.
    """

    flow_def = {
        "StartAt": "PassState",
        "States": {
            "PassState": {
                "End": True,
                "Parameters": {"Completed": True},
                "ResultPath": "$.Output",
                "Type": "Pass",
            }
        },
    }
    flow_schema = {"additionalProperties": False}

    # These get set during test setup
    host = ""
    flow_id: str = ""
    access_token: str = ""

    @task(20)
    def run_flow(self):
        self.client.post(
            f"/{self.flow_id}/run",
            json={"request_id": str(UUID(int=0)), "body": {}},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

    @task(1)
    def sporadic_health_check(self):
        self.client.get("/healthcheck")


"""
class RunAndEnumerateUser(FlowsHttpUser):

    Run many Flows that will stay in an Active state and poll the enumeration
    endpoint.


    flow_def = {
        "StartAt": "SleepingHelloWorld",
        "States": {
            "SleepingHelloWorld": {
                "ActionUrl": action_provider_url_for_environment("hello_world"),
                "End": True,
                "Parameters": {
                    "echo_string": "Hello Globus Automate!",
                    "sleep_time": 300,
                },
                "ResultPath": "$.Output",
                "Type": "Action",
            }
        },
    }
    flow_schema = {"additionalProperties": False}

    # These get set during test setup
    host = ""
    flow_id: str = ""
    access_token: str = ""
    enumerate_access_token: t.Optional[str] = None

    @task(5)
    def run_flow(self):
        self.client.post(
            f"/{self.flow_id}/run",
            json={"request_id": str(UUID(int=0)), "body": {}},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

    @task(1)
    def sporadic_health_check(self):
        self.client.get("/healthcheck")

    @task(1)
    def sporadic_run_enumeration(self):
        if self.enumerate_access_token is None:
            self.enumerate_access_token = get_token_for_scope(
                "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run_status"
            )

        self.client.get(
            "/runs", headers={"Authorization": f"Bearer {self.enumerate_access_token}"}
        )
"""
