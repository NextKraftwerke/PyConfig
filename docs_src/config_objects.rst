Config objects
================================================================================

.. image:: construction-tape.png
  :alt: "Under Construction" Sign

Here we describe the types and functions you can use to model configuration within your app. Usually each app will
have a single subclass of :py:class:`~nx_config.Config`.

.. autoclass:: nx_config.Config
.. autoclass:: nx_config.ConfigSection
.. autoclass:: nx_config.SecretString
.. autoclass:: nx_config.URL
.. autodecorator:: nx_config.validate
