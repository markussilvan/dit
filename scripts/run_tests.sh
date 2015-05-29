#! /bin/sh
# Run all unit tests for the code and generate XML reports
#

echo "Not implemented"

report_dir="$PWD/../reports/"


test_files="\
    ../src/tests/test_itemcache.py \
    ../src/tests/test_ditzcontrol.py \
    ../src/tests/test_config.py"

[ ! -e "$report_dir" ] && mkdir -p $report_dir

for testsuite in $test_files; do
    ./$testsuite --xml $report_dir
    if [ $? -ne 0 ]; then
        exit 1
    fi
done

