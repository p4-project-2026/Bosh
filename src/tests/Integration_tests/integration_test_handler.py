import os
import subprocess

# Make test_dir absolute relative to this file so all subdirectories are included
test_dir = os.path.join(os.path.dirname(__file__), "tests")

# Recursively go through all files in every directory under test_dir
def run_tests():
    for root, _, files in os.walk(test_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Skip non-.bosh.test files
            if not file_name.endswith(".bosh.test"):
                print(f"Skipping non-test bosh file: {file_path}")
                continue

            # get the content of the file
            content = open_and_read_file(file_path)

            if not "\n===\n" in content:
                print(f"Warning: {file_path} does not contain the expected === delimiter. Skipping {file_path}.")
                continue

            # Split the content by ===
            content = content.split("\n===\n")
            code = content[0]
            result = content[1].strip()

            if len(content) > 2:
                print(f"Warning: {file_path} contains more than one === delimiter. Skipping {file_path}.")
                continue

            subprocess.run([
                "uv",
                "run",
                "bosh",
                "-c",
                code,
            ], check=True)


def open_and_read_file(file):
    with open(file, "r") as f:
        return f.read()

run_tests()
		



