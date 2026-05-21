from bosh.interpreter.executor.environment.scope_stack import ScopeStack
from bosh.interpreter.executor.environment.var_table import VarTable

def test_scope_stack_bind_and_lookup():
    stack = ScopeStack[int](VarTable)
    stack.bind("a", 1)
    assert stack.lookup("a") == 1
    stack.bind("b", 2)
    assert stack.lookup("b") == 2
    try:
        stack.lookup("c")
        assert False, "Expected exception when looking up nonexistent variable"
    except Exception as e:
        assert str(e) == "Undefined variable 'c'"
    try:
        stack.bind("a", 3)
        assert False, "Expected exception when binding existing variable"
    except Exception as e:
        assert str(e) == "Variable 'a' already defined in current scope."

def test_scope_stack_new_and_exit_scope():
    stack = ScopeStack[int](VarTable)
    stack.bind("a", 1)
    stack.new_scope()
    assert stack.lookup("a") == 1
    stack.bind("b", 2)
    assert stack.lookup("b") == 2
    stack.exit_scope()
    try:
        stack.lookup("b")
        assert False, "Expected exception when looking up variable from exited scope"
    except Exception as e:
        assert str(e) == "Undefined variable 'b'"
    assert stack.lookup("a") == 1

def test_scope_stack_contains():
    stack = ScopeStack[int](VarTable)
    stack.bind("a", 1)
    assert stack.contains("a")
    assert not stack.contains("b")
    stack.new_scope()
    assert stack.contains("a")
    assert not stack.contains("b")
    stack.bind("b", 2)
    assert stack.contains("b")

def test_scope_stack_domain():
    stack = ScopeStack[int](VarTable)
    stack.bind("a", 1)
    stack.bind("b", 2)
    domain = stack.domain()
    assert "a" in domain
    assert "b" in domain
    assert "c" not in domain
    stack.new_scope()
    stack.bind("c", 3)
    domain = stack.domain()
    assert "a" in domain
    assert "b" in domain
    assert "c" in domain

