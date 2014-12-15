#! /usr/bin/env python
# -*- coding: utf-8 -*-

from config import ConfigControl

config = ConfigControl()
config.read_config_file()

print "Project name: " + str(config.get_project_name())
print "Unreleased releases: " + str(config.get_unreleased_releases())
print "All releases: " + str(config.get_releases())

