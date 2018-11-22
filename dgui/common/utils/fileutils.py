#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
General Python file utilities
"""

import os
import stat
import shutil


def find_file_along_path(filename, path="."):
    """
    Find a file from the given path.
    File is searched from every directory towards the root
    until it is found or a device boundary is reached.

    os.stat doesn't work on Windows before Python 3.4.
    Nevertheless, a root of a drive is reached at some point
    and the loop will end.

    Parameters:
    - filename: file to search
    - path: (optional) path to start the search from.
            Defaults to current directory.

    Returns:
    - path to the file not including the file name

    Raises:
    - Exception: root or device boundary reached before file is found
    """
    path = os.path.realpath(path)
    s = os.stat(path)[stat.ST_DEV]
    ps = s

    while path != '/' and path[1:] != ":\\":
        parent = os.path.dirname(path)
        ps = os.stat(parent)[stat.ST_DEV]

        # check if this directory contains dit config
        if os.path.isfile("{}/{}".format(path, filename)):
            return str(path)

        if ps == s:
            path = parent
        else:
            # not the same device anymore
            raise Exception("Can't find file on this device")


    # root dir
    if os.path.isfile("{}/{}".format(path, filename)):
        return str(path)

    raise Exception("Can't find the file")

def move_files(files, path):
    """
    Move a list of files to a given path.

    If the destination path doesn't exist, it is
    created automatically.
    Works over file system boundaries.

    Parameters:
    - files: list of files to move
    - path: destination path

    Raises:
    - TypeError, OSError, IOError
    """
    if files == [] or path == '':
        raise TypeError("Invalid parameters")
    if path in files:
        raise IOError("Destination one of the source files")

    # create destination directory if it doesn't exist
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        raise

    # move files
    try:
        for f in files:
            shutil.move(f, path)
    except (IOError, shutil.Error):
        # undo stuff that was already done?
        raise
