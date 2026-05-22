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



from bosh.interpreter.executor.environment.var_table import VarTable

def test_var_table_bind_and_lookup():
    var_table = VarTable()
    var_table.bind("x", 10)
    assert var_table.lookup("x") == 10
    try:
        var_table.bind("x", 20)
        assert False, "Expected exception when binding existing variable"
    except Exception as e:
        assert str(e) == "Variable 'x' already defined in scope."
    try:
        var_table.lookup("y")
        assert False, "Expected exception when looking up nonexistent variable"
    except Exception as e:
        assert str(e) == "Variable 'y' not found in scope."


def test_var_table_bind_and_lookup():
    var_table = VarTable()
    var_table.bind("x", 42)
    assert var_table.lookup("x") == 42

def test_var_table_bind_duplicate():
    var_table = VarTable()
    var_table.bind("x", 42)
    try:
        var_table.bind("x", 43)
        assert False, "Expected exception for duplicate binding"
    except Exception as e:
        assert str(e) == "Variable 'x' already defined in scope."

def test_var_table_lookup_not_found():
    var_table = VarTable()
    try:
        var_table.lookup("y")
        assert False, "Expected exception for name not found"
    except Exception as e:
        assert str(e) == "Variable 'y' not found in scope."

def test_contains_and_domain():
    var_table = VarTable()
    var_table.bind("a", 1)
    var_table.bind("b", 2)
    assert var_table.contains("a") == True
    assert var_table.contains("b") == True
    assert var_table.contains("c") == False
    assert set(var_table.domain()) == {"a", "b"}

def test_function_scope():
    var_table = VarTable(function_scope=True)
    var_table.bind("f", 99)
    assert var_table.lookup("f") == 99
    assert var_table.function_scope == True

def test_get_snapshot():
    var_table = VarTable()
    var_table.bind("x", 42)
    snapshot = var_table.get_snapshot()
    assert snapshot == {"x": 42}

def test_copy():
    var_table = VarTable()
    var_table.bind("x", 42)
    copy_table = var_table.copy()
    assert copy_table.lookup("x") == 42
    copy_table.bind("y", 99)
    assert not var_table.contains("y")
    assert copy_table.contains("y")