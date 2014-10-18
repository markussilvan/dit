#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
General Python file utilities
"""

import os
import sys
import stat

def find_file_along_path(filename, path="."):
    """
    Find a file from the given path.
    File is searched from every directory towards the root
    until it is found or a device boundary is reached.

    Parameters:
    - filename: file to search
    - path: (optional) path to start the search from.
            Defaults to current directory.

    Returns:
    - path to the file not including the file name

    Throws:
    - Exception: root or device boundary reached before file is found
    """
    path = os.path.realpath(path)
    s = os.stat(path)[stat.ST_DEV]
    ps = s

    while path != '/':
        parent = os.path.dirname(path)
        ps = os.stat(parent)[stat.ST_DEV]

        # check if this directory contains ditz config
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

