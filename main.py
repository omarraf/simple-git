import sys
import os
import zlib
import hashlib
import time


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

def read_tree(hash):
    """Reads and prints the contents of Git tree object"""
    dir_name = hash[:2]
    file_name = hash[2:]
    object_path = f".git/objects/{dir_name}/{file_name}"

    if not os.path.exists(object_path):
        print(f"Error: Git object {hash} not found!")
        return
    
    with open(object_path, "rb") as f:
        compressed_data = f.read()
    
    decompressed_data = zlib.decompress(compressed_data)
    parse_tree(decompressed_data)
    
def parse_tree(decompressed_data):
    """Parses a tree object's contents to a readable format"""
    header_end = decompressed_data.index(b'\0')
    data = decompressed_data[header_end + 1:]

    index = 0
    while index < len(data):
        #read mode permissions
        space_index = data.index(b' ', index)
        mode = data[index:space_index].decode() # convert bytes to string
        index = space_index + 1 #move to the file name

        #read file name
        null_index = data.index(b'\0', index)
        filename = data[index:null_index].decode()
        index = null_index + 1 #move past null terminator

        #read sha-1 hash (always 20 bytes)
        sha1_bytes = data[index:index + 20]
        sha1_hex = sha1_bytes.hex() #convert bytes to hex string
        index += 20 #move past hash

        #determine if its a file or dir
        type_str = "blob" if mode == "100644" else "tree"

        print(f"{mode} {type_str} {sha1_hex} {filename}")

def create_commit(tree_hash, parent_hash=None, author="John Doe <john@example.com>", message="Initial commit"):
    """Creates a Git commit object and stores it in .git/objects/"""
    
    timestamp = int(time.time())  # Current UNIX timestamp
    timezone = "-0800"  # Hardcoded timezone (for now)

    # Build commit object contents
    commit_lines = [
        f"tree {tree_hash}"
    ]

    if parent_hash:  # Only add parent if it exists (not the first commit)
        commit_lines.append(f"parent {parent_hash}")

    commit_lines.append(f"author {author} {timestamp} {timezone}")
    commit_lines.append(f"committer {author} {timestamp} {timezone}")
    commit_lines.append("")  # Blank line separating metadata from message
    commit_lines.append(message)

    commit_content = "\n".join(commit_lines).encode()

    # Compute SHA-1 hash
    header = f"commit {len(commit_content)}\0".encode()
    full_commit = header + commit_content
    commit_hash = hashlib.sha1(full_commit).hexdigest()

    # Store commit in .git/objects/
    dir_name = commit_hash[:2]
    file_name = commit_hash[2:]
    dir_path = f".git/objects/{dir_name}"
    file_path = f"{dir_path}/{file_name}"

    if not os.path.exists(file_path):  # Avoid rewriting existing objects
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(zlib.compress(full_commit))

    return commit_hash  # Return SHA-1 hash of commit


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

    elif command == "cat-tree" and len(sys.argv) == 3:
        tree_hash = sys.argv[2]
        read_tree(tree_hash)
    elif command == "commit-tree" and len(sys.argv) >= 4:
        tree_hash = sys.argv[2]
        message = sys.argv[3]
        
        parent_hash = None
        if len(sys.argv) == 5:  # If a parent commit hash is provided
            parent_hash = sys.argv[4]

        commit_hash = create_commit(tree_hash, parent_hash, message=message)
        print(commit_hash)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)

if __name__ == "__main__":
    main()