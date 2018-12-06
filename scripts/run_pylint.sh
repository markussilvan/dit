#! /bin/sh
# Run pylint for all python code in dit-gui
#

# find source dir
if [ "`basename $PWD`" = "scripts" ]; then
    cd ../dit
    if [ $? -ne 0 ]; then
        echo "Can't find source directory"
        exit 1
    fi
elif [ "`basename $PWD`" = "dit" ]; then
    # ok, already there
    :
else
    # assume "dit-gui"
    cd dit
    if [ $? -ne 0 ]; then
        echo "Can't find source directory"
        exit 1
    fi
fi

# set locations for report and source dirs and pylint config file
REPORT_DIR="../reports"
SOURCE_DIR="."
PYLINT_CONFIG="../scripts/pylint.cfg"

# create report dir if it doesn't exist
[ ! -e $REPORT_DIR ] && mkdir $REPORT_DIR

# find files to check with pylint
FILES="$(find $SOURCE_DIR -name "*.py" | grep -v attic)"

# run pylint and generate reports
#pylint --msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg} 'to --msg-template=%s' % (self.name, self.line_format) --rcfile pylint.cfg $FILES >$REPORT_DIR/pylint.log
pylint -f parseable --rcfile $PYLINT_CONFIG $FILES >$REPORT_DIR/pylint.log
exit 0
