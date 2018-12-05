#! /bin/sh
# Testing library

assert_return_value()
{
	local RETURNCODE=$?
	local MESSAGE=""
	local EXPECTED=0
	local EXITCODE=1

	[ $# -gt 0 ] && MESSAGE=$1 && shift
	[ $# -gt 0 ] && EXPECTED=$1 && shift
	[ $# -gt 0 ] && EXITCODE=$1 && shift

	if [ $RETURNCODE -ne $EXPECTED ]; then
		if [ ! "$MESSAGE" = "" ]; then
			printf "$MESSAGE\n"
		fi
		exit $EXITCODE
	fi
}

assert()
{
	local COMPARISON=""
	local MESSAGE=""
	local EXITCODE=1

	[ $# -gt 0 ] && COMPARISON=$1 && shift
	[ $# -gt 0 ] && MESSAGE=$1 && shift
	[ $# -gt 0 ] && EXITCODE=$1 && shift

	if [ ! $COMPARISON ]; then
		if [ ! "$MESSAGE" = "" ]; then
			printf "$MESSAGE\n"
		fi
		exit $EXITCODE
	fi
}
