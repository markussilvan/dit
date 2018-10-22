# Ditz-gui

Graphical *ditz* client developed using Python and PyQt. Provides
fast and easy access to ditz issues without need to hassle with the
command line tool. Implements all features as the original command
line ditz.

Ditz is a simple, light-weight distributed issue tracker designed
to work with distributed version control systems like git, darcs,
Mercurial, and Bazaar. It can also be used with centralized systems
like SVN. Ditz maintains an issue database directory on disk, with
files written in a line-based and human-editable format. This
directory can be kept under version control, alongside project code.


## Tools

Jenkins is used as a continuous integration platform to build
release packages, run PyUnit unit tests and Pylint static code analysis.
And of course, git is used as version control system and tickets, bugs
and new features are tracked using Ditz. Now the development has progressed
enough, so that the program itself can be used as the issue tracker.


### List of Tools

 - Python 3.3
 - PyQt 4.7
 - python-unittest (aka PyUnit)
 - python-yaml
 - python-dateutil
 - python-mock
 - PyLint
 - Jenkins
 - git
 - Ditz 0.5 (not required)


## Enabling Menu Icons On Ubuntu

By default menu icons are disabled on Ubuntu.
To enable, run:
    gconftool-2 --type Boolean --set /desktop/gnome/interface/menus_have_icons True


## Configuration File

Application uses a .ditz-gui-config file as it's configuration file.
The file should be located at the same path as .ditz-config.
Here is an example configuration file.

    !ditz.rubyforge.org,2008-03-06/guiconfig
    default_issue_type: task
    remember_window_size: false
    window_size:
    - 1222
    - 841


## Installation on Windows

  - Install python 2.7 (preferably 32-bit)
  - Install PyQt 4.7 (preferably 32-bit)
  - Run `pip install python-dateutil`
  - Run `pip install pyyaml`
  - Run `pip install mock`


## Unit Tests

Test code is located in `dgui/tests/`. Each test set can be run
separately or one script can be used to run all tests. This
script can be found in `scripts/` directory.

Unit tests use PyUnit framework and a mostly simple cases to
try is some feature runs without crashing. If possible, end
result is verified from files or data structures available.

A known, constant set of files is used to provide data to the
components being tested. Verifying known data values is then
hardcoded in the testing scripts.

