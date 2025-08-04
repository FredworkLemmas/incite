from incite import task, task_namespace


# Simple task
@task
def hello(c):
    """Say hello to the world."""
    print("Hello, World!")


# Namespaced tasks
@task(menu_parent=('build',))
def clean(c):
    """Clean build artifacts."""
    c.run("rm -rf build/ dist/ *.egg-info/")


@task(menu_parent=('build', 'python'))
def build_wheel(c):
    """Build Python wheel."""
    c.run("python -m build --wheel")


@task(menu_parent=('build', 'python'))
def build_sdist(c):
    """Build source distribution."""
    c.run("python -m build --sdist")



# Export namespace
ns = task_namespace()
