import typing as t
from uuid import UUID

from locust import HttpUser, task


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
