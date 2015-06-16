#! /bin/sh
# Run all unit tests for the code and generate XML reports
#

report_dir="$PWD/../reports/"

[ ! -e "$report_dir" ] && mkdir -p $report_dir

cd ../src/tests/ || exit 1

# remove old test reports
rm TEST-*.xml

# run tests
for testsuite in test_*.py; do
    ./$testsuite --xml $report_dir
    if [ $? -ne 0 ]; then
        exit 1
    fi
done

