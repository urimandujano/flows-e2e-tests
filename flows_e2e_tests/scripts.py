import argparse
import uuid

import pytest
import structlog

logger = structlog.get_logger(__name__)


def run_tests():
    parser = argparse.ArgumentParser(description="Run Flows E2E tests")
    parser.add_argument("--no-slow", action="store_true", help="Don't run slow tests")
    parser.add_argument(
        "--debug", action="store_true", help="Display discovered test settings"
    )
    parser.add_argument("--version", action="store_true", help="Display tests version")
    args = parser.parse_args()

    if args.debug:
        from flows_e2e_tests.config import settings

        print(f'Settings for "{settings.current_env}": {settings.sanitized}')
    elif args.version:
        from flows_e2e_tests import __version__

        print(f"Globus Flows E2E Tests v{__version__}")
    else:
        pytest_args = []
        if args.no_slow:
            pytest_args.append("-m not slow")
        pytest_args.append("-n 2")
        pytest.main(pytest_args)


def delete_flow():
    from flows_e2e_tests.utils import flows_client

    parser = argparse.ArgumentParser(description="Delete one or more Flows")
    parser.add_argument(
        "flow_ids",
        metavar="FLOW_ID",
        type=uuid.UUID,
        nargs="+",
    )
    args = parser.parse_args()
    for f_id in args.flow_ids:
        flows_client.delete_flow(f_id)

    logger.info(f"Deleted Flow(s) with ID(s) {args.flow_ids}")
