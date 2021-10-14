import typing as t
import uuid
from pathlib import Path

import pytest
import structlog
import typer

from flows_e2e_tests.config import get_settings
from flows_e2e_tests.scenarios.load_testing import start
from flows_e2e_tests.scenarios.load_testing.users import HelloWorldUser, PassFlowUser
from flows_e2e_tests.utils import get_flows_client

logger = structlog.getLogger(__name__)

app = typer.Typer()


def version_callback(display: bool):
    if display:
        from flows_e2e_tests import __version__

        print(f"Globus Flows E2E Tests v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        help="Print CLI version number and exit",
        is_eager=True,
    ),
):
    pass


@app.command()
def e2e(
    tests: t.Optional[t.List[str]] = typer.Argument(
        None,
        help="Only run a subset of tests as specified by a given pattern. "
        "Tests matching at least one pattern will be run.",
    ),
    skip_slow: bool = typer.Option(
        False, "--skip-slow", show_default=True, help="Skip long-running tests"
    ),
    parallel: bool = typer.Option(
        False, "--parallel", show_default=True, help="Run tests in parallel"
    ),
    print_config: bool = typer.Option(
        False, "--print-config", help="Display discovered test settings"
    ),
):
    pytest_args = []
    if skip_slow:
        pytest_args.append("-m not slow")
    if parallel:
        pytest_args.append("-n 2")

    if tests:
        pytest_args.append(f"-k {' or '.join(tests)}")
    else:
        test_dir = str(Path(__file__).resolve().parent.parent)
        pytest_args.append(test_dir)

    if print_config:
        settings = get_settings()
        typer.secho(f'Settings for "{settings.current_env}": {settings.sanitized}')
        typer.secho(f"Would invoke pytest as 'pytest {' '.join(pytest_args)}'")
        raise typer.Exit()

    pytest.main(pytest_args)


load_tests = {
    PassFlowUser.__name__: PassFlowUser,
    HelloWorldUser.__name__: HelloWorldUser,
}


def complete_load_tests(incomplete: str):
    tests = []
    for name, cls in load_tests.items():
        tests.append((name, cls.__doc__))

    matches = []
    for t in tests:
        name, _ = t
        if name.startswith(incomplete):
            matches.append(t)
    return matches


def load_test_validator(ctx: typer.Context, test_name: str) -> str:
    # Check if this is doing autocompletion
    if ctx.resilient_parsing:
        return  # type: ignore

    test = load_tests.get(test_name)
    if test is None:
        typer.secho(
            f"Invalid test chosen. Choose one of {list(load_tests.keys())}", fg="red"
        )
        raise typer.Exit()
    return test_name


@app.command()
def load(
    test: str = typer.Option(
        ...,
        help="Specify a load test to run",
        autocompletion=complete_load_tests,
        callback=load_test_validator,
    ),
    users: int = typer.Option(
        1,
        min=1,
        help="If set, load tests will be performed with this many users",
    ),
):
    settings = get_settings()
    if settings.current_env == "production":
        logger.error("Run load tests against production, you will not")
        raise SystemExit()

    load_scenario = load_tests.get(test)
    start(load_scenario, users)
    raise typer.Exit()


@app.command()
def rm_flow(
    flow_ids: t.List[uuid.UUID] = typer.Argument(
        ..., help="One of more Flow IDs to remove from the Flow's service"
    )
):
    flows_client = get_flows_client()
    for f_id in flow_ids:
        flows_client.delete_flow(f_id)

    typer.secho(f"Deleted Flow(s) with ID(s) {flow_ids}")


if __name__ == "__main__":
    app()
