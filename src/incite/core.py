"""Core functionality for BitDaddy Invoke task management."""

import contextlib
import os
from typing import Callable, Optional, Union, List, Tuple, Literal, Dict

import attrs
import invoke
from invoke import Collection

_task_collector = None
_namespace_tree = None
NO_COLLECTION_DEFINED = 'bitdaddy_no_collection_defined'


@attrs.define
class BitdaddyTask:
    """Represents a BitDaddy task with its metadata."""
    task: Callable
    name: str


@attrs.define
class TaskNamespace:
    """
    A data structure for the organization of namespaced tasks into
    invoke namespace collections.
    """
    name: Optional[str] = None
    parent: Optional['TaskNamespace'] = None
    children: Union[List['TaskNamespace'], None] = None
    tasks: Optional[List[callable]] = None
    collection: Optional[Collection] = None

    def __attrs_post_init__(self):
        self.children = self.children or []
        self.tasks = self.tasks or []

    @classmethod
    def add_task(
            cls,
            namespace_tuple: Union[
                Tuple[str], Literal['bitdaddy_no_collection_defined']],
            task: Callable) -> None:
        """Add a task to the tree of namespace collections."""
        if namespace_tuple == NO_COLLECTION_DEFINED:
            toplevel = cls._singleton_root()
            if not toplevel.tasks:
                toplevel.tasks = []
            toplevel.tasks.append(task)
            return

        namespace = cls._fetch_or_provision_namespace(namespace_tuple)
        if not namespace.tasks:
            namespace.tasks = []
        namespace.tasks.append(task)
        namespace.collection = None

    @classmethod
    def as_collection(cls):
        """Return the toplevel namespace as an invoke collection with all descendants added."""
        cursor = cls._singleton_root()
        return cursor._as_collection()

    @classmethod
    def _singleton_root(cls) -> 'TaskNamespace':
        global _namespace_tree
        if _namespace_tree:
            return _namespace_tree
        _namespace_tree = cls()
        return _namespace_tree

    @classmethod
    def _fetch_or_provision_namespace(
            cls, namespace_tuple: Tuple[str]) -> 'TaskNamespace':
        cursor = cls._singleton_root()
        for namespace_name in namespace_tuple:
            cursor = cursor._seek_or_create(namespace_name)
        return cursor

    def _as_collection(self):
        if self.collection:
            return self.collection
        self.collection = Collection(self.name) if self.name else Collection()
        if self.children:
            for child in self.children:
                self.collection.add_collection(child._as_collection())
        if self.tasks:
            for task in self.tasks:
                self.collection.add_task(task.task, name=task.name)
        return self.collection

    def _add_child_namespace(self, namespace_name) -> 'TaskNamespace':
        if not self.children:
            self.children = []
        new_child = self.__class__(name=namespace_name, parent=self)
        self.children.append(new_child)
        return new_child

    def _seek_or_create(self, namespace_name: str) -> 'TaskNamespace':
        for child in self.children:
            if child.name == namespace_name:
                return child
        return self._add_child_namespace(namespace_name)


@attrs.define
class BitdaddyTaskCollector:
    """A data structure for the collection of namespaced tasks."""
    tasks_dict: Optional[Dict[Tuple, List[BitdaddyTask]]] = None

    def add(self, menu_parent: Tuple, task: BitdaddyTask) -> None:
        """Store a task with its menu parent tuple."""
        if not self.tasks_dict:
            self.tasks_dict = {}
        if menu_parent not in self.tasks_dict:
            self.tasks_dict[menu_parent] = []
        self.tasks_dict[menu_parent].append(task)

    @classmethod
    def singleton(cls) -> 'BitdaddyTaskCollector':
        """Return the global task collector instance."""
        global _task_collector
        if _task_collector:
            return _task_collector
        _task_collector = cls()
        return _task_collector

    @classmethod
    def toplevel_invoke_namespace(cls):
        """Return the toplevel invoke task namespace collection."""
        instance = cls.singleton()
        if instance.tasks_dict:
            for menu_tuple, tasks in instance.tasks_dict.items():
                for task in tasks:
                    TaskNamespace.add_task(menu_tuple, task)
        return TaskNamespace.as_collection()


class _BitdaddyTaskDecorator:
    """Internal decorator class for invoke tasks with namespace support."""

    def __init__(self, *args, **kwargs):
        self.menu_parent = (
            tuple(kwargs.pop('menu_parent'))
            if 'menu_parent' in kwargs else NO_COLLECTION_DEFINED)
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        return self._collect(func)

    def _collect(self, func):
        wrapped_func = invoke.tasks.task(func, **self.kwargs)
        name = self.kwargs.get(
            'name') if 'name' in self.kwargs else func.__name__
        task = BitdaddyTask(task=wrapped_func, name=name)
        BitdaddyTaskCollector.singleton().add(self.menu_parent, task)
        return wrapped_func


def task(*args, **kwargs):
    """
    Decorator for invoke tasks with simplified namespace support.

    Usage:
        @task
        def my_task(c):
            pass

        @task(menu_parent=('env','build'))
        def deploy(c):
            pass

        @task(menu_parent='env.build'))
        def test_deploy(c):
            pass
    """
    if args:
        func = args[0]
        wrapped_func = invoke.tasks.task(func)
        name = func.__name__
        task = BitdaddyTask(task=wrapped_func, name=name)
        BitdaddyTaskCollector.singleton().add(NO_COLLECTION_DEFINED, task)
        return wrapped_func
    else:
        return _BitdaddyTaskDecorator(**kwargs)


def task_namespace():
    """Return the complete task namespace collection for use with Invoke."""
    return BitdaddyTaskCollector.toplevel_invoke_namespace()


@contextlib.contextmanager
def change_directory(path):
    """Context manager to temporarily change the current working directory."""
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)