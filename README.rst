Flows E2E Tests
---------------

This is a project for running integration tests against a particular Flows
service deployment. This project aims to be simple to install, configure and
use. It contains no Globus secrets and therefore is suitable for public view and
usage.

Installation
============

`pip install globus-flows-e2e-tests`

Usage
=====

If storing the configuration in environment variable in the file `.env`: `source
.env && globus-flows-e2e-tests`

Configuration
=============

The base configuration is stored in
`flows_e2e_tests/config/settings.toml`. This package relies on
environment variables to determine its runtime configuration as well as to use
runtime secrets.

Environment variables:

FLOWS_TEST_ENVIRONMENT
    - purpose:
        Used to select the Flows environment to run tests against. This value is
        also used to set the `GLOBUS_SDK_ENVIRONMENT` variable which allows the
        Automate SDK to function against the different environments.
    - values: production, integration, sandbox, etc.

TEST_GLOBUS_AUTH_CLIENT_ID
    - purpose:
        The Globus Auth client ID which will be used to run the tests. This
        client should be a confidential client capabable of consenting to scopes
        dynamically. Care should be taken to ensure that the client used for
        testing exists in the target test environment. Note that although you
        can set this as an environment variable, you usually want to use the
        client ID defined in the package's config.
    - values: uuid

TEST_GLOBUS_AUTH_CLIENT_SECRET
    - purpose:
        The Globus Auth client ID's secret which is used to authenticate
        requests. This package makes no assumptions about how the secret got
        into the running environment. Care should be taken to ensure that the
        secret used for testing exists in the target test environment.
    - values: secret

Creating a Client or Secrets in an Auth Environment
===================================================

Go to the developer page for the Auth environment the client will exist in. The
portal follows the pattern of:
`https://auth.{environment_name}.globuscs.info/v2/web/developers`. Once there,
go to the `Automate` project and locate or create a client called `Flows
Integration Testing`. Note its ID and create a secret for the environment.

Adding Tests
============

If a test does not logically fit in one of the existing scenarios, add a new
scenario. Each scenario should be self contained and define its own resources in
a conftest. Slow tests should use the `@pytest.mark.slow` decorator.
