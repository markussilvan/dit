# Dit

Dit is a simple and light-weight distributed issue tracker designed
to work with distributed version control systems like git and Mercurial.
Dit maintains an issue database directory on disk, with
files written in a line-based and human-editable format. This
directory can be kept under version control, alongside project code.

Graphical *dit* client is developed using Python and PyQt. Provides
fast and easy access to dit issues without need to hassle with the
command line tool. Implements all features of the command line client.

Idea of Dit is based on *Ditz*. Originally Dit was just a GUI front
for it, but later reimplemented all the same features. Since, Dit
has become incompatible with the original Ditz implementation.

## Tools

Jenkins is used as a continuous integration platform to build
release packages, run PyUnit unit tests and Pylint static code analysis.
And of course, git is used as version control system and tickets, bugs
and new features are tracked using Ditz. Now the development has progressed
enough, so that the program itself can be used as the issue tracker.


### List of Tools

 - Python 3.4
 - PyQt 5.x
 - python-unittest (aka PyUnit)
 - python-yaml
 - python-dateutil
 - python-mock
 - PyLint
 - Jenkins
 - git


## Enabling Menu Icons On Ubuntu

By default menu icons are disabled on Ubuntu.
To enable, run:
    gconftool-2 --type Boolean --set /desktop/gnome/interface/menus_have_icons True


## Configuration File

Application uses a .dit-gui-config file as it's configuration file.
The file should be located at the same path as .dit-config.
Here is an example configuration file.

    !dit.random.org,2008-03-06/guiconfig
    default_issue_type: task
    remember_window_size: false
    window_size:
    - 1222
    - 841


## Installation on Windows

  - Install python 3.4 (preferably 32-bit)
  - Install PyQt 5.x (preferably 32-bit)
  - Run `pip install python-dateutil`
  - Run `pip install pyyaml`
  - Run `pip install mock`


## Unit Tests

Test code is located in `dit/tests/`. Each test set can be run
separately or one script can be used to run all tests. This
script can be found in `scripts/` directory.

Unit tests use PyUnit framework and a mostly simple cases to
try is some feature runs without crashing. If possible, end
result is verified from files or data structures available.

A known, constant set of files is used to provide data to the
components being tested. Verifying known data values is then
hardcoded in the testing scripts.

## Docker image

  1. Docker image can be built from the _Dockerfile_ with simply
     `docker build -t "dit:dockerfile" .`
  2. List all Docker containers with `docker ps --all`.
  3. List all Docker images with `docker images`.
  4. Create container from the docker image with
     `docker create -it dit:dockerfile`.
