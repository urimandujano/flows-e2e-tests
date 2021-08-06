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

Store the configuration in a safe place. Keep in mind that exports on the command
line are usually stored in your shell's history. It's recommended to store the
configuration a file called `.env`. This file is automatically loaded when the
package is run.

It is also possible to run the tests directly from this git repository:

.. code-block:: bash

    poetry install && poetry run globus-flows-e2e-tests


Slow tests can be skipped by running:

.. code-block:: bash

    globus-flows-e2e-tests --no-slow
        OR
    poetry run globus-flows-e2e-tests --no-slow

Configuration
=============

The base configuration is stored in
`flows_e2e_tests/config/settings.toml`. This package relies on
environment variables to determine its runtime configuration as well as to use
runtime secrets.

Environment variables
*********************

FLOWS_TEST_ENVIRONMENT
^^^^^^^^^^^^^^^^^^^^^^
    purpose: Used to select the Flows environment to run tests against. This value is
        also used to set the `GLOBUS_SDK_ENVIRONMENT` variable which allows the
        Automate SDK to function against the different environments.
    values: production, integration, sandbox, etc.

TEST_GLOBUS_AUTH_CLIENT_ID
^^^^^^^^^^^^^^^^^^^^^^^^^^
    purpose: The Globus Auth client ID which will be used to run the tests. This
        client should be a confidential client capabable of consenting to scopes
        dynamically. Care should be taken to ensure that the client used for
        testing exists in the target test environment. Note that although you
        can set this as an environment variable, you usually want to use the
        client ID defined in the package's config.
    values: uuid

TEST_GLOBUS_AUTH_CLIENT_SECRET
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    purpose: The Globus Auth client ID's secret which is used to authenticate
        requests. This package makes no assumptions about how the secret got
        into the running environment. Care should be taken to ensure that the
        secret used for testing exists in the target test environment.
    values: secret

.env file
*********

To simplify interactive use and remove the need to export senstive secrets on
the command line (which may be stored in your shell's history), this package
will automatically attempt to load a file named `.env` in the directory from
which it's run. This file should be in `KEY=VALUE` format where the KEY is one 
of the environment variables above.

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
