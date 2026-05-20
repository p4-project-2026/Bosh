import os

import pytest
from bosh.interpreter.pre_processor.pre_processor import PreProcessor

# Make test_dir absolute relative to this file so all subdirectories are included
test_dir = os.path.join(os.path.dirname(__file__), "test_strings")

def collect_test_files():
    test_files = []
    for root, _, files in os.walk(test_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Skip non-.bosh.test files
            if not file_name.endswith(".test"):
                print(f"Skipping non-test bosh file: {file_path}")
                continue

            test_files.append(file_path)
    return test_files

def open_and_read_file(file):
    with open(file, "r") as f:
        return f.read()

@pytest.mark.parametrize("file_path", collect_test_files(), ids=lambda p: os.path.relpath(p, test_dir))
def test_pre_processor(file_path):
    # get the content of the file
    content = open_and_read_file(file_path)

    if not "\n===\n" in content:
        print(f"Warning: {file_path} does not contain the expected === delimiter. Skipping {file_path}.")
        pytest.skip(f"No === delimiter found in {file_path}")

    # Split the content by ===
    content = content.split("\n===\n")
    input = content[0]
    result = content[1].strip()

    if len(content) > 2:
        print(f"Warning: {file_path} contains more than one === delimiter. Skipping {file_path}.")
        pytest.skip(f"Multiple === delimiters found in {file_path}")

    output = PreProcessor().run(input)

    assert output == result