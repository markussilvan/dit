#! /bin/sh
# Run pylint for all python code in ditz-gui
#

# find report, source and pylint config dirs
if [ "`basename $PWD`" = "scripts" ]; then
    REPORT_DIR="../reports"
    SOURCE_DIR="../src/"
    PYLINT_CONFIG="pylint.cfg"
elif [ "`basename $PWD`" = "ditz-gui" ]; then
    REPORT_DIR="reports"
    SOURCE_DIR="src/"
    PYLINT_CONFIG="scripts/pylint.cfg"
fi

# create report dir if it doesn't exist
[ ! -e $REPORT_DIR ] && mkdir $REPORT_DIR

# find files to check with pylint
FILES="$(find $SOURCE_DIR -name "*.py" | grep -v attic)"

# run pylint and generate reports
#pylint --msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg} 'to --msg-template=%s' % (self.name, self.line_format) --rcfile pylint.cfg $FILES >$REPORT_DIR/pylint.log
pylint -f parseable --rcfile $PYLINT_CONFIG $FILES >$REPORT_DIR/pylint.log
exit 0
