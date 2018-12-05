#! /bin/bash
# Test Dit issue listing

source testlib.inc

expect <<EOF
set timeout 10

spawn dit add

expect "Title:*"
send -- "Test item title\r"

expect "Description:*"
send -- "Description of the test item.\r"
send -- "That spans two lines.\r"
send -- "/stop\r"

expect "Type:*"
send -- "\r"

send -- "\r"

send -- "\r"

expect "Creator:*"
send -- "Terry Tester \<terry@tester.com\>\r"

send -- "\r"

send -- "No comment.\r"
send -- "/stop\r"

expect eof
EOF

assert_return_value "Dit add returned an error"
assert "`ls bugs/issue-* | wc -l` -eq 1" "Issue file was not created"
