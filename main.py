import sys
import os
import hashlib
import zlib


def create_blob(file_name):
    with open(file_name, "rb") as f:
        file = f.read()

    header = f"blob {len(file)}\0".encode()
    content = header + file

    blob_hash = hashlib.sha1(content).hexdigest()
    compressed_blob = zlib.compress(content)

    dir_path = f".git/objects/{blob_hash[:2]}"
    file_path = f"{dir_path}/{blob_hash[2:]}"

    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(compressed_blob)

    return blob_hash

file_name = "example.txt"
blob_hash = create_blob(file_name)
print(f"Blob for {file_name} created with hash: {blob_hash}")

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
    

if __name__ == "__main__":
    main()