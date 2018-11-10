#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: consider moving ditz plumbing to a library which can be used from cli and gui?

"""
Ditz commandline client
"""

import sys
import getopt
import textwrap

from common.items import DitzRelease, DitzIssue
from ditzcontrol import DitzControl
from config import ConfigControl

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
        self.issue_id = None

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

    def get_user_input(self, prompt):
        value = input(prompt)
        return value

    def add_issue(self):
        """Add new issue to database.
           Read issue input from user, and add new ticket to database."""
        title = self.get_user_input("Title: ")
        description = self.get_user_input("Description: ")
        #TODO: adding (copy from ditz-gui)
        #       - create an issue based on user input
        #       - give issue to ditzcontrol to insert to "database"
        #issue = Issue(title, description, datetime.utcnow(), None)
        #collection = self.db.issues
        #return collection.insert(issue.data)

    def list_items(self):
        """List titles of all releases and issues."""
        print("All issues:")
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

    def show_issue(self, issue_id):
        """Show content of an issue by identifier."""
        try:
            issue = self.ditz.get_issue_content(issue_id)
        except NameError:
            found_id = self.ditz.get_issue_identifier(issue_id)
            try:
                issue = self.ditz.get_issue_content(found_id)
            except NameError:
                print("Invalid issue id specified")
                return
        fmt = "{:<15} {}"
        print(fmt.format("Name:", issue.name))
        print(fmt.format("Title:", issue.title))
        dedented_description = textwrap.dedent(issue.description).strip()
        filled_description = textwrap.fill(dedented_description,
                                           initial_indent='',
                                           subsequent_indent=fmt.format("",""),
                                           width=70)
        print(fmt.format("Description:", filled_description))
        print(fmt.format("Type:", issue.issue_type))
        print(fmt.format("Component:", issue.component))
        print(fmt.format("Status:", issue.status))
        print(fmt.format("Disposition:", issue.disposition))
        print(fmt.format("Creator:", issue.creator))
        print(fmt.format("Created:", str(issue.created)))
        print(fmt.format("Release:", issue.release))
        print(fmt.format("Identifier:", issue.identifier))
        #TODO: add other fields, and use format specifiers instead of hardcoded spaces to align
        ###if references is not None:
        ###    self.references = references
        ###else:
        ###    self.references = []
        ###self.log = log

    def remove_issue(self):
        """Remove issue from database based on issue identifier."""
        issues = self.list_items()
        index = int(self.get_user_input("Issue to remove: "))
        #TODO self.db.issues.remove({'_id': issues[index]})

    def usage(self):
        """Print help for accepted command line arguments."""
        print("Commands:")
        print(" 'add'      : add new issue")
        print(" 'list'     : list titles of all issues in database")
        print(" 'list_ids' : list identifiers of all issues in database")
        print(" 'show'     : show content of one selected issue")
        print(" 'remove'   : remove an issue from database")

    def parse_options(self, argv):
        """Parse command line options."""
        # remove existing values
        shortOpts = "h"
        longOpts = ["help"]
        try:
            opts, args = getopt.getopt(argv, shortOpts, longOpts)
        except getopt.error as msg:
            print >> self.output, msg #TODO: is this ok in python3?
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
        if args[0] in ['add', 'list', 'list_ids', 'show', 'remove']:
            self.command = args[0]
            if self.command == 'show':
                if len(args) != 2:
                    print("No issue to show specified.")
                    return Status.INVALID_ARGUMENTS
                self.issue_id = args[1]
            else:
                self.issue_id = None
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
    elif ditz_cli.command == 'list':
        ditz_cli.list_items()
    elif ditz_cli.command == 'list_ids':
        ditz_cli.list_issue_ids()
    elif ditz_cli.command == 'show':
        ditz_cli.show_issue(ditz_cli.issue_id)
    elif ditz_cli.command == 'remove':
        ditz_cli.remove_issue()
    return Status.OK

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
