"""
Invocate - Enhanced Invoke task management with namespacing support.

This package provides a decorator-based approach to organizing Invoke tasks
with a simplified model of namespacing.
"""

from .core import (
    task,
    task_namespace
)

__version__ = "0.1.0"
__author__ = "Fred McDavid"
__email__ = "fred@frameworklabs.us"

__all__ = [
    "task",
    "task_namespace",
]