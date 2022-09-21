#! /usr/bin/env python3

import datetime
import dateutil.relativedelta
import dateutil.parser


def human_time_diff(date_string, max_elements=2):
    """
    Express a time difference in a human understandable form.
    Two timescales are used to explain the difference.
    Rest is just left off as it would provide too much details.

    It's assumed that the times are given in UTC. Any time zone information
    is disregarded.

    Parameters:
    - date_string: ISO date format datetime to count the difference with current time
    - max_elements: how many words to use to explain the time difference

    Returns:
    - string explaining the difference, not exact
    """
    yourdate = dateutil.parser.parse(date_string).replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    timediff = dateutil.relativedelta.relativedelta(now, yourdate) # pylint: disable=W0612
    elements = 0
    explanation = ""
    for unit in ['years', 'months', 'days', 'hours', 'minutes', 'seconds']:
        # pylint: disable=E0602
        execdict = {}
        execdict['timediff'] = timediff
        exec('diff = timediff.' + unit, execdict) # pylint: disable=W0122
        if execdict['diff'] > 0:
            explanation = "{}{} {}".format(explanation, str(execdict['diff']), unit)
            if execdict['diff'] == 1:
                explanation = explanation[:-1]
            elements = elements + 1
            if elements == max_elements:
                break
            explanation += ' '
    return explanation.rstrip()
