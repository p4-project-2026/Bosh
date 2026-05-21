from bosh.interpreter.executor.environment.table import Table


def test_table():
    table = Table[int]()
    table.bind("a", 1)
    table.bind("b", 2)
    assert table.lookup("a") == 1
    assert table.lookup("b") == 2
    assert table.contains("a")
    assert table.contains("b")
    assert not table.contains("c")

def test_table_snapshot():
    table = Table[int]()
    table.bind("a", 1)
    table.bind("b", 2)
    snapshot = table.get_snapshot()
    assert snapshot["a"] == 1
    assert snapshot["b"] == 2
    assert "a" in snapshot
    assert "b" in snapshot
    assert "c" not in snapshot

def test_table_domain():
    table = Table[int]()
    table.bind("a", 1)
    table.bind("b", 2)
    domain = table.domain()
    assert "a" in domain
    assert "b" in domain
    assert "c" not in domain

def test_table_bind_existing(): 
    table = Table[int]()
    table.bind("a", 1)
    try:
        table.bind("a", 2)
        assert False, "Expected exception when binding existing variable"
    except Exception as e:
        assert str(e) == "Name 'a' already defined in scope."

def test_table_lookup_nonexistent():
    table = Table[int]()
    try:
        table.lookup("a")
        assert False, "Expected exception when looking up nonexistent variable"
    except Exception as e:
        assert str(e) == "Name 'a' not found in scope."

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