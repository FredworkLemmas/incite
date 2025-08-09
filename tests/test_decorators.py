"""
A test suite for the decorator arguments.

NOTE that this is an atypical use case in that the namespace is defined.
This is not required in the tasks.py module.
"""

from invocate import task, task_namespace


# --- define tasks
@task
def no_decorator_args(c):
    pass


@task(help={'somearg': 'some argument'})
def with_decorator_args(c, somearg):
    pass


@task(namespace=('ns', 'this'))
def with_namespace_as_tuple(c):
    pass


@task(namespace='ns.that')
def with_namespace_as_string(c):
    pass


@task(namespace='ns.the_other', name='updated-name')
def with_namespace_as_string_and_updated_name(c):
    pass


ns = task_namespace()


# --- define tests
def test_no_decorator_args():
    """It should register tasks with no decorator arguments."""
    assert 'no-decorator-args' in ns.task_names


def test_with_decorator_args():
    """It should register tasks with decorator arguments."""
    assert 'with-decorator-args' in ns.task_names


def test_with_namespace_as_tuple():
    """It should register tasks with namespace as tuple."""
    # print(f'ns: {ns.task_names}')
    assert 'ns.this.with-namespace-as-tuple' in ns.task_names


def test_with_namespace_as_string():
    """It should register tasks with namespace as string."""
    assert 'ns.that.with-namespace-as-string' in ns.task_names


def test_with_namespace_as_string_and_updated_name():
    """It should register tasks with namespace as string and updated name."""
    assert 'ns.the-other.updated-name' in ns.task_names
