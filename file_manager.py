import sys
import os
import shutil


this = sys.modules[__name__]
this.fs_dir = None


def init(purge, fs_dir="fs"):
    this.fs_dir = fs_dir
    if os.path.exists(this.fs_dir):
        if purge:
            purge_filesystem()
            os.makedirs(this.fs_dir)
    else:
        os.makedirs(this.fs_dir)


def purge_filesystem():
    shutil.rmtree(this.fs_dir)


def create_file(filename):
    filepath = os.path.join(this.fs_dir, filename)

    # If the file exists, skip creation
    if os.path.exists(filepath):
        return

    # Create the file, don't write anything yet
    with open(filepath, "w") as fp:
        pass


def delete_file(filename):
    filepath = os.path.join(this.fs_dir, filename)

    # If the file doesn't exist, skip deletion
    if not os.path.exists(filepath):
        return

    # Delete the file
    os.unlink(filepath)


def read_file(filename):
    filepath = os.path.join(this.fs_dir, filename)

    # If the file doesn't exist, skip deletion
    if not os.path.exists(filepath):
        return

    # Create the file, don't write anything yet
    with open(filepath, "r") as fp:
        content = fp.read()

    return content


def write_file(filename, content):
    filepath = os.path.join(this.fs_dir, filename)

    # If the file doesn't exist, skip deletion
    if not os.path.exists(filepath):
        return

    # Create the file, don't write anything yet
    with open(filepath, "w") as fp:
        fp.write(content)


def append_file(filename, content):
    filepath = os.path.join(this.fs_dir, filename)

    # If the file doesn't exist, skip deletion
    if not os.path.exists(filepath):
        return

    # Create the file, don't write anything yet
    with open(filepath, "a") as fp:
        fp.write(content)
