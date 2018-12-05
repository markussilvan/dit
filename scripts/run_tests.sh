#! /bin/sh
# Run all unit tests for the code and generate XML reports
#

report_dir="$PWD/../reports/"
test_dir="$PWD/../dit/tests/"

[ ! -e "$report_dir" ] && mkdir -p $report_dir

# remove old test reports
cd $report_dir || exit 1
rm TEST-*.xml

# run tests
cd $test_dir || exit 1

for testsuite in test_*.py; do
    ./$testsuite --xml $report_dir
    if [ $? -ne 0 ]; then
        exit 1
    fi
done

