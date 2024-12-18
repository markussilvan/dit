# Dit

Dit is a simple and light-weight distributed issue tracker designed
to work with distributed version control systems like Git.
Dit maintains an issue database directory on disk, with
files written in a line-based and human-editable format. This
directory can be kept under version control, alongside project code,
or in a separate (sub)repository.

Console based *dit-cli* and graphical *dit-gui* clients are developed using
Python and PyQt. The GUI provides fast and easy access to dit issues without need
to hassle with the command line tool. It has all the same features of the command
line client.

![dit-gui screenshot](dit-gui-screenshot.jpg)

Idea of Dit is based on *Ditz*. Originally Dit was just a GUI front end
for it, but later reimplemented all the functionality. Since, Dit
has become incompatible with the original Ditz implementation.


## Tools

Of course, git is used as version control system and tickets, bugs
and new features are tracked using Dit. Now the development has progressed
enough, so that the program itself can be used as the issue tracker.

### Python Virtual Environment

First, create the virtual environment. It can be done by running
`python3 -m venv dit-venv` in the project directory.

Then, enable the environment using `source dit-venv/bin/activate`.

Install the dependencies in the virtual environment using
`pip install -r requirements.txt`.

Now it should be possible to start the applications.

Exit the virtual environment using `deactivate`.

**NOTE: The path to the virtual environment is hardcoded in
the applications shebang. Change it locally if needed.**

### List of Used Tools

 - Python 3.4
 - PyQt 5.x
 - python-unittest (aka PyUnit)
 - python-yaml
 - python-dateutil
 - python-mock
 - PyLint
 - git

## Enabling Menu Icons On Ubuntu

By default menu icons are disabled on Ubuntu.
To enable, run:
    `gconftool-2 --type Boolean --set /desktop/gnome/interface/menus_have_icons True`


## Configuration File

The GUI application uses a `.dit-gui-config` file as it's configuration file.
The file should be located at the same path as `.dit-config`, which is created
by `dit init`.

An example `.dit-config` configuration file.

```
    !dit.random.org,2008-03-06/config
    email: john.doe@gmail.com
    issue_dir: issues
    name: "John Doe"
```

Here is an example `.dit-gui-config` configuration file.

```
    !dit.random.org,2008-03-06/guiconfig
    default_issue_type: task
    remember_window_size: false
    window_size:
    - 1222
    - 841
```


## Installation

  - Install python 3.x (preferably 32-bit)
  - Install PyQt 5.x (preferably 32-bit) (required for dit-gui only)
  - Install library dependencies `pip3 install -r requirements.txt`

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

## Integration tests

Integration tests run some simple tests using the Dit CLI interface.
These tests should be run inside the Docker image with known set
of test data.

Run integration tests with `run_tests.sh`.

## Docker testing image

  1. Docker image can be built from the _Dockerfile_ with simply
     `docker build --network host -t "dit:latest" .` or
     use a script to do the same `./scripts/docker_build.sh`.
  2. List all Docker containers with `docker ps --all`.
  3. List all Docker images with `docker images`.
  4. Create and start the container with the script
     `./scripts/docker_run.sh` to use the run command with correct parameters.
