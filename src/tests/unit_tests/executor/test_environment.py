import bosh.interpreter.executor.environment.environment as environment_module
import bosh.interpreter.executor.environment.scope_stack as scope_stack_module
import bosh.interpreter.executor.environment.table as table_module
import bosh.interpreter.executor.environment.var_table as var_table_module
import bosh.interpreter.executor.environment.store as store_module

noop_print = lambda *args, **kwargs: None

environment_module.vvvprint = noop_print
scope_stack_module.vvvprint = noop_print
table_module.vvvprint = noop_print
var_table_module.vvvprint = noop_print
store_module.vvvprint = noop_print

from bosh.interpreter.executor.environment.environment import Environment

# Test cases for variable binding
def test_bind_and_read_integer_variable():
    env = Environment()
    env.new_scope()
    env.assign_variable("count", 42)
    assert env.lookup_variable("count") == 42

def test_bind_and_read_string_variable():
    env = Environment()
    env.new_scope()
    env.assign_variable("name", "Alice")
    assert env.lookup_variable("name") == "Alice"

def test_bind_and_read_float_variable():
    env = Environment()
    env.new_scope()
    env.assign_variable("temperature", 98.6)
    assert env.lookup_variable("temperature") == 98.6

def test_bind_and_read_boolean_variable():
    env = Environment()
    env.new_scope()
    env.assign_variable("is_active", True)
    assert env.lookup_variable("is_active") is True

def test_bind_and_read_list_variable():
    env = Environment()
    env.new_scope()
    test_list = [1, 2, 3, 4, 5]
    env.assign_variable("numbers", test_list)
    assert env.lookup_variable("numbers") == test_list

def test_bind_and_read_none_variable():
    env = Environment()
    env.new_scope()
    env.assign_variable("empty", None)
    assert env.lookup_variable("empty") is None

def test_bind_multiple_variables_different_types():
    env = Environment()
    env.new_scope()
    env.assign_variable("integer", 100)
    env.assign_variable("string", "hello world")
    env.assign_variable("float", 3.14159)
    env.assign_variable("boolean", False)
    env.assign_variable("list", [10, 20, 30])
    assert env.lookup_variable("integer") == 100
    assert env.lookup_variable("string") == "hello world"
    assert env.lookup_variable("float") == 3.14159
    assert env.lookup_variable("boolean") is False
    assert env.lookup_variable("list") == [10, 20, 30]

def test_local_variable_binding_integer():
    env = Environment()
    env.new_scope()
    env.bind_local_variable("x", 55)
    assert env.lookup_variable("x") == 55

def test_local_variable_binding_string():
    env = Environment()
    env.new_scope()
    env.bind_local_variable("greeting", "Hi there!")
    assert env.lookup_variable("greeting") == "Hi there!"

def test_update_variable_same_type():
    env = Environment()
    env.new_scope()
    env.assign_variable("counter", 0)
    assert env.lookup_variable("counter") == 0
    env.assign_variable("counter", 10)
    assert env.lookup_variable("counter") == 10

def test_update_variable_different_type():
    env = Environment()
    env.new_scope()
    env.assign_variable("value", 42)
    assert env.lookup_variable("value") == 42
    env.assign_variable("value", "now a string")
    assert env.lookup_variable("value") == "now a string"

def test_environment_variable_update():
    env = Environment()
    env.assign_variable("x", 10)
    assert env.lookup_variable("x") == 10
    env.assign_variable("x", 20)
    assert env.lookup_variable("x") == 20

def test_environment_variable_not_found():
    env = Environment()
    try:
        env.lookup_variable("y")
        assert False, "Expected exception for variable not found"
    except Exception as e:
        assert str(e) == "Error looking up variable 'y': Undefined variable 'y'"

def test_environment_snapshot():
    env = Environment()
    env.assign_variable("x", 42)
    snapshot = env.snapshot()