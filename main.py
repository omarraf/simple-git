import sys
import os
import zlib
import hashlib

def create_blob(content):
    """Creates a Git blob object and stores it in .git/objects/"""
    
    # Create the Git blob header
    header = f"blob {len(content)}\0".encode()
    blob_data = header + content  # Concatenating header + file content

    # Compute SHA-1 hash (Git hashes uncompressed content)
    blob_hash = hashlib.sha1(blob_data).hexdigest()

    # Compress the blob data
    compressed_blob = zlib.compress(blob_data)

    # Git stores objects in `.git/objects/<first 2 chars of hash>/<remaining 38 chars>`
    dir_name = blob_hash[:2]
    file_name = blob_hash[2:]
    dir_path = f".git/objects/{dir_name}"
    file_path = f"{dir_path}/{file_name}"

    # Ensure the directory exists
    os.makedirs(dir_path, exist_ok=True)

    # Write the compressed blob to the file
    with open(file_path, "wb") as f:
        f.write(compressed_blob)

    return blob_hash  # Return the SHA-1 hash

def read_blob(hash):
    """Reads and prints the contents of a Git blob object."""
    dir_name = hash[:2]  # First two characters of the hash
    file_name = hash[2:]  # Remaining characters
    object_path = f".git/objects/{dir_name}/{file_name}"

    if not os.path.exists(object_path):
        print(f"Error: Git object {hash} not found!", file=sys.stderr)
        return

    with open(object_path, "rb") as f:
        compressed_data = f.read()

    # Decompress using zlib
    decompressed_data = zlib.decompress(compressed_data)

    # Git objects start with a header like "blob 12\x00"
    header_end = decompressed_data.index(b'\x00')  # Find the null byte
    content = decompressed_data[header_end + 1:]  # Extract actual content

    print(content.decode(), end="")

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

    elif command == "cat-file" and len(sys.argv) == 4 and sys.argv[2] == "-p":
        read_blob(sys.argv[3])  # Read and print the blob object

    elif command == "hash-object" and len(sys.argv) == 4 and sys.argv[2] == "-w":
        file_name = sys.argv[3]
        
        if not os.path.exists(file_name):
            print(f"Error: File {file_name} not found!", file=sys.stderr)
            return

        with open(file_name, "rb") as f:
            content = f.read()

        blob_hash = create_blob(content)
        print(blob_hash)  # Print the SHA-1 hash

    else:
        print(f"Unknown command: {command}", file=sys.stderr)

if __name__ == "__main__":
    main()