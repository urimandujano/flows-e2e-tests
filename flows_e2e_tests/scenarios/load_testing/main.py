import datetime
import typing as t

import gevent
import locust
import structlog
from locust.env import Environment
from locust.stats import stats_history

from flows_e2e_tests.scenarios.load_testing.users import ActionHttpUser, FlowsHttpUser
from flows_e2e_tests.utils import (
    FlowResponse,
    action_provider_scope,
    action_provider_url_for_environment,
    get_flows_client,
    get_token_for_scope,
)

logger = structlog.getLogger(__name__)


def init_action(*_, **kwargs):
    """
    This runs before ActionHttpUser tests and configures the test with
    properties required to run the load test
    """
    user: t.Type[ActionHttpUser] = kwargs["environment"].user_classes[0]
    user.host = action_provider_url_for_environment(user.action_provider)
    action_scope = action_provider_scope(user.host)
    user.access_token = get_token_for_scope(action_scope)


def deploy_flow(*_, **kwargs):
    """
    This will run first and configure the class with properties required to
    run the load test
    """
    # This will be the class under test
    user: t.Type[FlowsHttpUser] = kwargs["environment"].user_classes[0]
    flows_client = get_flows_client()
    resp = flows_client.deploy_flow(
        title=f"E2E Load Test on {datetime.datetime.utcnow()}",
        flow_definition=user.flow_def,
        input_schema=user.flow_schema,
        flow_starters=["all_authenticated_users"],
    )
    assert resp.http_status == 201

    flow = FlowResponse(**resp.data)
    user.flow_id = flow.id
    user.access_token = get_token_for_scope(flow.globus_auth_scope)
    user.host = flows_client.base_url
    logger.info(f"Created Flow {flow.id} for tests")


def remove_flow(*_, **kwargs):
    user: t.Type[FlowsHttpUser] = kwargs["environment"].user_classes[0]
    flow_id = getattr(user, "flow_id", None)
    if flow_id:
        resp = get_flows_client().delete_flow(flow_id)
        assert resp.http_status == 200
        logger.info(f"Removed Flow {flow_id}")


def start(
    user_class: t.Union[t.Type[FlowsHttpUser], t.Type[ActionHttpUser]],
    n_workers: int = 1,
):
    # monkey patch the locust CLI since it will parse our CLI args and fail
    locust.argument_parser.ui_extra_args_dict = lambda *args, **kwargs: {}
    env = Environment(user_classes=[user_class])

    # Add start/stop hooks to init/remove test state
    if issubclass(user_class, ActionHttpUser):
        env.events.test_start.add_listener(init_action)
    elif issubclass(user_class, FlowsHttpUser):
        env.events.test_start.add_listener(deploy_flow)
        env.events.test_stop.add_listener(remove_flow)

    env.create_local_runner()

    # start a WebUI instance
    env.create_web_ui("127.0.0.1", 8089)
    logger.warning(
        f"Starting web server at http://{env.web_ui.host}:{env.web_ui.port}. Hit CTRL-C to stop load test"
    )

    # start a greenlet that save current stats to history
    gevent.spawn(stats_history, env.runner)

    # start the test
    env.runner.start(n_workers, spawn_rate=10)

    # in 30 seconds stop the runner
    # gevent.spawn_later(30, lambda: env.runner.quit())

    try:
        # wait for the greenlets
        env.runner.greenlet.join()
    except KeyboardInterrupt:
        pass

    env.runner.quit()
    env.runner.greenlet.join()
    # stop the web server for good measures
    env.web_ui.stop()
