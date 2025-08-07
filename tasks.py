import shutil
import tempfile
import tomllib
import os
from dotenv import load_dotenv
from invoke import task


# Load environment variables from .env file and get the tokens
load_dotenv()


def get_current_git_branch(c):
    """Return the current git branch."""
    return c.run("git branch --show-current").stdout.strip()


def get_invocate_version(c):
    """Return the current version of Invocate from project TOML file."""
    with open('pyproject.toml', 'rb') as f:
        pyproject = tomllib.load(f)
    return pyproject['project']['version']


def build_twine_opts(testing=False):
    opts = [
        '-u __token__',
        '-p {}'.format(
            os.getenv('TEST_PYPI_TOKEN') if testing
            else os.getenv('PYPI_TOKEN'))
    ]
    return ['--repository testpypi'] + opts if testing else opts


@task
def run_tests(c):
    """Run all tests."""
    c.run("PYTHONPATH=src/ pytest")


@task
def build_package(c):
    """Build the package."""
    c.run("python -m build")


@task
def publish_package(c):
    """Publish the package to PyPI."""
    c.run('python -m twine upload {} dist/*'.format(
        ' '.join(build_twine_opts(testing=False))
    ))


@task
def publish_test_package(c):
    """Publish the package to TestPyPI."""
    c.run('python -m twine upload {} dist/*'.format(
        ' '.join(build_twine_opts(testing=True))
    ))


@task
def tag_release(c):
    """Tag the current release."""
    # get version and branch
    version = get_invocate_version(c)
    branch = get_current_git_branch(c)

    # bail if not on master
    if branch != 'master':
        print(f"Skipping tag release on branch {branch} - must be on master")
        return

    # get list of tags and bail if already tagged
    tags = c.run("git tag").stdout.strip().split('\n')
    if version in tags:
        print(f"Skipping tag release for version {version} - already exists")

    # tag the version
    c.run(f'git tag {version}')
    c.run('git push --tags')


@task(help={'testing': 'Whether to use TestPyPI or PyPI. Defaults to False.'})
def test_invocate_installation(c, testing=True):
    """Test invocate package installation and basic functionality."""
    temp_dir = None
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix='invocate_test_')
        print(f"Created temporary directory: {temp_dir}")

        # Create virtual environment
        venv_path = os.path.join(temp_dir, 'test_env')
        c.run(f"virtualenv {venv_path}")

        # Determine the python executable path in the virtual environment
        if os.name == 'nt':  # Windows
            python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
            pip_exe = os.path.join(venv_path, 'Scripts', 'pip.exe')
            inv_exe = os.path.join(venv_path, 'Scripts', 'inv.exe')
        else:  # Unix/Linux/macOS
            python_exe = os.path.join(venv_path, 'bin', 'python')
            pip_exe = os.path.join(venv_path, 'bin', 'pip')
            inv_exe = os.path.join(venv_path, 'bin', 'inv')

        # install invoke from non-testing PyPI
        print("Installing invoke package...")
        c.run(f"{pip_exe} install invoke")

        # Install invocate package
        print("Installing invocate package...")
        opts = '--index-url https://test.pypi.org/simple/' if testing else ''
        c.run(f"{pip_exe} install {opts} invocate")

        # Create a test tasks.py file
        test_tasks_content = '''from invocate import task, task_namespace

@task(namespace="test", name="hello")
def hello_task(c):
    """A simple hello task in test namespace."""
    print("Hello from invocate test task!")
    return "success"

@task(namespace="demo", name="greet")
def greet_task(c, name="World"):
    """A greeting task in demo namespace."""
    message = f"Greetings, {name}!"
    print(message)
    return message

@task(name="simple")
def simple_task(c):
    """A simple task without namespace."""
    print("Simple task executed successfully!")
    return "simple_done"
    
ns = task_namespace()
'''

        test_tasks_file = os.path.join(temp_dir, 'tasks.py')
        with open(test_tasks_file, 'w') as f:
            f.write(test_tasks_content)

        print("Created test tasks.py file")

        # Change to temp directory and run the tasks
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        try:
            # Test the tasks by running them with inv command
            print("\nTesting task execution:")

            # Run hello task - should be "inv hello-task"
            print("Running hello-task...")
            result1 = c.run(
                f"{inv_exe} test.hello",
                hide=True
            )
            expected1 = "Hello from invocate test task!"
            if expected1 in result1.stdout:
                print(f"✅ hello-task output correct: {result1.stdout.strip()}")
            else:
                print(
                    f"❌ hello-task output incorrect. Expected: {expected1}, Got: {result1.stdout.strip()}")
                return

            # Run greet task with default parameter - should be "inv greet-task"
            print("Running greet-task with default parameter...")
            result2 = c.run(f"{inv_exe} demo.greet", hide=True)
            expected2 = "Greetings, World!"
            if expected2 in result2.stdout:
                print(
                    f"✅ greet-task (default) output correct: {result2.stdout.strip()}")
            else:
                print(
                    f"❌ greet-task (default) output incorrect. Expected: {expected2}, Got: {result2.stdout.strip()}")
                return

            # Run greet task with custom parameter - should be "inv greet-task -n 'PyCharm'"
            print("Running greet-task with custom parameter...")
            result3 = c.run(f"{inv_exe} demo.greet -n 'PyCharm'", hide=True)
            expected3 = "Greetings, PyCharm!"
            if expected3 in result3.stdout:
                print(
                    f"✅ greet-task (custom) output correct: {result3.stdout.strip()}")
            else:
                print(
                    f"❌ greet-task (custom) output incorrect. Expected: {expected3}, Got: {result3.stdout.strip()}")
                return

            # Run simple task - should be "inv simple-task"
            print("Running simple-task...")
            result4 = c.run(f"{inv_exe} simple", hide=True)
            expected4 = "Simple task executed successfully!"
            if expected4 in result4.stdout:
                print(f"✅ simple-task output correct: {result4.stdout.strip()}")
            else:
                print(
                    f"❌ simple-task output incorrect. Expected: {expected4}, Got: {result4.stdout.strip()}")
                return

            print(
                "\n✅ SUCCESS: Invocate package was successfully installed and all tasks executed correctly!")
            print("✅ Namespace and name parameters work as expected")
            print("✅ Task parameter passing works correctly")
            print("✅ All task outputs matched expectations")

        finally:
            os.chdir(original_dir)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")
