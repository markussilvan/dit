#! /usr/bin/env python
import datetime
import dateutil.relativedelta
import dateutil.parser


def human_time_diff(date, max_elements=2):
    """
    Express a time difference in a human understandable form.
    Two timescales are used to explain the difference.
    Rest is just left off as it would provide too much details.

    Parameters:
    - date: datetime to count the difference with current time
    - max_elements: how many words to use to explain the time difference

    Returns:
    - string explaining the difference, not exact
    """
    yourdate = dateutil.parser.parse(date)
    now = datetime.datetime.now()
    timediff = dateutil.relativedelta.relativedelta(now, yourdate)
    elements = 0
    explanation = ""
    for unit in ['years', 'months', 'days', 'hours', 'minutes', 'seconds']:
        exec('diff = timediff.' + unit)
        if diff > 0:
            explanation = "{}{} {}".format(explanation, str(diff), unit)
            if diff == 1:
                explanation = explanation[:-1]
            elements = elements + 1
            if elements == max_elements:
                break
            explanation += ' '
    return explanation.rstrip()

