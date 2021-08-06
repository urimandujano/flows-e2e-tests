import datetime
import typing as t

from pydantic import BaseModel, Field, validator

uuid_regex = (
    "([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
)
auth_id_urn_regex = f"^urn:globus:auth:identity:{uuid_regex}$"
principal_urn_regex = f"^urn:globus:(auth:identity|groups:id):{uuid_regex}$"


class FlowResponse(BaseModel):
    id: str = Field(regex=uuid_regex)
    api_version: t.Literal["1.0"]
    created_at: datetime.datetime
    definition: t.Dict[str, t.Any]
    description: str
    flow_administrators: t.List[str]
    flow_owner: str = Field(regex=auth_id_urn_regex)
    flow_starters: t.List[str]
    flow_url: str
    flow_viewers: t.List[str]
    globus_auth_scope: str
    globus_auth_username: str
    # If the Flow doesn't have an input schema defined it will be removed from
    # the output, so default it here
    input_schema: t.Dict[str, t.Any] = {}
    keywords: t.List[str]
    log_supported: bool
    principal_urn: str = Field(regex=auth_id_urn_regex)
    subtitle: str
    synchronous: bool
    title: str
    types: t.List[str]
    updated_at: datetime.datetime
    user_role: t.Literal[
        "flow_owner", "flow_starter", "flow_administrator", "flow_viewer"
    ]

    @validator("globus_auth_scope")
    def validate_scope(cls, v, values, **kwargs):
        flow_id = values["id"]
        if (
            v
            != f"https://auth.globus.org/scopes/{flow_id}/flow_{flow_id.replace('-', '_')}_user"
        ):
            raise ValueError(f"Invalid Globus Auth scope {v}")
        return v

    @validator("globus_auth_username")
    def validate_username(cls, v, values, **kwargs):
        flow_id = values["id"]
        if v != f"{flow_id}@clients.auth.globus.org":
            raise ValueError(f"Invalid Globus Auth username {v}")
        return v

    @validator("flow_url")
    def validate_url(cls, v, values, **kwargs):
        flow_id = values["id"]
        if (
            not v.endswith(f"flows.automate.globus.org/flows/{flow_id}")
            and not v.endswith(f"flows.automate.globus.org/{flow_id}")
            and not v.endswith(f"flows.globus.org/flows/{flow_id}")
            and not v.endswith(f"flows.globus.org/{flow_id}")
        ):
            raise ValueError(f"Invalid Flow URL {v}")
        return v


class RunResponse(BaseModel):
    run_id: str = Field(regex=uuid_regex)
    completion_time: t.Optional[datetime.datetime]
    details: t.Dict[str, t.Any]
    display_status: str
    flow_last_updated: t.Optional[datetime.datetime]
    flow_deleted_at: t.Optional[datetime.datetime] = None
    run_managers: t.List[str] = Field(regex=principal_urn_regex)
    run_monitors: t.List[str] = Field(regex=principal_urn_regex)
    run_owner: str = Field(regex=auth_id_urn_regex)
    start_time: datetime.datetime
    status: t.Literal["ACTIVE", "INACTIVE", "FAILED", "SUCCEEDED"]
    user_role: t.Literal["run_owner", "run_monitor", "run_manager"]

    @validator("completion_time", pre=True)
    def validate_completion_time(cls, v):
        """
        The API returns 'None' as a completion time when the Run is incomplete.
        Help pydantic parse that as None.
        """
        if v == str(None):
            return None
        return v
