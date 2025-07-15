"""
Environment configuration helper with caching and validation.

This module provides a singleton-based `EnvConfig` class to safely retrieve
environment variables in Django applications. It includes automatic caching
and typed access methods (`str`, `int`, `list`). Raises `ImproperlyConfigured`
if a required environment variable is missing or has invalid format.

Example usage:

    from utils.env_config import get_env

    env = get_env()
    SECRET_KEY = env.get_str("SECRET_KEY")
    ALLOWED_HOSTS = env.get_list("ALLOWED_HOSTS")
    PORT = env.get_int("PORT", default=8000)

Functions:
    - get_env(): Returns the singleton instance of EnvConfig.

Classes:
    - EnvConfig: Singleton class for accessing and caching environment variables.

"""

import os
from threading import Lock

from django.core.exceptions import ImproperlyConfigured


class EnvConfig:
    """
    Singleton class to access and validate environment variables with caching.

    Methods:
        - get_str(var_name, default=None, required=True) -> str:
            Returns a string value of an environment variable.

        - get_list(var_name, default=None, required=True, delimiter=',') -> list[str]:
            Returns a list of strings split by the specified delimiter.

        - get_int(var_name, default=None, required=True) -> int:
            Returns an integer value of an environment variable.

    Raises:
        - ImproperlyConfigured: If a required variable is missing or has invalid format.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache = {}
        return cls._instance

    def __init__(self):
        self._cache = {}

    def get_str(self, var_name: str, default=None, required=True) -> str:
        """
        Retrieve a string environment variable with optional default and required check.

        Args:
            var_name (str): The name of the environment variable.
            default (str, optional): Default value if not set. Defaults to None.
            required (bool, optional): Whether this variable is mandatory. Defaults to True.

        Returns:
            str: The value of the environment variable.

        Raises:
            ImproperlyConfigured: If the variable is required but missing.
        """
        if var_name in self._cache:
            return self._cache[var_name]

        value = os.getenv(var_name, default)
        if required and (value is None or value == ""):
            raise ImproperlyConfigured(f"Set the {var_name} environment variable")
        self._cache[var_name] = value
        return value

    def get_list(self, var_name: str, default=None, required=True, delimiter=",") -> list[str]:
        """
        Retrieve a list from a delimited environment variable string.

        Args:
            var_name (str): The name of the environment variable.
            default (str, optional): Default raw value. Defaults to None.
            required (bool, optional): Whether this variable is mandatory. Defaults to True.
            delimiter (str, optional): Delimiter used to split the string. Defaults to ",".

        Returns:
            list[str]: The list of values.
        """
        raw = self.get_str(var_name, default=default, required=required)
        if raw is None:
            return []
        return [item.strip() for item in raw.split(delimiter) if item.strip()]

    def get_int(self, var_name: str, default=None, required=True) -> int:
        """
        Retrieve an integer environment variable with validation.

        Args:
            var_name (str): The name of the environment variable.
            default (int, optional): Default integer value if not set. Defaults to None.
            required (bool, optional): Whether this variable is mandatory. Defaults to True.

        Returns:
            int: The integer value.

        Raises:
            ImproperlyConfigured: If the variable is required but missing,
                                  or cannot be converted to an integer.
        """
        raw = self.get_str(var_name, default=None, required=required)
        if raw is None:
            if default is not None:
                return default
            raise ImproperlyConfigured(f"Set the {var_name} environment variable")
        try:
            return int(raw)
        except ValueError:
            raise ImproperlyConfigured(f"Environment variable {var_name} must be an integer")


def get_env() -> EnvConfig:
    """
    Return the singleton instance of EnvConfig.

    Returns:
        EnvConfig: The global environment configuration handler.
    """
    return EnvConfig()
