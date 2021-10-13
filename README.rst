Flows E2E Tests
---------------

This is a project for running end to end tests against a particular Flows
service deployment. This project aims to be simple to install, configure and
use. It contains no Globus secrets and therefore is suitable for public view and
usage.

Installation
============

The preferred installation is via pipx:

.. code-block:: bash
    
    pipx install flows-e2e-tests

But pip can work too:

.. code-block:: bash

    pip install flows-e2e-tests

It is also possible to install these tests directly from this git repository:

.. code-block:: bash

    git clone git@github.com:urimandujano/flows-e2e-tests.git
    cd flows-e2e-tests && poetry install

Configuration
=============

This package relies on environment variables [listed below] to determine its
runtime configuration. Most use cases will only require setting the Flows
environment and Globus Auth client secret variables. The base configuration is
stored in ``flows_e2e_tests/config/settings.toml``. 

Environment variables
*********************

E2E_TESTS_FLOWS_ENV
^^^^^^^^^^^^^^^^^^^
- purpose
  
  Used to select the Flows environment to run tests against. This value is
  also sets the ``GLOBUS_SDK_ENVIRONMENT`` variable which allows the
  Automate SDK to function against the different environments. This
  environment variable must be set manually and will not be read from a
  .env file.

- values

  - production
  - integration
  - sandbox
  - preview
  - staging
  - test

- default

  production

E2E_TESTS_GLOBUS_AUTH_CLIENT_ID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- purpose

  The Globus Auth client ID which will be used to run the tests. This
  client should be a confidential client capabable of consenting to scopes
  dynamically. Care should be taken to ensure that the client used for
  testing exists in the target test environment. Note that although you
  can set this as an environment variable or in a .env file, you usually
  want to use the client ID defined in the package's config.

- values: 

  - some uuid

- default: 

  environment specific client ID

E2E_TESTS_GLOBUS_AUTH_CLIENT_SECRET
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- purpose

  The Globus Auth client ID's secret which is used to authenticate
  requests. Be sure that the secret used for testing exists in the target
  test environment.

- values

  - secret

- default
    
  none

.env file
*********

To simplify interactive use and remove the need to export sensitive secrets on
the command line (which may be stored in your shell's history), this package
will automatically attempt to load a file named ``.env`` in the directory from
which it's run. This file should be in ``KEY=VALUE`` format where the ``KEY`` is
one of the environment variables above. This file **SHOULD NOT** define the
``E2E_TESTS_FLOWS_ENV`` variable as it will not be read from this file.

Below is an example of what the .env file may look like:

.. code-block:: bash

   E2E_TESTS_GLOBUS_AUTH_CLIENT_SECRET=$uper$ecret$auce
   E2E_TESTS_GLOBUS_AUTH_CLIENT_ID=00000000-0000-0000-0000-000000000000

**Store the .env file in a safe place**

Usage
=====

If the package is installed globally:

.. code-block:: bash

    globus-flows-e2e-tests --version

Or if running the package directly from the repository:

.. code-block:: bash

    poetry run globus-flows-e2e-tests --version

To display the end-to-end tests current configuration:

.. code-block:: bash

    globus-flows-e2e-tests e2e --print-config

Slow tests can be skipped by running:

.. code-block:: bash

    globus-flows-e2e-tests e2e --skip-slow

Tests will default to running in serial since Flows only allows whitelisted
clients to deploy multiple flows. If the Globus Auth client ID is whitelisted,
tests can be run in parallel. To do so:

.. code-block:: bash

    globus-flows-e2e-tests e2e --parallel

You can also run locust load tests via the CLI on non-prod environments. You can
choose a test to run and the number of users to run it with via the `load`
subcommand: 

.. code-block:: bash

    globus-flows-e2e-tests load --test <TEST_NAME> --users <N_USERS>

If you install the CLI autocomplete, you can see which tests are available to
run via:

.. code-block:: bash

    globus-flows-e2e-tests load --test [TAB][TAB]

Running the load test will load a webpage display at http://127.0.0.1:8089.
The test may be stopped and the user count may be tweaked via the webpage but
re-starting the tests must be done via the CLI. 

Creating a Client or Secrets in an Auth Environment
===================================================

Go to the developer page for the Auth environment the client will exist in. The
portal follows the pattern of:
``https://auth.{environment_name}.globuscs.info/v2/web/developers``. Once there, 
go to the ``Automate`` project and locate or create a client called ``Flows
E2E Testing``. Copy its ID and create a personal secret for the environment.

| The Auth preview environment is at https://auth.preview.globus.org/v2/web/developers

Adding Tests
============

If a test does not logically fit in one of the existing scenarios, add a new
scenario. Each scenario should be self contained and define its own resources in
a conftest. Slow tests should use the ``@pytest.mark.slow`` decorator.
