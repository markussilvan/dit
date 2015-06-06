#! /bin/sh
# Run all unit tests for the code and generate XML reports
#

report_dir="$PWD/../reports/"
test_files="\
    test_archivecontrol.py \
    test_issuemodel.py \
    test_itemcache.py \
    test_ditzcontrol.py \
    test_config.py"

[ ! -e "$report_dir" ] && mkdir -p $report_dir

cd ../src/tests/ || exit 1

for testsuite in $test_files; do
    ./$testsuite --xml $report_dir
    if [ $? -ne 0 ]; then
        exit 1
    fi
done

