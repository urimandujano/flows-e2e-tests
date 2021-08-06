import argparse
import uuid

import pytest
import structlog

from flows_e2e_tests.config import settings
from flows_e2e_tests.utils import flows_client

logger = structlog.get_logger(__name__)


def run_tests():
    parser = argparse.ArgumentParser(description="Run Flows E2E tests")
    parser.add_argument("--no-slow", action="store_true", help="Don't run slow tests")
    parser.add_argument(
        "--debug", action="store_true", help="Display discovered test settings"
    )
    args = parser.parse_args()

    if args.debug:
        print(f"Loaded settings={settings.censored}")
    elif args.no_slow:
        pytest.main(["-m not slow"])
    else:
        pytest.main()


def delete_flow():
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
