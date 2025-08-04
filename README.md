# BitDaddy Invoke

Enhanced Invoke task management with simplified namespacing support.

## Features

- **Namespaced Tasks**: Organize tasks into hierarchical namespaces
- **Enhanced Decorator**: Drop-in replacement for `@task` with additional features

## Installation

```bash
pip install incite
```

## Quick Start

```python
from incite import task, task_namespace


# Simple task (no namespace)
@task
def hello(c):
    """Say hello"""
    print("Hello, World!")


# Namespaced task
@task(menu_parent=('build', 'frontend'))
def build_js(c):
    """Build JavaScript assets"""
    c.run("npm run build")


# Another namespaced task
@task(menu_parent='build.backend')
def build_python(c):
    """Build Python package"""
    c.run("python -m build")


# Export the namespace for invoke
ns = task_namespace()

```

Save this as tasks.py and run:

```bash
inv -l
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
@task(name='custom-name', menu_parent=('utils',))
def some_function(c):
    pass
```

## API Reference
### `task(*args, **kwargs)`
Enhanced task decorator with namespace support.
**Parameters:**
- (tuple): Namespace hierarchy as tuple of strings `menu_parent`
- Standard invoke task parameters (name, help, etc.)

### `task_namespace()`
Returns the complete task collection for use with Invoke.
