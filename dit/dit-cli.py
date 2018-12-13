#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: consider moving dit plumbing to a library which can be used from cli and gui?

"""
Dit commandline client
"""

import sys
import getopt
import textwrap
import datetime
from enum import Enum

from pick import pick

from common import constants
from common.items import DitRelease, DitIssue
from common.errors import DitError, ApplicationError
from ditcontrol import DitControl
from config import ConfigControl
from cli.completer import Completer

class DitCommands:
    """A helper class for parsing command line commands and their parameters"""
    class CommandEnum(Enum):
        ADD = 'add'
        ASSIGN = 'assign'
        CLOSE = 'close'
        COMMENT = 'comment'
        INIT = 'init'
        LIST = 'list'
        LIST_IDS = 'list_ids'
        REMOVE = 'remove'
        SHOW = 'show'
        START = 'start'
        STOP = 'stop'

    def __init__(self):
        self.commands_with_issue_param = [self.CommandEnum.ASSIGN.value,
                                          self.CommandEnum.CLOSE.value,
                                          self.CommandEnum.COMMENT.value,
                                          self.CommandEnum.REMOVE.value,
                                          self.CommandEnum.SHOW.value,
                                          self.CommandEnum.START.value,
                                          self.CommandEnum.STOP.value]
        self.commands_with_no_params = [self.CommandEnum.ADD.value,
                                        self.CommandEnum.INIT.value,
                                        self.CommandEnum.LIST.value,
                                        self.CommandEnum.LIST_IDS.value]
        self.commands_all = self.commands_with_issue_param + self.commands_with_no_params

class Status:
    """A simple class to encapsulate error codes."""
    OK, \
    GETOPT_ERROR, \
    DB_ERROR, \
    INTERNAL_ERROR, \
    INVALID_ARGUMENTS = range(5)

    def __init__(self):
        pass


class DitCli:
    """Simple Dit command line client"""

    def __init__(self):
        self.commands = DitCommands()
        self.command = None
        self.issue_name = None
        self.config = ConfigControl()

    def load_configs(self):
        #try:
        #    self.config.load_configs()
        #except ApplicationError as e:
        #    message = "{}.\n{}\n{}".format(e.error_message,
        #            "Run 'dit init' first to initialize or",
        #            "start Dit GUI in any subdirectory of\nan initialized Dit project.")
        #    print("Dit not initialized")
        #    print(message)
        #    sys.exit(1)

        try:
            self.config.load_configs()
        except ApplicationError as e:
            if e.error_message == "Dit config not found":
                message = "{}\n{}".format(e.error_message,
                        "Use 'dit init' to initialize.")
                print(e.error_message)
            elif e.error_message == "Project file not found":
                print("Fatal configuration error")
                print(e.error_message)
            else:
                print(e.error_message)
            sys.exit(1)

        self.dit = DitControl(self.config)

    def get_user_input(self, prompt):
        value = input(prompt)
        return value

    def get_user_input_multiline(self, prompt):
        """
        Get multiple lines of text input from user.

        Parameters:
        - prompt:   text prompt to show to the user when asking for input

        Returns:
        - a multiline string
        """
        lines = []
        print(prompt)

        while True:
            line = input()
            if line.startswith('/stop'):
                break
            else:
                lines.append(line)

        return '\n'.join(lines)

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

    def init_dit(self):
        """Initialize new Dit project in the current directory"""
        #TODO: move this function to ConfigControl?
        #TODO: improve error handling
        #TODO: check that GUI still works (it may need some changes I have forgotten already)

        default_issue_dir = 'issues'
        name = self.get_user_input("Name: ")
        email = self.get_user_input("Email: ")
        issue_dir = self.get_user_input("Issue directory ({}): ".format(default_issue_dir))
        if not issue_dir:
            issue_dir = default_issue_dir

        # create dit config file (overwrites, but file shouldn't be there)
        dit_yaml = self.config.get_dit_configs()
        dit_yaml.name = name
        dit_yaml.email = email
        dit_yaml.issue_dir = issue_dir
        ret = self.config.ditconfig.write_config_file()
        if ret is False:
            print("Writing Dit config file failed")
            sys.exit(1)

        # create a project file (overwrites existing file, if any)
        project_file = '{}/{}/{}'.format(self.config.ditconfig.project_root,
                                         dit_yaml.issue_dir,
                                         'project.yaml')
        self.config.projectconfig.project_file = project_file
        ret = self.config.projectconfig.write_config_file()
        if ret is False:
            print("Writing project file failed")
            sys.exit(1)

    def add_issue(self):
        """Add new issue to database.
           Read issue input from user, and add new ticket to database."""
        # issue name will be generated, now need to ask for it
        title = self.get_user_input("Title: ")
        issue = DitIssue(title)

        issue_types = self.config.get_valid_issue_types()
        issue_states = self.config.get_valid_issue_states()
        components = self.config.get_valid_components()
        default_creator = self.config.get_default_creator()
        release_names = []
        for release in self.config.get_releases(constants.release_states.UNRELEASED):
            release_names.append(release.title)
        release_names.append("Unassigned")

        issue.description = self.get_user_input_multiline("Description: ")
        issue.issue_type = self.get_user_list_input("Type: ", issue_types)
        issue.component = self.get_user_list_input("Component: ", components)
        issue.status = self.get_user_list_input("Status: ", issue_states)
        issue.disposition = ""
        issue.creator = self.get_user_input("Creator ({}): ".format(default_creator))
        issue.created = datetime.datetime.utcnow()
        issue.release = self.get_user_list_input("Release: ", release_names)
        issue.identifier = None
        issue.references = []

        #TODO: add possibility to add references?
        #      (or just separate functionality to add references?)
        comment = self.get_user_input_multiline("Comment: ")

        if issue.component in [None, '']:
            issue.component = self.config.get_project_name()

        if issue.creator in [None, '']:
            issue.creator = default_creator

        if issue.release == "Unassigned":
            issue.release = None

        self.dit.add_issue(issue, comment)

    def assign_issue(self, issue_name):
        """Assign an existing ticket to a given user"""
        if issue_name is None:
            print("No issue id")
            return

        release_names = []
        for release in self.config.get_releases(constants.release_states.UNRELEASED):
            release_names.append(release.title)

        try:
            issue_id = self.dit.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitError("Unknown issue identifier")
            print("Failed to assign issue: {}".format(issue_name))

            release = self.get_user_list_input("Release: ", release_names)
            comment = self.get_user_input_multiline("Comment: ")
            self.dit.assign_issue(issue_id, release, comment)
        except (DitError, ApplicationError) as e:
            print("Error assigning issue: {}".format(e.error_message))
        pass

    def list_items(self):
        """List titles of all releases and issues."""
        items = self.dit.get_items()
        max_name_width = self.dit.get_issue_name_max_len()

        for item in items:
            icon = ' '
            if isinstance(item, DitRelease):
                # add one empty line as a spacer before releases
                print("")
                icon = ''
            # set icon to the added item
            if isinstance(item, DitIssue):
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
        for item in self.dit.get_items():
            if isinstance(item, DitIssue):
                print(item.identifier)

    def show_issue(self, issue_name):
        """Show content of an issue by identifier."""
        try:
            issue = self.dit.get_issue_content(issue_name)
        except NameError:
            found_id = self.dit.get_issue_identifier(issue_name)
            try:
                issue = self.dit.get_issue_content(found_id)
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

        for entry in issue.log:
            print("------------------------------------------")
            print("{}     {}\n{}".format(entry[0].strftime("%Y-%m-%d %H:%M"), entry[1], entry[2]))
            print("----------")
            if len(entry) == 4 and entry[3] != "":
                dedented_log_message = textwrap.dedent(entry[3]).strip()
                filled_log_message = textwrap.fill(dedented_log_message,
                                                   initial_indent='   ',
                                                   subsequent_indent='   ',
                                                   width=70)
                print("{}".format(filled_log_message))
            print("")
        #TODO: add support for --no-log or --short to print issue info without log

    def start_work(self, issue_name):
        """Start work on an issue."""
        if issue_name is None:
            print("No issue id")
            return

        try:
            issue_id = self.dit.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitError("Unknown issue identifier")
            print("Starting work on issue: {}".format(issue_name))
            comment = self.get_user_input_multiline("Comment: ")
            self.dit.start_work(issue_id, comment)
        except (DitError, ApplicationError) as e:
            print("Error starting work: {}".format(e.error_message))

    def stop_work(self, issue_name):
        """Stop work on an issue."""
        if issue_name is None:
            print("No issue id")
            return

        try:
            issue_id = self.dit.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitError("Unknown issue identifier")
            print("Stopping work on issue: {}".format(issue_name))
            comment = self.get_user_input_multiline("Comment: ")
            self.dit.stop_work(issue_id, comment)
        except (DitError, ApplicationError) as e:
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
            issue_id = self.dit.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitError("Unknown issue identifier")
            dispositions = self.config.get_app_configs().issue_dispositions
            disposition = self.get_user_list_input_index("Disposition: ", dispositions)
            comment = self.get_user_input_multiline("Comment: ")
            self.dit.close_issue(issue_id, disposition, comment)
        except (DitError, ApplicationError) as e:
            print("Error closing issue: {}".format(e.error_message))

    def comment_issue(self, issue_name):
        """
        Comment an issue based on issue identifier or name.

        Parameters:
        - issue_name:   issue to comment
        """
        if issue_name is None:
            print("No issue id")
            return

        print("Commenting issue: {}".format(issue_name))
        try:
            issue_id = self.dit.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitError("Unknown issue identifier")
            comment = self.get_user_input_multiline("Comment: ")
            self.dit.add_comment(issue_id, comment)
        except (DitError, ApplicationError) as e:
            print("Error commenting issue: {}".format(e.error_message))

    def remove_issue(self, issue_name):
        """Remove issue from database based on issue identifier."""
        if issue_name is None:
            print("No issue id")
            return

        print("Removing issue: {}".format(issue_name))
        try:
            issue_id = self.dit.get_issue_identifier(issue_name)
            if issue_id is None:
                raise DitError("Unknown issue identifier")
            self.dit.drop_issue(issue_id)
        except (DitError, ApplicationError) as e:
            print("Error removing issue: {}".format(e.error_message))

    def usage(self):
        """Print help for accepted command line arguments."""
        print("Commands:")
        print(" add       : add new issue")
        print(" assign    : assign issue to a release")
        print(" close     : close an issue")
        print(" comment   : add a comment to an issue")
        print(" list      : list state and titles of all issues in database")
        print(" list_ids  : list identifiers of all issues in database")
        print(" remove    : remove an issue from database")
        print(" show      : show content of one issue")
        print(" start     : start work on an issue")
        print(" stop      : stop work on an issue")

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
            self.usage()
            return Status.INVALID_ARGUMENTS

        # validate command
        if args[0] in self.commands.commands_all:
            self.command = args[0]
            if self.command in self.commands.commands_with_issue_param:
                if len(args) == 1:
                    issue_names = []
                    for item in self.dit.get_items(): #TODO: DitControl is only created after reading configs
                        if isinstance(item, DitIssue):
                            issue_names.append(item.name)
                    self.issue_name = self.get_user_input_complete("Issue name: ", issue_names);
                elif len(args) == 2:
                    self.issue_name = args[1]
                elif len(args) > 2:
                    print("Too many arguments given.")
                    return Status.INVALID_ARGUMENTS
            elif self.command in self.commands.commands_with_no_params:
                self.issue_name = None
            else:
                return Status.INTERNAL_ERROR
        else:
            print("Invalid command issued.")
            return Status.INVALID_ARGUMENTS

        # parsing options and arguments succeeded
        return Status.OK

    def run_command(self):
        """Execute a dit command"""
        if self.command == self.commands.CommandEnum.ADD.value:
            self.add_issue()
        elif self.command == self.commands.CommandEnum.ASSIGN.value:
            self.assign_issue(self.issue_name)
        elif self.command == self.commands.CommandEnum.CLOSE.value:
            self.close_issue(self.issue_name)
        elif self.command == self.commands.CommandEnum.COMMENT.value:
            self.comment_issue(self.issue_name)
        # INIT command is not executed from here
        elif self.command == self.commands.CommandEnum.LIST.value:
            self.list_items()
        elif self.command == self.commands.CommandEnum.LIST_IDS.value:
            self.list_issue_ids()
        elif self.command == self.commands.CommandEnum.REMOVE.value:
            self.remove_issue(self.issue_name)
        elif self.command == self.commands.CommandEnum.SHOW.value:
            self.show_issue(self.issue_name)
        elif self.command == self.commands.CommandEnum.START.value:
            self.start_work(self.issue_name)
        elif self.command == self.commands.CommandEnum.STOP.value:
            self.stop_work(self.issue_name)

        return Status.OK


# main function
def main(argv):
    dit_cli = DitCli()
    err = dit_cli.parse_options(argv)
    if err:
        return err

    if dit_cli.command == dit_cli.commands.CommandEnum.INIT.value:
        return dit_cli.init_dit()

    dit_cli.load_configs()
    return dit_cli.run_command()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
