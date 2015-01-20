#! /usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import datetime


class YamlConfig(object):
    """
    YAML library configuration/extension
    """
    def __init__(self):
        """
        Initialize YamlConfig instance
        """
        if type(self) == YamlConfig:
            raise Exception("YamlConfig should not be instantiated")

    @staticmethod
    def add_representers():
        """
        Add new representers for PyYaml library
        """
        yaml.add_representer(str, YamlConfig.str_representer)
        yaml.add_representer(datetime.datetime, YamlConfig.datetime_representer)

    @staticmethod
    def str_representer(dumper, data):
        tag = None
        if '\n' in data:
            style = '|'
        else: style = None
        try:
            data = unicode(data, 'ascii')
            tag = u'tag:yaml.org,2002:str'
        except UnicodeDecodeError:
            try:
                data = unicode(data, 'utf-8')
                tag = u'tag:yaml.org,2002:str'
            except UnicodeDecodeError:
                data = data.encode('base64')
                tag = u'tag:yaml.org,2002:binary'
                style = '|'
        return dumper.represent_scalar(tag, data, style=style)

    @staticmethod
    def datetime_representer(dumper, data):
        value = unicode(data.isoformat(' ') + ' Z')
        return dumper.represent_scalar(u'tag:yaml.org,2002:timestamp', value)



