Loading configs
================================================================================

This section documents the functions used (usually on app start-up) to load the configuration from a file or from
environment variables. It also describes functions that can help you add useful command-line arguments to your app
related to config file paths, config file templates and documenting the app's configuration options.

.. autofunction:: nx_config.fill_config
.. autofunction:: nx_config.fill_config_from_path
.. autofunction:: nx_config.resolve_config_path
.. autofunction:: nx_config.add_cli_options
.. autoclass:: nx_config.Format
