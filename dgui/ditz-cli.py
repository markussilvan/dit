#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: consider moving ditz plumbing to a library which can be used from cli and gui?

"""
Ditz commandline client
"""

import sys
import getopt
import textwrap
import datetime

from pick import pick

from common import constants
from common.items import DitzRelease, DitzIssue
from common.errors import DitzError, ApplicationError
from ditzcontrol import DitzControl
from config import ConfigControl
from cli.completer import Completer

class Status:
    """A simple class to encapsulate error codes."""
    OK, \
    GETOPT_ERROR, \
    DB_ERROR, \
    INVALID_ARGUMENTS = range(4)
    def __init__(self):
        pass

class DitzCli:
    """Simple Ditz command line client"""

    def __init__(self):
        self.command = None
        self.issue_name = None

        try:
            self.config = ConfigControl()
        except ApplicationError as e:
            message = "{}.\n{}\n{}".format(e.error_message,
                    "Run 'ditz init' first to initialize or",
                    "start Ditz GUI in any subdirectory of\nan initialized Ditz project.")
            print("Ditz not initialized")
            print(message)
            sys.exit(1)

        try:
            self.config.load_configs()
        except ApplicationError as e:
            if e.error_message == "Ditz config not found":
                message = "{}\n{}".format(e.error_message,
                        "Go to settings to configure before using")
                print("Configuration error")
                print(e.error_message)
            elif e.error_message == "Project file not found":
                print("Fatal configuration error")
                print(e.error_message)
                sys.exit(1)
            else:
                print(e.error_message)
                sys.exit(1)

        self.ditz = DitzControl(self.config)
        self.ditz.reload_cache() #TODO: needed?

    def get_user_input(self, prompt):
        value = input(prompt)
        return value

    def get_user_input_complete(self, prompt, options):
        completer = Completer(options)
        completer.enable()
        return input(prompt)
        #TODO: disable completer?

    def get_user_list_input(self, prompt, options):
        option, _ = pick(options, prompt)
        print(prompt + option)
        return option

    def get_user_list_input_index(self, prompt, options):
        option, index = pick(options, prompt)
        print(prompt + option)
        return index

    def add_issue(self):
        """Add new issue to database.
           Read issue input from user, and add new ticket to database."""
        # issue name will be generated, now need to ask for it
        title = self.get_user_input("Title: ")
        issue = DitzIssue(title)

        issue_types = self.config.get_valid_issue_types()
        issue_states = self.config.get_valid_issue_states() #TODO: should this list include 'closed'
        components = self.config.get_valid_components()
        default_creator = self.config.get_default_creator()
        release_names = []
        for release in self.config.get_releases(constants.release_states.UNRELEASED):
            release_names.append(release.title)
        release_names.append("Unassigned")

        issue.description = self.get_user_input("Description: ")
        issue.issue_type = self.get_user_list_input("Type: ", issue_types)
        issue.component = self.get_user_list_input("Component: ", components)
        issue.status = self.get_user_list_input("Status: ", issue_states)
        issue.disposition = ""
        issue.creator = self.get_user_input("Creator ({}): ".format(default_creator))
        issue.created = datetime.datetime.utcnow()
        issue.release = self.get_user_list_input("Release: ", release_names)
        issue.identifier = None
        issue.references = []

        #TODO: add possibility to add references? (or just separate functionality to add references?)
        comment = "" #TODO: implement "comment dialog" to get a comment

        if issue.component in [None, '']:
            issue.component = self.config.get_project_name()

        if issue.creator in [None, '']:
            issue.creator = default_creator

        if issue.release == "Unassigned":
            issue.release = None

        self.ditz.add_issue(issue, comment)

    def list_items(self):
        """List titles of all releases and issues."""
        items = self.ditz.get_items()
        max_name_width = self.ditz.get_issue_name_max_len()

        for item in items:
            icon = ' '
            if isinstance(item, DitzRelease):
                # add one empty line as a spacer before releases
                print("")
            # set icon to the added item
            if isinstance(item, DitzIssue):
                if item.status == 'unstarted':
                    icon = ' '
                elif item.status == 'in progress':
                    icon = '+'
                elif item.status == 'paused':
                    icon = '-'
                else:
                    print("Unrecognized issue status ({})".format(item.status))
            if item.name is None:
                title = item.title
            else:
                title = "{0}{1:<{2}}{3}".format(icon, item.name, max_name_width + 1, item.title)
            print(title)
        return items

    def list_issue_ids(self):
        """List issue identifiers in database."""
        for item in self.ditz.get_items():
            if isinstance(item, DitzIssue):
                print(item.identifier)

    def show_issue(self, issue_name):
        """Show content of an issue by identifier."""
        try:
            issue = self.ditz.get_issue_content(issue_name)
        except NameError:
            found_id = self.ditz.get_issue_identifier(issue_name)
            try:
                issue = self.ditz.get_issue_content(found_id)
            except NameError:
                issue = None
        if issue is None:
            print("Invalid issue id specified")
            return

        fmt = "{:<15} {}"
        print(fmt.format("Name:", issue.name))
        print(fmt.format("Title:", issue.title))
        dedented_description = textwrap.dedent(issue.description).strip()
        filled_description = textwrap.fill(dedented_description,
                                           initial_indent='',
                                           subsequent_indent=fmt.format("", ""),
                                           width=70)
        #TODO: for description, use multiline imput using readline() instead
        print(fmt.format("Description:", filled_description))
        print(fmt.format("Type:", issue.issue_type))
        print(fmt.format("Component:", issue.component))
        print(fmt.format("Status:", issue.status))
        print(fmt.format("Disposition:", issue.disposition))
        print(fmt.format("Creator:", issue.creator))
        print(fmt.format("Created:", str(issue.created)))
        print(fmt.format("Release:", issue.release))
        print(fmt.format("Identifier:", issue.identifier))

        references = ""
        if issue.references is not None:
            for ref in issue.references:
                references += str(ref) + ' '
            references = textwrap.dedent(references).strip()
            references = textwrap.fill(references,
                                       initial_indent='',
                                       subsequent_indent=fmt.format("", ""),
                                       width=70)
        print(fmt.format("References:", references))
        #TODO: print log in some format
        #TODO: add support for --no-log or --short to print issue info without log

    def start_work(self, issue_name):
        """Start work on an issue."""
        if issue_name is None:
            print("No issue id")
            return

        try:
            issue_id = self.ditz.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitzError("Unknown issue identifier")
            print("Starting work on issue: {}".format(issue_name))
            comment = '' #TODO: ask for a comment with multiline user input
            self.ditz.start_work(issue_id, comment)
        except (DitzError, ApplicationError) as e:
            print("Error starting work: {}".format(e.error_message))

    def stop_work(self, issue_name):
        """Stop work on an issue."""
        if issue_name is None:
            print("No issue id")
            return

        try:
            issue_id = self.ditz.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitzError("Unknown issue identifier")
            print("Stopping work on issue: {}".format(issue_name))
            comment = '' #TODO: ask for a comment with multiline user input
            self.ditz.stop_work(issue_id, comment)
        except (DitzError, ApplicationError) as e:
            print("Error stopping work: {}".format(e.error_message))

    def close_issue(self, issue_name):
        """
        Close an issue based on issue identifier or name.

        Even an issue that is already closed, can be closed again.
        Old disposition is overwritten and a new comment is added.
        """
        if issue_name is None:
            print("No issue id")
            return

        print("Closing issue: {}".format(issue_name))
        try:
            issue_id = self.ditz.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitzError("Unknown issue identifier")
            dispositions = self.config.get_app_configs().issue_dispositions
            disposition = self.get_user_list_input_index("Disposition: ", dispositions)
            self.ditz.close_issue(issue_id, disposition, comment="")
        except (DitzError, ApplicationError) as e:
            print("Error closing issue: {}".format(e.error_message))

    def remove_issue(self, issue_name):
        """Remove issue from database based on issue identifier."""
        if issue_name is None:
            print("No issue id")
            return

        print("Removing issue: {}".format(issue_name))
        try:
            issue_id = self.ditz.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitzError("Unknown issue identifier")
            self.ditz.drop_issue(issue_id)
        except (DitzError, ApplicationError) as e:
            print("Error removing issue: {}".format(e.error_message))

    def usage(self):
        """Print help for accepted command line arguments."""
        print("Commands:")
        print(" 'add'      : add new issue")
        print(" 'close'    : close an issue")
        print(" 'list'     : list state and titles of all issues in database")
        print(" 'list_ids' : list identifiers of all issues in database")
        print(" 'remove'   : remove an issue from database")
        print(" 'show'     : show content of one issue")
        print(" 'start'    : start work on an issue")

    def parse_options(self, argv):
        """Parse command line options."""
        # remove existing values
        shortOpts = "h"
        longOpts = ["help"]
        try:
            opts, args = getopt.getopt(argv, shortOpts, longOpts)
        except getopt.error as msg:
            print(msg)
            self.usage()
            return Status.GETOPT_ERROR

        # process options
        for opt, _ in opts:
            if opt in ("-h", "--help"):
                self.usage()
                return 0

        # process command line arguments here
        if not args:
            print("No command issued.")
            return Status.INVALID_ARGUMENTS

        # validate command
        if args[0] in ['add', 'close', 'list', 'list_ids', 'remove', 'show', 'start', 'stop']:
            self.command = args[0]
            if self.command in ['close', 'remove', 'show', 'start', 'stop']:
                if len(args) == 1:
                    issue_names = []
                    for item in self.ditz.get_items():
                        if isinstance(item, DitzIssue):
                            issue_names.append(item.name)
                    self.issue_name = self.get_user_input_complete("Issue name: ", issue_names);
                elif len(args) == 2:
                    self.issue_name = args[1]
                elif len(args) > 2:
                    print("Too many arguments given.")
                    return Status.INVALID_ARGUMENTS
            else:
                self.issue_name = None
        else:
            print("Invalid command issued.")
            return Status.INVALID_ARGUMENTS

        # parsing options and arguments succeeded
        return Status.OK


# main function
def main(argv):
    ditz_cli = DitzCli()
    err = ditz_cli.parse_options(argv)
    if err:
        return err
    if ditz_cli.command == 'add':
        ditz_cli.add_issue()
    elif ditz_cli.command == 'close':
        ditz_cli.close_issue(ditz_cli.issue_name)
    elif ditz_cli.command == 'list':
        ditz_cli.list_items()
    elif ditz_cli.command == 'list_ids':
        ditz_cli.list_issue_ids()
    elif ditz_cli.command == 'remove':
        ditz_cli.remove_issue(ditz_cli.issue_name)
    elif ditz_cli.command == 'show':
        ditz_cli.show_issue(ditz_cli.issue_name)
    elif ditz_cli.command == 'start':
        ditz_cli.start_work(ditz_cli.issue_name)
    elif ditz_cli.command == 'stop':
        ditz_cli.stop_work(ditz_cli.issue_name)
    return Status.OK

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
