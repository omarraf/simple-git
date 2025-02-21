import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <command>", file=sys.stderr)
        return

    command = sys.argv[1]

    if command == "init":
        os.makedirs(".git/objects", exist_ok=True)
        os.makedirs(".git/refs", exist_ok=True)
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
        