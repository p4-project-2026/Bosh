from bosh.interpreter.executor.environment.scope_stack import ScopeStack

def test_scope_stack_bind_and_lookup():
    stack = ScopeStack()
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
    stack = ScopeStack()
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
