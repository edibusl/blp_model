import sys
import os
import shutil


this = sys.modules[__name__]
this.fs_dir = None


def init(purge, fs_dir="fs"):
    this.fs_dir = fs_dir
    if os.path.exists(this.fs_dir):
        if purge:
            shutil.rmtree(this.fs_dir)
            os.makedirs(this.fs_dir)
    else:
        os.makedirs(this.fs_dir)


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
