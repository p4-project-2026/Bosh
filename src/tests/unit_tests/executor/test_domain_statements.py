import os
from pathlib import Path
import bosh.interpreter.executor.environment.environment as environment_module
import bosh.helper_functions.logged as logging_module
from bosh.interpreter.executor.environment.environment import Environment
from bosh.interpreter.abstract_syntax import *

# Silence verbose debug printers during tests
noop_print = lambda *args, **kwargs: None
environment_module.vvvprint = noop_print
logging_module.vvvprint = noop_print

def test_make_statement():
    env = Environment()
    try:
        make_stmt = Make(new=True, entity_type=Type(name="file"), name=StringLiteral("test_file.txt"), location=None)
        make_stmt.execute(env)
        assert os.path.isfile("test_file.txt")
    finally:
        if os.path.exists("test_file.txt"):
            os.remove("test_file.txt")

def test_write_and_read_statement():
    env = Environment()
    target = "test_rw.txt"
    try:
        write_stmt = Write(target=StringLiteral(target), data=StringLiteral("hello world"))
        write_stmt.execute(env)
        read_stmt = Read(source=StringLiteral(target))
        contents = read_stmt.execute(env)
        assert contents == "hello world"
    finally:
        if os.path.exists(target):
            os.remove(target)

def test_delete_statement():
    env = Environment()
    target = "test_delete.txt"
    with open(target, "w") as f:
        f.write("x")
    assert os.path.isfile(target)
    delete_stmt = Delete(target=StringLiteral(target))
    delete_stmt.execute(env)
    assert not os.path.exists(target)

def test_rename_statement():
    env = Environment()
    old = "old_name.txt"
    new = "new_name.txt"
    with open(old, "w") as f:
        f.write("x")
    try:
        rename_stmt = Rename(target=StringLiteral(old), new_name=StringLiteral(new))
        rename_stmt.execute(env)
        assert os.path.isfile(new)
        assert not os.path.exists(old)
    finally:
        for p in (old, new):
            if os.path.exists(p):
                os.remove(p)

def test_copy_and_move_statement():
    env = Environment()
    src = "src_file.txt"
    dst = "dst_file.txt"
    moved = "moved_file.txt"
    with open(src, "w") as f:
        f.write("copyme")
    try:
        copy_stmt = Copy(source=StringLiteral(src), target=StringLiteral(dst))
        copy_stmt.execute(env)
        assert os.path.isfile(dst)
        with open(dst, "r") as f:
            assert f.read() == "copyme"

        move_stmt = Move(source=StringLiteral(dst), target=StringLiteral(moved))
        move_stmt.execute(env)
        assert os.path.isfile(moved)
        assert not os.path.exists(dst)
    finally:
        for p in (src, dst, moved):
            if os.path.exists(p):
                os.remove(p)
