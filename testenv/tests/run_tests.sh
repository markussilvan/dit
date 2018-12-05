#! /bin/bash
# Run all tests

source testlib.inc

for testfile in ./[0-9]*.sh; do
	name=`basename ${testfile%.*}`
	echo -n Running tests from $name...
	output=`$testfile`
	outval=$?
	err=`printf "fail\n\r$output"`
	assert "$outval = 0" "$err"
	echo pass
done

echo All tests passed
