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

from bosh.interpreter.executor.environment.table import Table

def test_bind_and_lookup():
    table = Table[int]()
    table.bind("x", 42)
    assert table.lookup("x") == 42

def test_bind_duplicate():
    table = Table[int]()
    table.bind("x", 42)
    try:
        table.bind("x", 43)
        assert False, "Expected exception for duplicate binding"
    except Exception as e:
        assert str(e) == "Name 'x' already defined in scope."

def test_lookup_not_found():
    table = Table[int]()
    try:
        table.lookup("y")
        assert False, "Expected exception for name not found"
    except Exception as e:
        assert str(e) == "Name 'y' not found in scope."

def test_contains_and_domain():
    table = Table[int]()
    table.bind("a", 1)
    table.bind("b", 2)
    assert table.contains("a") == True
    assert table.contains("b") == True
    assert table.contains("c") == False
    assert set(table.domain()) == {"a", "b"}

def test_function_scope():
    table = Table[int](function_scope=True)
    table.bind("f", 99)
    assert table.lookup("f") == 99
    assert table.function_scope == True