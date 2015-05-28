# Ditz-gui

Ditz frontend developed using Python and PyQt. Provides fast and
easy access to ditz issues without need to hassle with the
command line tool.

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
are tracked using Ditz. As the development progresses the program
itself can be used as the issue tracker.


### List of Tools

 - Python 2.7
 - PyQt 4.7
 - python-unittest (aka PyUnit)
 - python-yaml
 - python-dateutil
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


