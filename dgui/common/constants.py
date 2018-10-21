#! /usr/bin/env python
#
# Constants used around the project
#


class Constants(object):
    """
    Create objects with constant (read-only) attributes.
    """
    def __init__(self, *args, **kwargs):
        """ Initialize """
        self._d = dict(*args, **kwargs)

    def __iter__(self):
        """ Iteration """
        return iter(self._d)

    def __len__(self):
        """ Length """
        return len(self._d)

    def __getattr__(self, name):
        """
        Get attribute.

        This is only called when named constant of given
        name is not found. It is then searched from
        the internal dictionary.
        """
        return self._d[name]

    def __setattr__(self, name, value):
        """
        Set attribute.

        Allows setting attibutes with a name starting with
        an underscore. This is required to initialize '_d'.
        """
        if name[0] == '_':
            super(Constants, self).__setattr__(name, value)
        else:
            raise ValueError("__setattr called for a constant", self)


releases = Constants(UNASSIGNED='Unassigned')
release_states = Constants(
        UNRELEASED='unreleased',
        RELEASED='released',
        )
