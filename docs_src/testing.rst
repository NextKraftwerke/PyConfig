Testing with PyConfig
================================================================================

.. image:: construction-tape.png
  :alt: "Under Construction" Sign

Config objects are made to be mostly immutable (meaning that only the very few loading functions are able to modify
them). This makes it easier to track at which points in the app the config might possibly change. On the other hand,
it makes it difficult/annoying to write tests that require different configurations. This section documents functions
that make it quick and less verbose to adapt configs for specific tests.

.. autofunction:: nx_config.test_utils.update_section
