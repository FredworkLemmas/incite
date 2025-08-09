# Invocate
Enhanced Invoke task management with simplified namespacing support.

## Purpose
I love [Invoke](https://www.pyinvoke.org/) and I use it all the time, but I
find the namespace feature to be a bit cumbersome to maintain so I've written
Invocate as a wrapper on top of Invoke.

Invocate overrides the task decorator to accept additional namespace-related
parameters and defines a task_namespace() function that makes namespacing
task a lot easier to work with.

## Features

- **Namespaced Tasks**: Organize tasks into hierarchical namespaces
- **Enhanced Decorator**: Drop-in replacement for `@task` with additional features

## Installation

```bash
pip install invocate
```

## Quick Start

```python
from invocate import task


# Simple task (no namespace)
@task
def hello(c):
    """Say hello"""
    print("Hello, World!")


# Namespaced task
@task(namespace=('build', 'frontend'))
def build_js(c):
    """Build JavaScript assets"""
    c.run("npm run build")


# Another namespaced task
@task(namespace='build.backend')
def build_python(c):
    """Build Python package"""
    c.run("python -m build")

```

Save this as tasks.py and run:

```bash
invocate -l
```

You'll see:

```
Available tasks:

  hello
  build.frontend.build-js
  build.backend.build-python
```

## Advanced Usage
### Customer Task Names
```python
@task(name='custom-name', namespace=('utils',))
def some_function(c):
    pass
```

## API Reference
### `task(*args, **kwargs)`
Enhanced task decorator with namespace support.
**Parameters:**
- (tuple): Namespace hierarchy as tuple of strings `namespace`
- Standard invoke task parameters (name, help, etc.)

### `task_namespace()`
Returns the complete task collection for use with Invoke.
