#! /usr/bin/env python3

import re
import readline

class Completer():
    """Dit CLI readline input completer"""

    def __init__(self, options):
        """Initialize user input completer"""
        self.options = options
        self.spaces_regexp = re.compile(r'.*\s+$', re.M)

    def enable(self):
        """Enable this completer"""
        # we want to treat '/' as part of a word, so override the delimiters
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.complete)

    def complete(self, _text, state):
        """Generic completion entry point for readline."""
        linebuffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()

        # show all commands
        if not line:
            return [c + ' ' for c in self.options][state]

        # account for last argument ending in a space
        if self.spaces_regexp.match(linebuffer):
            line.append('')

        # resolve command to the implementation function
        user_input = line[0].strip()
        if user_input in self.options:
            impl = getattr(self, 'complete_{}'.format(user_input))
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [user_input + ' '][state]

        results = [c + ' ' for c in self.options if c.startswith(user_input)] + [None]

        return results[state]
