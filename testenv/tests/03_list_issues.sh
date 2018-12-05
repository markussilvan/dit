#! /bin/bash
# Test Dit issue listing

source testlib.inc

output=`dit list`
issue=`echo "$output" | grep "Test item title"`

assert "`echo "$output" | wc -l` -gt 0" "No output"
assert "! \"`echo "$output" | grep Unassigned`\" = \"\"" "Unassigned section not found"
assert '"'$issue'" = ""' 'Added issue ("dit-gui-1") not found'

expect <<EOF
spawn dit list
expect "Unassigned\r dit-gui-1 Test item title\r"
EOF
