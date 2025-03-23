# Simple Git - A Minimal Git Implementation

## Overview
This project is a minimal Git-like version control system implemented in Python. It provides basic functionalities for working with Git objects, such as blobs and trees. This implementation helps understand how Git internally stores and retrieves data. Inspired by codecrafters build-your-own-git

## Features
- **Create Blob**: Stores file contents as Git blob objects.
- **Read Blob**: Retrieves and prints blob contents from `.git/objects/`.
- **Read Tree**: Parses tree objects to display file structure.
- **Custom Object Storage**: Mimics Git's object storage structure.

## Installation
Ensure you have Python 3 installed on your system.

Clone this repository:
```sh
$ git clone <your-repo-url>
$ cd <your-repo-folder>
```

## Usage
### 1. Creating a Blob
You can create a blob object by running:
```python
from git_clone import create_blob

content = b"Hello, Git!"
blob_hash = create_blob(content)
print("Blob Hash:", blob_hash)
```
This will store the blob inside `.git/objects/` using Git's SHA-1 hashing mechanism.

### 2. Reading a Blob
To read and display a stored blob:
```python
from git_clone import read_blob

read_blob(blob_hash)  # Use the hash generated from create_blob()
```
This will output the content of the stored blob.

### 3. Reading a Tree
If you have a Git tree object stored, you can read it using:
```python
from git_clone import read_tree

read_tree(tree_hash)  # Replace with actual tree hash
```
This will display the structure of files and subdirectories stored in the tree object.

## How It Works
1. The `create_blob` function creates a Git blob by:
   - Adding a Git header (`blob <size>\0`)
   - Compressing and storing the content in `.git/objects/` using SHA-1.
2. The `read_blob` function retrieves and decompresses the stored blob.
3. The `read_tree` function reads and parses a Git tree object.

## Dependencies
This project relies on Python's built-in libraries:
- `os` (File and directory management)
- `sys` (Error handling)
- `zlib` (Compression)
- `hashlib` (SHA-1 hashing)
- `time` (Timestamp handling)

