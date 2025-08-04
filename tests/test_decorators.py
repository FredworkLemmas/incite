import pytest from bitdaddy_invoke import bitdaddy_task, bitdaddy_task_namespace
def test_simple_task_decorator(): """Test basic task decoration without namespaces.""" @bitdaddy_task def test_task(c): pass
ns = bitdaddy_task_namespace()
assert 'test_task' in [task.name for task in ns.tasks]
def test_namespaced_task_decorator(): """Test task decoration with namespaces.""" @bitdaddy_task(menu_parent=('build', 'frontend')) def build_js(c): pass
ns = bitdaddy_task_namespace()
# Check that namespace structure is created
assert len(ns.collections) > 0
def test_custom_task_name(): """Test custom task naming.""" @bitdaddy_task(name='custom-name') def some_function(c): pass
ns = bitdaddy_task_namespace()
task_names = [task.name for task in ns.tasks]
assert 'custom-name' in task_names
