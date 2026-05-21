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

from bosh.interpreter.executor.environment.scope_stack import ScopeStack
from bosh.interpreter.executor.environment.function_binding import FunctionBinding


def test_bind_and_lookup():
    stack = ScopeStack()
    stack.bind("x", 42)
    assert stack.lookup("x") == 42

def test_nested_scope():
    stack = ScopeStack()
    stack.bind("x", 1)
    stack.new_scope()
    stack.bind("y", 2)
    assert stack.lookup("x") == 1
    assert stack.lookup("y") == 2
    stack.exit_scope()
    try:
        stack.lookup("y")
        assert False, "Expected exception for variable not found"
    except Exception as e:
        assert str(e) == "Undefined variable 'y'"

def test_nested_scope_shadowing():
    stack = ScopeStack()
    stack.bind("x", 1)
    stack.new_scope()
    stack.bind("x", 2)  # Shadowing outer x
    assert stack.lookup("x") == 2
    stack.exit_scope()
    assert stack.lookup("x") == 1

def test_exit_global_scope():
    stack = ScopeStack()
    try:
        stack.exit_scope()
        assert False, "Expected exception for exiting global scope"
    except Exception as e:
        assert str(e) == "Cannot exit global scope."

def test_function_scope():
    stack = ScopeStack()
    stack.bind("a", 1)
    captured_scope = stack.snapshot()
    func_def = FunctionBinding(parameters=[], captured_scope=captured_scope, body=None)
    stack.enter_function_scope(func_def)
    assert stack.lookup("a") == 1
    stack.bind("b", 2)
    assert stack.lookup("b") == 2
    stack.exit_scope()
    try:
        stack.lookup("b")
        assert False, "Expected exception for variable not found after exiting function scope"
    except Exception as e:
        assert str(e) == "Undefined variable 'b'"
    assert stack.lookup("a") == 1

def test_lookup_assign():
    stack = ScopeStack()
    stack.bind("x", 1)
    stack.new_scope()
    stack.bind("y", 2)
    assert stack.lookup_assign("x") == 1
    assert stack.lookup_assign("y") == 2
    stack.exit_scope()
    try:
        stack.lookup_assign("y")
        assert False, "Expected exception for variable not found in lookup_assign"
    except Exception as e:
        assert str(e) == "Variable 'y' not found in scope."

def test_lookup_assign_function_scope():
    stack = ScopeStack()
    stack.bind("a", 1)
    captured_scope = stack.snapshot()
    func_def = FunctionBinding(parameters=[], captured_scope=captured_scope, body=None)
    stack.enter_function_scope(func_def)
    assert stack.lookup("a") == 1
    try:
        stack.lookup_assign("a")
        assert False, "Expected exception for variable not found in lookup_assign when reaching function scope"
    except Exception as e:
        assert str(e) == "Variable 'a' not found in scope."
    stack.bind("b", 2)
    assert stack.lookup_assign("b") == 2
    assert stack.lookup("b") == 2
    stack.exit_scope()
    try:
        stack.lookup_assign("b")
        assert False, "Expected exception for variable not found in lookup_assign after exiting function scope"
    except Exception as e:
        assert str(e) == "Variable 'b' not found in scope."
    assert stack.lookup_assign("a") == 1

def test_bind_duplicate():
    stack = ScopeStack()
    stack.bind("x", 1)
    try:
        stack.bind("x", 2)
        assert False, "Expected exception for duplicate binding"
    except Exception as e:
        assert str(e) == "Variable 'x' already defined in current scope."

def test_function_scope_stop():
    stack = ScopeStack()
    stack.bind("a", 1)
    captured_scope = stack.snapshot()
    func_def = FunctionBinding(parameters=[], captured_scope=captured_scope, body=None)
    stack.enter_function_scope(func_def)
    stack.bind("b", 2)
    assert stack.lookup("a") == 1
    assert stack.lookup("b") == 2
    try:
        stack.lookup_assign("a")
        assert False, "Expected exception for variable not found in lookup_assign when reaching function scope"
    except Exception as e:
        assert str(e) == "Variable 'a' not found in scope."
    stack.exit_scope()
    try:
        stack.lookup("b")
        assert False, "Expected exception for variable not found after exiting function scope"
    except Exception as e:
        assert str(e) == "Undefined variable 'b'"

def test_snapshot():
    stack = ScopeStack()
    stack.bind("x", 1)
    stack.new_scope()
    stack.bind("y", 2)
    snapshot = stack.snapshot()
    assert snapshot.lookup("x") == 1
    assert snapshot.lookup("y") == 2

def test_snapshot_function_scope():
    stack = ScopeStack()
    stack.bind("a", 1)
    captured_scope = stack.snapshot()
    func_def = FunctionBinding(parameters=[], captured_scope=captured_scope, body=None)
    stack.enter_function_scope(func_def)
    stack.bind("b", 2)
    snapshot = stack.snapshot()
    assert snapshot.lookup("a") == 1
    assert snapshot.lookup("b") == 2