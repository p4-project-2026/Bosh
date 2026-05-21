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

