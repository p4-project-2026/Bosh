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


    